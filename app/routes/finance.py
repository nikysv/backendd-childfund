from flask import Blueprint, jsonify, request
from app.db import db
from app.models import Transaction
from datetime import datetime
import pytz

finance_bp = Blueprint('finance', __name__, url_prefix='/api/finance')
bolivia_tz = pytz.timezone('America/La_Paz')

@finance_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """
    Obtener transacciones de un usuario
    Query params: user_id (requerido), type (opcional: ingreso/egreso), start_date, end_date
    """
    user_id = request.args.get('user_id')
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not user_id:
        return jsonify({'error': 'user_id es requerido'}), 400
    
    try:
        query = Transaction.query.filter_by(user_id=user_id)
        
        # Filtrar por tipo si se especifica
        if transaction_type and transaction_type in ['ingreso', 'egreso']:
            query = query.filter_by(type=transaction_type)
        
        # Filtrar por rango de fechas
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.date >= start)
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.date <= end)
        
        transactions = query.order_by(Transaction.date.desc()).all()
        transactions_data = [t.to_dict() for t in transactions]
        
        # Calcular totales
        total_ingresos = sum(t.amount for t in transactions if t.type == 'ingreso')
        total_egresos = sum(t.amount for t in transactions if t.type == 'egreso')
        balance = total_ingresos - total_egresos
        
        return jsonify({
            'success': True,
            'data': transactions_data,
            'count': len(transactions_data),
            'summary': {
                'total_ingresos': total_ingresos,
                'total_egresos': total_egresos,
                'balance': balance
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """Crear una nueva transacción"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['user_id', 'type', 'category', 'amount', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Validar tipo
        if data['type'] not in ['ingreso', 'egreso']:
            return jsonify({'error': 'type debe ser "ingreso" o "egreso"'}), 400
        
        # Validar amount
        if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
            return jsonify({'error': 'amount debe ser un número positivo'}), 400
        
        # Convertir fecha
        date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        
        # Crear transacción
        import uuid
        transaction = Transaction(
            id=str(uuid.uuid4()),
            user_id=data['user_id'],
            type=data['type'],
            category=data['category'],
            amount=data['amount'],
            description=data.get('description', ''),
            date=date,
            payment_method=data.get('payment_method', 'efectivo')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict(),
            'message': 'Transacción creada exitosamente'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Obtener una transacción específica"""
    try:
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transacción no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/transactions/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Actualizar una transacción"""
    try:
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transacción no encontrada'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'type' in data and data['type'] in ['ingreso', 'egreso']:
            transaction.type = data['type']
        
        if 'category' in data:
            transaction.category = data['category']
        
        if 'amount' in data:
            if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
                return jsonify({'error': 'amount debe ser un número positivo'}), 400
            transaction.amount = data['amount']
        
        if 'description' in data:
            transaction.description = data['description']
        
        if 'date' in data:
            transaction.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        
        if 'payment_method' in data:
            transaction.payment_method = data['payment_method']
        
        transaction.updated_at = datetime.now(bolivia_tz)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict(),
            'message': 'Transacción actualizada exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Eliminar una transacción"""
    try:
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transacción no encontrada'}), 404
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transacción eliminada exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/summary/<user_id>', methods=['GET'])
def get_summary(user_id):
    """Obtener resumen financiero de un usuario"""
    try:
        # Obtener todas las transacciones del usuario
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        # Calcular totales
        total_ingresos = sum(t.amount for t in transactions if t.type == 'ingreso')
        total_egresos = sum(t.amount for t in transactions if t.type == 'egreso')
        balance = total_ingresos - total_egresos
        
        # Agrupar por categoría
        ingresos_por_categoria = {}
        egresos_por_categoria = {}
        
        for t in transactions:
            if t.type == 'ingreso':
                if t.category not in ingresos_por_categoria:
                    ingresos_por_categoria[t.category] = 0
                ingresos_por_categoria[t.category] += t.amount
            else:
                if t.category not in egresos_por_categoria:
                    egresos_por_categoria[t.category] = 0
                egresos_por_categoria[t.category] += t.amount
        
        return jsonify({
            'success': True,
            'data': {
                'total_ingresos': total_ingresos,
                'total_egresos': total_egresos,
                'balance': balance,
                'total_transacciones': len(transactions),
                'ingresos_por_categoria': ingresos_por_categoria,
                'egresos_por_categoria': egresos_por_categoria
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        transaction_count = Transaction.query.count()
        return jsonify({
            'success': True,
            'message': 'Finance API is running',
            'transactions_count': transaction_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

