from flask import Blueprint, jsonify, request
from app.db import db
from app.models import LearningCourse, LearningSection, UserCourseProgress, UserSectionProgress
from sqlalchemy import and_

learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')

@learning_bp.route('/courses', methods=['GET'])
def get_courses():
    """
    Obtener cursos filtrados por ruta
    Query params: route_type (pre o inc)
    """
    route_type = request.args.get('route_type')
    
    if not route_type or route_type not in ['pre', 'inc']:
        return jsonify({'error': 'route_type es requerido y debe ser "pre" o "inc"'}), 400
    
    try:
        courses = LearningCourse.query.filter_by(route_type=route_type).order_by(LearningCourse.order_number).all()
        
        courses_data = []
        for course in courses:
            course_dict = course.to_dict()
            # Contar secciones
            sections_count = LearningSection.query.filter_by(course_id=course.id).count()
            course_dict['total_sections'] = sections_count
            courses_data.append(course_dict)
        
        return jsonify({
            'success': True,
            'data': courses_data,
            'count': len(courses_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    """Obtener un curso específico con sus secciones"""
    try:
        course = LearningCourse.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Curso no encontrado'}), 404
        
        course_dict = course.to_dict()
        
        # Obtener secciones
        sections = LearningSection.query.filter_by(course_id=course_id).order_by(LearningSection.order_number).all()
        course_dict['sections'] = [section.to_dict() for section in sections]
        course_dict['total_sections'] = len(sections)
        
        return jsonify({
            'success': True,
            'data': course_dict
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/courses/<course_id>/sections', methods=['GET'])
def get_course_sections(course_id):
    """Obtener todas las secciones de un curso"""
    try:
        course = LearningCourse.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Curso no encontrado'}), 404
        
        sections = LearningSection.query.filter_by(course_id=course_id).order_by(LearningSection.order_number).all()
        sections_data = [section.to_dict() for section in sections]
        
        return jsonify({
            'success': True,
            'data': sections_data,
            'count': len(sections_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/progress/<user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Obtener el progreso de un usuario en todos los cursos"""
    try:
        # Obtener progreso de cursos
        course_progress = UserCourseProgress.query.filter_by(user_id=user_id).all()
        progress_data = [progress.to_dict() for progress in course_progress]
        
        # Obtener progreso de secciones
        section_progress = UserSectionProgress.query.filter_by(user_id=user_id).all()
        sections_data = [progress.to_dict() for progress in section_progress]
        
        return jsonify({
            'success': True,
            'data': {
                'courses': progress_data,
                'sections': sections_data
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/progress/<user_id>/course/<course_id>', methods=['GET'])
def get_user_course_progress(user_id, course_id):
    """Obtener el progreso de un usuario en un curso específico"""
    try:
        progress = UserCourseProgress.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not progress:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No hay progreso registrado'
            }), 200
        
        # Obtener progreso de secciones del curso
        sections = LearningSection.query.filter_by(course_id=course_id).all()
        section_ids = [s.id for s in sections]
        
        section_progress = UserSectionProgress.query.filter(
            and_(
                UserSectionProgress.user_id == user_id,
                UserSectionProgress.section_id.in_(section_ids)
            )
        ).all()
        
        progress_dict = progress.to_dict()
        progress_dict['sections_progress'] = [sp.to_dict() for sp in section_progress]
        
        return jsonify({
            'success': True,
            'data': progress_dict
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/progress/section', methods=['POST'])
def update_section_progress():
    """Actualizar el progreso de una sección"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        section_id = data.get('section_id')
        completed = data.get('completed', False)
        
        if not user_id or not section_id:
            return jsonify({'error': 'user_id y section_id son requeridos'}), 400
        
        # Buscar o crear progreso de sección
        progress = UserSectionProgress.query.filter_by(
            user_id=user_id,
            section_id=section_id
        ).first()
        
        if progress:
            progress.completed = completed
            if completed:
                from datetime import datetime
                import pytz
                bolivia_tz = pytz.timezone('America/La_Paz')
                progress.completed_at = datetime.now(bolivia_tz)
        else:
            import uuid
            progress = UserSectionProgress(
                id=str(uuid.uuid4()),
                user_id=user_id,
                section_id=section_id,
                completed=completed
            )
            if completed:
                from datetime import datetime
                import pytz
                bolivia_tz = pytz.timezone('America/La_Paz')
                progress.completed_at = datetime.now(bolivia_tz)
            db.session.add(progress)
        
        db.session.commit()
        
        # Actualizar progreso del curso
        section = LearningSection.query.get(section_id)
        if section:
            update_course_progress(user_id, section.course_id)
        
        return jsonify({
            'success': True,
            'data': progress.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_course_progress(user_id, course_id):
    """Actualizar el progreso general de un curso basado en las secciones completadas"""
    try:
        # Obtener todas las secciones del curso
        sections = LearningSection.query.filter_by(course_id=course_id).all()
        total_sections = len(sections)
        
        if total_sections == 0:
            return
        
        section_ids = [s.id for s in sections]
        
        # Contar secciones completadas
        completed_sections = UserSectionProgress.query.filter(
            and_(
                UserSectionProgress.user_id == user_id,
                UserSectionProgress.section_id.in_(section_ids),
                UserSectionProgress.completed == True
            )
        ).count()
        
        # Calcular porcentaje
        progress_percentage = int((completed_sections / total_sections) * 100)
        
        # Buscar o crear progreso del curso
        course_progress = UserCourseProgress.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if course_progress:
            course_progress.completed_sections = completed_sections
            course_progress.total_sections = total_sections
            course_progress.progress_percentage = progress_percentage
            
            if progress_percentage == 100 and not course_progress.completed_at:
                from datetime import datetime
                import pytz
                bolivia_tz = pytz.timezone('America/La_Paz')
                course_progress.completed_at = datetime.now(bolivia_tz)
                
                # Verificar logros al completar un curso
                from app.routes.achievements import check_and_unlock_achievements
                check_and_unlock_achievements(user_id, 'course_completed', course_id)
                check_and_unlock_achievements(user_id, 'first_course_completed')
        else:
            import uuid
            course_progress = UserCourseProgress(
                id=str(uuid.uuid4()),
                user_id=user_id,
                course_id=course_id,
                completed_sections=completed_sections,
                total_sections=total_sections,
                progress_percentage=progress_percentage
            )
            db.session.add(course_progress)
            
            # Si se completa al crear, verificar logros
            if progress_percentage == 100:
                from app.routes.achievements import check_and_unlock_achievements
                check_and_unlock_achievements(user_id, 'course_completed', course_id)
                check_and_unlock_achievements(user_id, 'first_course_completed')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating course progress: {str(e)}")

@learning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a la base de datos
        course_count = LearningCourse.query.count()
        return jsonify({
            'success': True,
            'message': 'Learning API is running',
            'courses_count': course_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

