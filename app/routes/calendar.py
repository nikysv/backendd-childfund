from flask import Blueprint, jsonify, request
from app.db import db
from app.models import (
    MentorAvailability, MentorBooking, Event, EventRegistration
)
from sqlalchemy import and_, or_, func
from datetime import datetime, date, time, timedelta
import pytz
import uuid

calendar_bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')
bolivia_tz = pytz.timezone('America/La_Paz')

# ============================================
# DISPONIBILIDAD DEL MENTOR
# ============================================

@calendar_bp.route('/availability', methods=['GET'])
def get_mentor_availability():
    """Obtener disponibilidad del mentor"""
    try:
        mentor_id = request.args.get('mentor_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        session_type = request.args.get('session_type')  # 'individual', 'grupo', o None para ambos
        
        query = MentorAvailability.query.filter_by(is_available=True)
        
        if mentor_id:
            query = query.filter_by(mentor_id=mentor_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(MentorAvailability.date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(MentorAvailability.date <= end)
        
        if session_type:
            query = query.filter_by(session_type=session_type)
        
        availability = query.order_by(MentorAvailability.date, MentorAvailability.start_time).all()
        
        return jsonify({
            'success': True,
            'data': [a.to_dict() for a in availability]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/availability/<availability_id>', methods=['GET'])
def get_availability_detail(availability_id):
    """Obtener detalle de una disponibilidad específica"""
    try:
        availability = MentorAvailability.query.get(availability_id)
        if not availability:
            return jsonify({'error': 'Disponibilidad no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': availability.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Crear una reserva de mentoría"""
    try:
        data = request.get_json()
        availability_id = data.get('availability_id')
        user_id = data.get('user_id')
        notes = data.get('notes', '')
        
        if not availability_id or not user_id:
            return jsonify({'error': 'availability_id y user_id son requeridos'}), 400
        
        # Verificar que la disponibilidad existe y está disponible
        availability = MentorAvailability.query.get(availability_id)
        if not availability:
            return jsonify({'error': 'Disponibilidad no encontrada'}), 404
        
        if not availability.is_available:
            return jsonify({'error': 'Esta disponibilidad ya no está disponible'}), 400
        
        # Verificar si ya existe una reserva para este usuario en esta disponibilidad
        existing = MentorBooking.query.filter_by(
            availability_id=availability_id,
            user_id=user_id,
            status='confirmed'
        ).first()
        
        if existing:
            return jsonify({'error': 'Ya tienes una reserva para esta sesión'}), 400
        
        # Verificar capacidad para sesiones grupales
        if availability.session_type == 'grupo':
            confirmed_bookings = MentorBooking.query.filter(
                and_(
                    MentorBooking.availability_id == availability_id,
                    MentorBooking.status == 'confirmed'
                )
            ).count()
            
            if confirmed_bookings >= availability.max_participants:
                return jsonify({'error': 'Esta sesión grupal está llena'}), 400
        
        # Crear la reserva
        booking = MentorBooking(
            id=str(uuid.uuid4()),
            availability_id=availability_id,
            user_id=user_id,
            status='confirmed',
            notes=notes
        )
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': booking.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/bookings/user/<user_id>', methods=['GET'])
def get_user_bookings(user_id):
    """Obtener reservas de un usuario"""
    try:
        bookings = MentorBooking.query.filter_by(user_id=user_id).order_by(
            MentorBooking.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [b.to_dict() for b in bookings]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """Cancelar una reserva"""
    try:
        booking = MentorBooking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Reserva no encontrada'}), 404
        
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reserva cancelada exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================
# EVENTOS
# ============================================

@calendar_bp.route('/events', methods=['GET'])
def get_events():
    """Obtener eventos"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        event_type = request.args.get('event_type')
        
        query = Event.query
        
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Event.start_date >= start)
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Event.end_date <= end)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        events = query.order_by(Event.start_date).all()
        
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in events]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/<event_id>', methods=['GET'])
def get_event_detail(event_id):
    """Obtener detalle de un evento"""
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Evento no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': event.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/<event_id>/register', methods=['POST'])
def register_to_event(event_id):
    """Registrarse a un evento"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id es requerido'}), 400
        
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Evento no encontrado'}), 404
        
        # Verificar si ya está registrado
        existing = EventRegistration.query.filter_by(
            event_id=event_id,
            user_id=user_id
        ).first()
        
        if existing:
            if existing.status == 'confirmed':
                return jsonify({'error': 'Ya estás registrado en este evento'}), 400
            else:
                existing.status = 'confirmed'
                db.session.commit()
                return jsonify({
                    'success': True,
                    'data': existing.to_dict()
                }), 200
        
        # Verificar capacidad
        if event.max_participants:
            confirmed_registrations = EventRegistration.query.filter(
                and_(
                    EventRegistration.event_id == event_id,
                    EventRegistration.status == 'confirmed'
                )
            ).count()
            
            if confirmed_registrations >= event.max_participants:
                # Agregar a lista de espera
                registration = EventRegistration(
                    id=str(uuid.uuid4()),
                    event_id=event_id,
                    user_id=user_id,
                    status='waitlist'
                )
                db.session.add(registration)
                db.session.commit()
                return jsonify({
                    'success': True,
                    'data': registration.to_dict(),
                    'message': 'Evento lleno, agregado a lista de espera'
                }), 200
        
        # Crear registro
        registration = EventRegistration(
            id=str(uuid.uuid4()),
            event_id=event_id,
            user_id=user_id,
            status='confirmed'
        )
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': registration.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/events/user/<user_id>/registrations', methods=['GET'])
def get_user_event_registrations(user_id):
    """Obtener registros de eventos de un usuario"""
    try:
        registrations = EventRegistration.query.filter_by(user_id=user_id).order_by(
            EventRegistration.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [r.to_dict() for r in registrations]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'success': True,
            'message': 'Calendar API is running'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

