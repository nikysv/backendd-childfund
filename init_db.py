"""Script para crear solo las tablas en producción"""
from app import create_app
from app.db import db

app = create_app()

def create_tables_only():
    """Crear todas las tablas sin datos de ejemplo"""
    with app.app_context():
        print("📦 Creando tablas...")
        db.create_all()
        print("✅ Tablas creadas exitosamente")

if __name__ == '__main__':
    create_tables_only()

