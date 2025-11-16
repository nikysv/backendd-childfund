from datetime import datetime
import pytz # type: ignore
from .db import db
import uuid

bolivia_tz = pytz.timezone('America/La_Paz')

# ============================================
# MODELOS DE APRENDIZAJE (Solo para Render)
# Los usuarios se manejan en Supabase
# ============================================

class LearningCourse(db.Model):
    __tablename__ = 'learning_courses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_type = db.Column(db.String(10), nullable=False)  # 'pre' o 'inc'
    month_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    duration_weeks = db.Column(db.Integer)
    order_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    sections = db.relationship('LearningSection', back_populates='course', cascade='all, delete-orphan')
    user_progress = db.relationship('UserCourseProgress', back_populates='course', cascade='all, delete-orphan', foreign_keys='UserCourseProgress.course_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'route_type': self.route_type,
            'month_number': self.month_number,
            'title': self.title,
            'description': self.description,
            'duration_weeks': self.duration_weeks,
            'order_number': self.order_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LearningSection(db.Model):
    __tablename__ = 'learning_sections'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(36), db.ForeignKey('learning_courses.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer)
    video_url = db.Column(db.String(500))
    content = db.Column(db.Text)
    order_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    course = db.relationship('LearningCourse', back_populates='sections')
    user_progress = db.relationship('UserSectionProgress', back_populates='section', cascade='all, delete-orphan', foreign_keys='UserSectionProgress.section_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'video_url': self.video_url,
            'content': self.content,
            'order_number': self.order_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserCourseProgress(db.Model):
    __tablename__ = 'user_course_progress'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario de Supabase
    course_id = db.Column(db.String(36), db.ForeignKey('learning_courses.id', ondelete='CASCADE'), nullable=False)
    completed_sections = db.Column(db.Integer, default=0)
    total_sections = db.Column(db.Integer, nullable=False)
    progress_percentage = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    completed_at = db.Column(db.DateTime(timezone=True))
    
    # Relaciones (sin user porque está en Supabase)
    course = db.relationship('LearningCourse', back_populates='user_progress', foreign_keys=[course_id])
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'completed_sections': self.completed_sections,
            'total_sections': self.total_sections,
            'progress_percentage': self.progress_percentage,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class UserSectionProgress(db.Model):
    __tablename__ = 'user_section_progress'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario de Supabase
    section_id = db.Column(db.String(36), db.ForeignKey('learning_sections.id', ondelete='CASCADE'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    
    # Relaciones (sin user porque está en Supabase)
    section = db.relationship('LearningSection', back_populates='user_progress', foreign_keys=[section_id])
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'section_id', name='unique_user_section'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'section_id': self.section_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============================================
# MODELOS DE FINANZAS (ERP)
# ============================================

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario de Supabase
    type = db.Column(db.String(10), nullable=False)  # 'ingreso' o 'egreso'
    category = db.Column(db.String(100), nullable=False)  # Categoría de la transacción
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    payment_method = db.Column(db.String(50))  # efectivo, transferencia, tarjeta, etc.
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(bolivia_tz))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================
# MODELOS DE COMUNIDAD (FORO)
# ============================================

class CommunityPost(db.Model):
    __tablename__ = 'community_posts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario de Supabase
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # experiencia, curiosidad, pregunta, etc.
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    comments = db.relationship('CommunityComment', back_populates='post', cascade='all, delete-orphan')
    likes = db.relationship('CommunityLike', back_populates='post', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CommunityComment(db.Model):
    __tablename__ = 'community_comments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(db.String(36), db.ForeignKey('community_posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario de Supabase
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    post = db.relationship('CommunityPost', back_populates='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CommunityLike(db.Model):
    __tablename__ = 'community_likes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(db.String(36), db.ForeignKey('community_posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario de Supabase
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    post = db.relationship('CommunityPost', back_populates='likes')
    
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============================================
# MODELOS DE LOGROS Y RECOMPENSAS
# ============================================

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100))  # Nombre del icono o emoji
    points = db.Column(db.Integer, default=0)  # Puntos que otorga
    category = db.Column(db.String(50))  # aprendizaje, ventas, comunidad, etc.
    requirement_type = db.Column(db.String(50))  # course_completed, section_completed, first_sale, etc.
    requirement_value = db.Column(db.String(255))  # Valor específico del requisito (ej: course_id)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    user_achievements = db.relationship('UserAchievement', back_populates='achievement', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'points': self.points,
            'category': self.category,
            'requirement_type': self.requirement_type,
            'requirement_value': self.requirement_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario de Supabase
    achievement_id = db.Column(db.String(36), db.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False)
    unlocked_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    progress = db.Column(db.Integer, default=0)  # Progreso hacia el logro (0-100)
    
    # Relaciones
    achievement = db.relationship('Achievement', back_populates='user_achievements')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress': self.progress,
            'achievement': self.achievement.to_dict() if self.achievement else None
        }

# ============================================
# MODELOS DE CALENDARIO Y EVENTOS
# ============================================

class MentorAvailability(db.Model):
    __tablename__ = 'mentor_availability'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mentor_id = db.Column(db.String(36), nullable=False)  # ID del mentor (puede ser user_id de Supabase)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    session_type = db.Column(db.String(20), nullable=False)  # 'individual' o 'grupo'
    max_participants = db.Column(db.Integer, default=1)  # Para sesiones grupales
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz), onupdate=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    bookings = db.relationship('MentorBooking', back_populates='availability', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'mentor_id': self.mentor_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'session_type': self.session_type,
            'max_participants': self.max_participants,
            'is_available': self.is_available,
            'booked_count': len([b for b in self.bookings if b.status == 'confirmed']),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MentorBooking(db.Model):
    __tablename__ = 'mentor_bookings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    availability_id = db.Column(db.String(36), db.ForeignKey('mentor_availability.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)  # ID del usuario que reserva
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz), onupdate=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    availability = db.relationship('MentorAvailability', back_populates='bookings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'availability_id': self.availability_id,
            'user_id': self.user_id,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'availability': self.availability.to_dict() if self.availability else None
        }

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50))  # 'workshop', 'webinar', 'networking', 'evento_especial', etc.
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    end_date = db.Column(db.DateTime(timezone=True), nullable=False)
    location = db.Column(db.String(255))  # Presencial o URL para virtual
    is_virtual = db.Column(db.Boolean, default=False)
    max_participants = db.Column(db.Integer)
    organizer_id = db.Column(db.String(36))  # ID del organizador
    image_url = db.Column(db.String(500))
    registration_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz), onupdate=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    registrations = db.relationship('EventRegistration', back_populates='event', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'is_virtual': self.is_virtual,
            'max_participants': self.max_participants,
            'organizer_id': self.organizer_id,
            'image_url': self.image_url,
            'registration_url': self.registration_url,
            'registered_count': len([r for r in self.registrations if r.status == 'confirmed']),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = db.Column(db.String(36), db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, waitlist
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(bolivia_tz))
    
    # Relaciones
    event = db.relationship('Event', back_populates='registrations')
    
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='unique_event_registration'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'event': self.event.to_dict() if self.event else None
        }