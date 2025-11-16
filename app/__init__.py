from flask import Flask
from flask_cors import CORS # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
from flask_apscheduler import APScheduler # type: ignore
from datetime import datetime
import pytz
import os

from .db import db
from flask_migrate import Migrate # type: ignore
from .models import (
    LearningCourse, LearningSection, 
    UserCourseProgress, UserSectionProgress,
    Transaction,
    CommunityPost, CommunityComment, CommunityLike,
    Achievement, UserAchievement,
    MentorAvailability, MentorBooking, Event, EventRegistration
    
    
)
from app.config import Config  



migrate = Migrate()
jwt = JWTManager()
scheduler = APScheduler()



def create_app(config_class=None):
    app = Flask(__name__)

    # Configure the application
    if config_class is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    # Register blueprints and extensions
    CORS(app,
        resources={r"/*": {
            "origins": [
                "http://localhost:5173", 
                "http://localhost:8080",
                "http://localhost:3000", 
                "http://localhost:3001", 
                "https://frontend-childfund.onrender.com",
                "https://lovable.dev",
                "https://frontend-childfund-2gby9knzj-serratenikoll-gmailcoms-projects.vercel.app/"
            ],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type", "Authorization", "Content-Disposition"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }},
        supports_credentials=True
    )
    
    JWTManager(app)
    
    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar y iniciar APScheduler
    scheduler.init_app(app)
    scheduler.start()
    
    # Registrar blueprints
    from app.routes.learning import learning_bp
    from app.routes.finance import finance_bp
    from app.routes.community import community_bp
    from app.routes.achievements import achievements_bp
    from app.routes.calendar import calendar_bp
    app.register_blueprint(learning_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(calendar_bp)

    return app
