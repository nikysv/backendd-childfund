"""Script para crear solo las tablas en producción"""
import os
import sys
from app import create_app
from app.db import db

# Importar todos los modelos para que db.create_all() los reconozca
from app.models import (
    LearningCourse, LearningSection, 
    UserCourseProgress, UserSectionProgress,
    Transaction,
    CommunityPost, CommunityComment, CommunityLike,
    Achievement, UserAchievement,
    MentorAvailability, MentorBooking, Event, EventRegistration
)

app = create_app()

def create_tables_only():
    """Crear todas las tablas sin datos de ejemplo"""
    try:
        with app.app_context():
            # Verificar conexión a la base de datos
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            if not database_url:
                print("❌ ERROR: No se encontró DATABASE_URL en las variables de entorno")
                sys.exit(1)
            
            print(f"📊 Conectando a la base de datos...")
            print(f"   Database: {database_url.split('@')[1] if '@' in database_url else 'N/A'}")
            
            # Intentar conectar
            try:
                db.engine.connect()
                print("✅ Conexión a la base de datos exitosa")
            except Exception as e:
                print(f"❌ ERROR al conectar a la base de datos: {e}")
                sys.exit(1)
            
            print("\n📦 Creando tablas...")
            
            # Crear todas las tablas
            db.create_all()
            
            # Verificar que se crearon las tablas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n✅ Tablas creadas exitosamente!")
            print(f"📋 Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
                
    except Exception as e:
        print(f"\n❌ ERROR al crear las tablas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    create_tables_only()
