from flask import Blueprint, jsonify, request
from app.db import db
from app.models import Achievement, UserAchievement, UserCourseProgress, UserSectionProgress, Transaction
from sqlalchemy import and_
import uuid
from datetime import datetime
import pytz

achievements_bp = Blueprint('achievements', __name__, url_prefix='/api/achievements')
bolivia_tz = pytz.timezone('America/La_Paz')

def check_and_unlock_achievements(user_id, achievement_type, achievement_value=None):
    """Verificar y desbloquear logros según el tipo"""
    try:
        # Buscar logros que coincidan con el tipo
        query = Achievement.query.filter_by(requirement_type=achievement_type)
        if achievement_value:
            query = query.filter_by(requirement_value=achievement_value)
        
        achievements = query.all()
        unlocked = []
        
        for achievement in achievements:
            # Verificar si el usuario ya tiene este logro
            existing = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            
            if existing and existing.progress >= 100:
                continue  # Ya está desbloqueado
            
            # Verificar si cumple el requisito
            should_unlock = False
            progress = 0
            
            if achievement_type == 'course_completed':
                # Verificar si el curso está completado
                course_progress = UserCourseProgress.query.filter_by(
                    user_id=user_id,
                    course_id=achievement_value
                ).first()
                if course_progress and course_progress.progress_percentage >= 100:
                    should_unlock = True
                    progress = 100
            
            elif achievement_type == 'first_course_completed':
                # Verificar si completó al menos un curso
                completed = UserCourseProgress.query.filter(
                    and_(
                        UserCourseProgress.user_id == user_id,
                        UserCourseProgress.progress_percentage >= 100
                    )
                ).count()
                if completed >= 1:
                    should_unlock = True
                    progress = 100
            
            elif achievement_type == 'first_sale':
                # Verificar si tiene al menos una venta
                sales = Transaction.query.filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.type == 'ingreso'
                    )
                ).count()
                if sales >= 1:
                    should_unlock = True
                    progress = 100
            
            elif achievement_type == 'first_post':
                # Verificar si tiene al menos un post
                from app.models import CommunityPost
                posts = CommunityPost.query.filter_by(user_id=user_id).count()
                if posts >= 1:
                    should_unlock = True
                    progress = 100
            
            if should_unlock:
                if existing:
                    existing.progress = 100
                    existing.unlocked_at = datetime.now(bolivia_tz)
                else:
                    user_achievement = UserAchievement(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        achievement_id=achievement.id,
                        progress=100,
                        unlocked_at=datetime.now(bolivia_tz)
                    )
                    db.session.add(user_achievement)
                    unlocked.append(achievement.to_dict())
                
                db.session.commit()
        
        return unlocked
    
    except Exception as e:
        db.session.rollback()
        print(f"Error checking achievements: {str(e)}")
        return []

@achievements_bp.route('/user/<user_id>', methods=['GET'])
def get_user_achievements(user_id):
    """Obtener logros de un usuario"""
    try:
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        achievements_data = [ua.to_dict() for ua in user_achievements]
        
        # Obtener todos los logros disponibles para mostrar progreso
        all_achievements = Achievement.query.all()
        all_achievements_dict = {}
        
        for ach in all_achievements:
            user_ach = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=ach.id
            ).first()
            
            all_achievements_dict[ach.id] = {
                **ach.to_dict(),
                'unlocked': user_ach is not None and user_ach.progress >= 100,
                'progress': user_ach.progress if user_ach else 0,
                'unlocked_at': user_ach.unlocked_at.isoformat() if user_ach and user_ach.unlocked_at else None
            }
        
        return jsonify({
            'success': True,
            'data': list(all_achievements_dict.values()),
            'unlocked_count': len([a for a in all_achievements_dict.values() if a['unlocked']])
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@achievements_bp.route('/check/<user_id>', methods=['POST'])
def check_achievements(user_id):
    """Verificar y desbloquear logros para un usuario"""
    try:
        data = request.get_json()
        achievement_type = data.get('type')
        achievement_value = data.get('value')
        
        unlocked = check_and_unlock_achievements(user_id, achievement_type, achievement_value)
        
        return jsonify({
            'success': True,
            'unlocked': unlocked,
            'count': len(unlocked)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@achievements_bp.route('/stats/<user_id>', methods=['GET'])
def get_achievement_stats(user_id):
    """Obtener estadísticas de logros de un usuario"""
    try:
        total_achievements = Achievement.query.count()
        unlocked_achievements = UserAchievement.query.filter(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.progress >= 100
            )
        ).count()
        
        # Calcular puntos totales
        unlocked_ua = UserAchievement.query.filter(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.progress >= 100
            )
        ).all()
        
        total_points = sum(ua.achievement.points for ua in unlocked_ua if ua.achievement)
        
        # Logros por categoría
        achievements_by_category = {}
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        
        for ua in user_achievements:
            if ua.progress >= 100 and ua.achievement:
                category = ua.achievement.category or 'otros'
                if category not in achievements_by_category:
                    achievements_by_category[category] = 0
                achievements_by_category[category] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'total_achievements': total_achievements,
                'unlocked_achievements': unlocked_achievements,
                'total_points': total_points,
                'completion_percentage': (unlocked_achievements / total_achievements * 100) if total_achievements > 0 else 0,
                'by_category': achievements_by_category
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@achievements_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        achievements_count = Achievement.query.count()
        return jsonify({
            'success': True,
            'message': 'Achievements API is running',
            'achievements_count': achievements_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

