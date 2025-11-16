import os
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

# Verificar y crear tablas al iniciar si no existen
with app.app_context():
    try:
        # Verificar si las tablas existen
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # Si no hay tablas, crearlas
        if not existing_tables:
            print("📦 No se encontraron tablas. Creando tablas...")
            db.create_all()
            
            # Verificar que se crearon
            inspector = db.inspect(db.engine)
            new_tables = inspector.get_table_names()
            print(f"✅ Tablas creadas exitosamente! ({len(new_tables)} tablas)")
            for table in new_tables:
                print(f"   - {table}")
        else:
            print(f"✅ Base de datos lista ({len(existing_tables)} tablas existentes)")
    except Exception as e:
        print(f"⚠️  Advertencia al verificar tablas: {e}")
        # Intentar crear las tablas de todas formas
        try:
            db.create_all()
            print("✅ Tablas creadas después del error inicial")
        except Exception as e2:
            print(f"❌ Error al crear tablas: {e2}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)