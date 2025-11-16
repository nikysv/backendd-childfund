"""
Script para inicializar y poblar la base de datos de aprendizaje
Ejecutar con: python setup_db.py
"""
import os
import uuid
from datetime import datetime, timedelta, time, date
import pytz
from app import create_app
from app.db import db
from app.models import (
    LearningCourse, LearningSection, Transaction, 
    CommunityPost, CommunityComment, CommunityLike,
    Achievement, UserAchievement,
    MentorAvailability, Event
)

app = create_app()

def create_tables():
    """Crear todas las tablas"""
    with app.app_context():
        print("📦 Creando tablas...")
        db.create_all()
        print("✅ Tablas creadas exitosamente\n")

def seed_data():
    """Poblar la base de datos con cursos"""
    with app.app_context():
        # Verificar si ya existen cursos
        existing = LearningCourse.query.count()
        if existing > 0:
            print(f"⚠️  Ya existen {existing} cursos. Limpiando...")
            LearningSection.query.delete()
            LearningCourse.query.delete()
            db.session.commit()
        
        print("📚 Insertando cursos de PRE-INCUBADORA (6 meses)...")
        
        pre_courses_data = [
            {'route_type': 'pre', 'month_number': 1, 'title': 'Ideación y Oportunidad', 'description': 'Aprende Design Thinking para validar tu idea de negocio', 'duration_weeks': 3, 'order_number': 1},
            {'route_type': 'pre', 'month_number': 1, 'title': 'Validación de Problema y Solución', 'description': 'Técnicas para validar si tu solución resuelve un problema real', 'duration_weeks': 2, 'order_number': 2},
            {'route_type': 'pre', 'month_number': 2, 'title': 'Propuesta de Valor', 'description': 'Diseña una propuesta de valor única y segmenta tus clientes', 'duration_weeks': 3, 'order_number': 3},
            {'route_type': 'pre', 'month_number': 2, 'title': 'Finanzas Básicas', 'description': 'Introducción a costos, precios y utilidad', 'duration_weeks': 2, 'order_number': 4},
            {'route_type': 'pre', 'month_number': 3, 'title': 'Branding Inicial', 'description': 'Crea la identidad visual de tu marca', 'duration_weeks': 2, 'order_number': 5},
            {'route_type': 'pre', 'month_number': 3, 'title': 'Presencia Digital', 'description': 'Establece tu presencia en redes sociales', 'duration_weeks': 2, 'order_number': 6},
            {'route_type': 'pre', 'month_number': 4, 'title': 'Marketing Digital', 'description': 'Domina Facebook, Instagram, TikTok y WhatsApp Business', 'duration_weeks': 4, 'order_number': 7},
            {'route_type': 'pre', 'month_number': 5, 'title': 'Herramientas Digitales', 'description': 'Aprende Canva, ChatGPT y más herramientas', 'duration_weeks': 3, 'order_number': 8},
            {'route_type': 'pre', 'month_number': 5, 'title': 'Producto Mínimo Viable', 'description': 'Crea tu primer prototipo o MVP', 'duration_weeks': 3, 'order_number': 9},
            {'route_type': 'pre', 'month_number': 6, 'title': 'Habilidades Blandas', 'description': 'Propósito, motivación y resiliencia emprendedora', 'duration_weeks': 4, 'order_number': 10},
        ]
        
        pre_courses = []
        for data in pre_courses_data:
            course = LearningCourse(id=str(uuid.uuid4()), **data)
            db.session.add(course)
            pre_courses.append(course)
            print(f"  ✓ {course.title}")
        
        print("\n📚 Insertando cursos de INCUBADORA (4 meses)...")
        
        inc_courses_data = [
            {'route_type': 'inc', 'month_number': 1, 'title': 'Desarrollo Personal y Liderazgo', 'description': 'Lidera con propósito y visión clara', 'duration_weeks': 1, 'order_number': 1},
            {'route_type': 'inc', 'month_number': 1, 'title': 'Modelo de Negocio Canvas', 'description': 'Diseña tu modelo de negocio completo', 'duration_weeks': 1, 'order_number': 2},
            {'route_type': 'inc', 'month_number': 1, 'title': 'Design Thinking Aplicado', 'description': 'Innovación centrada en el usuario', 'duration_weeks': 1, 'order_number': 3},
            {'route_type': 'inc', 'month_number': 1, 'title': 'Habilidades Socioemocionales', 'description': 'Inteligencia emocional para emprendedores', 'duration_weeks': 1, 'order_number': 4},
            {'route_type': 'inc', 'month_number': 2, 'title': 'Marketing Estratégico', 'description': 'Estrategia de marketing y propuesta de valor', 'duration_weeks': 1, 'order_number': 5},
            {'route_type': 'inc', 'month_number': 2, 'title': 'Construcción de Marca', 'description': 'Branding profesional y diferenciación', 'duration_weeks': 1, 'order_number': 6},
            {'route_type': 'inc', 'month_number': 2, 'title': 'Marketing Digital Intensivo', 'description': 'Domina todas las plataformas digitales', 'duration_weeks': 2, 'order_number': 7},
            {'route_type': 'inc', 'month_number': 2, 'title': 'Herramientas Digitales Avanzadas', 'description': 'Canva, ChatGPT, edición de video', 'duration_weeks': 1, 'order_number': 8},
            {'route_type': 'inc', 'month_number': 3, 'title': 'Visión y Conformación de Equipos', 'description': 'Construye equipos de alto rendimiento', 'duration_weeks': 1, 'order_number': 9},
            {'route_type': 'inc', 'month_number': 3, 'title': 'Estandarización de Procesos', 'description': 'Optimiza y documenta tus procesos', 'duration_weeks': 1, 'order_number': 10},
            {'route_type': 'inc', 'month_number': 3, 'title': 'CRM y Funnel de Ventas', 'description': 'Gestión de clientes y conversión', 'duration_weeks': 1, 'order_number': 11},
            {'route_type': 'inc', 'month_number': 3, 'title': 'Formalización Legal', 'description': 'NIT, SENASAG, SEPREC, tipos societarios', 'duration_weeks': 2, 'order_number': 12},
            {'route_type': 'inc', 'month_number': 3, 'title': 'Bootcamp: Oratoria y Pitch', 'description': 'Presenta tu negocio con impacto', 'duration_weeks': 1, 'order_number': 13},
            {'route_type': 'inc', 'month_number': 4, 'title': 'Ciclo de Inversiones', 'description': 'Tipos de financiamiento y capital', 'duration_weeks': 1, 'order_number': 14},
            {'route_type': 'inc', 'month_number': 4, 'title': 'Estrategias de Expansión', 'description': 'Penetración y crecimiento de mercado', 'duration_weeks': 1, 'order_number': 15},
            {'route_type': 'inc', 'month_number': 4, 'title': 'Preparación Demo Day', 'description': 'Prepara tu presentación final', 'duration_weeks': 2, 'order_number': 16},
        ]
        
        inc_courses = []
        for data in inc_courses_data:
            course = LearningCourse(id=str(uuid.uuid4()), **data)
            db.session.add(course)
            inc_courses.append(course)
            print(f"  ✓ {course.title}")
        
        db.session.commit()
        print("\n✅ Cursos insertados exitosamente!")
        
        # Agregar secciones de ejemplo
        print("\n📝 Agregando secciones de ejemplo...")
        
        # Secciones para "Ideación y Oportunidad"
        if pre_courses:
            sections_data = [
                {'title': 'Introducción al Design Thinking', 'description': 'Conoce la metodología y sus fases', 'duration_minutes': 45, 'order_number': 1},
                {'title': 'Empatizar con tu usuario', 'description': 'Técnicas de investigación de usuarios', 'duration_minutes': 60, 'order_number': 2},
                {'title': 'Definir el problema', 'description': 'Cómo formular el problema correcto', 'duration_minutes': 50, 'order_number': 3},
                {'title': 'Idear soluciones', 'description': 'Brainstorming y técnicas creativas', 'duration_minutes': 55, 'order_number': 4},
            ]
            for data in sections_data:
                section = LearningSection(id=str(uuid.uuid4()), course_id=pre_courses[0].id, **data)
                db.session.add(section)
            print(f"  ✓ Secciones agregadas a '{pre_courses[0].title}'")
        
        # Secciones para "Desarrollo Personal y Liderazgo"
        if inc_courses:
            sections_data = [
                {'title': 'Liderazgo con propósito', 'description': 'Descubre tu estilo de liderazgo', 'duration_minutes': 40, 'order_number': 1},
                {'title': 'Visión y misión personal', 'description': 'Define tu norte como emprendedor', 'duration_minutes': 45, 'order_number': 2},
                {'title': 'Gestión del tiempo', 'description': 'Prioriza y organiza tu día', 'duration_minutes': 35, 'order_number': 3},
            ]
            for data in sections_data:
                section = LearningSection(id=str(uuid.uuid4()), course_id=inc_courses[0].id, **data)
                db.session.add(section)
            print(f"  ✓ Secciones agregadas a '{inc_courses[0].title}'")
        
        db.session.commit()
        print("\n✅ Secciones de ejemplo agregadas!")

def seed_community_posts():
    """Poblar la base de datos con posts de ejemplo"""
    with app.app_context():
        # Verificar si ya existen posts
        existing = CommunityPost.query.count()
        if existing > 0:
            print(f"⚠️  Ya existen {existing} posts. Limpiando...")
            CommunityLike.query.delete()
            CommunityComment.query.delete()
            CommunityPost.query.delete()
            db.session.commit()
        
        print("\n💬 Insertando posts de ejemplo...")
        
        bolivia_tz = pytz.timezone('America/La_Paz')
        now = datetime.now(bolivia_tz)
        
        # IDs de usuarios ficticios (pero válidos)
        user_ids = [
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ]
        
        # Posts de ejemplo
        posts_data = [
            {
                'user_id': user_ids[0],
                'title': 'Mi primera venta: ¡Qué emoción!',
                'content': 'Hace una semana logré mi primera venta y no puedo estar más feliz. Después de meses trabajando en mi producto, finalmente alguien confió en mí y compró. Fue solo Bs. 50, pero para mí significa el mundo. ¿Alguien más recuerda su primera venta?',
                'category': 'experiencia',
                'created_at': now - timedelta(days=2),
            },
            {
                'user_id': user_ids[1],
                'title': '¿Cómo calcular el precio de mi producto?',
                'content': 'Estoy empezando con mi emprendimiento de productos artesanales y no sé cómo fijar el precio. He calculado mis costos pero no sé cuánto margen agregar. ¿Alguien tiene alguna fórmula o consejo que me pueda ayudar?',
                'category': 'pregunta',
                'created_at': now - timedelta(days=1),
            },
            {
                'user_id': user_ids[2],
                'title': 'Curiosidad: ¿Sabían que el 90% de las startups fallan?',
                'content': 'Leí un dato interesante: el 90% de las startups fallan, pero el 10% que sobrevive suele ser muy exitoso. Lo importante no es no fallar, sino aprender de los errores y persistir. ¿Qué opinan?',
                'category': 'curiosidad',
                'created_at': now - timedelta(hours=12),
            },
            {
                'user_id': user_ids[3],
                'title': 'Experiencia: Cómo superé mi miedo a vender',
                'content': 'Siempre tuve miedo al rechazo y me costaba mucho acercarme a clientes potenciales. Lo que me ayudó fue practicar mi pitch frente al espejo y empezar con amigos y familiares. Ahora me siento mucho más confiada. Si alguien está pasando por lo mismo, ¡pueden hacerlo!',
                'category': 'experiencia',
                'created_at': now - timedelta(hours=6),
            },
            {
                'user_id': user_ids[4],
                'title': '¿Qué herramientas digitales recomiendan para emprendedores?',
                'content': 'Estoy buscando herramientas gratuitas o de bajo costo para gestionar mi negocio. Ya uso Canva para diseño, pero necesito algo para facturación y control de inventario. ¿Qué usan ustedes?',
                'category': 'pregunta',
                'created_at': now - timedelta(hours=3),
            },
            {
                'user_id': user_ids[0],
                'title': 'Curiosidad: El poder del networking',
                'content': 'Hace un mes asistí a un evento de emprendedores y conocí a alguien que ahora es mi mejor cliente. El networking realmente funciona, pero hay que ser genuino y no solo buscar vender. ¿Han tenido experiencias similares?',
                'category': 'curiosidad',
                'created_at': now - timedelta(hours=1),
            },
        ]
        
        posts = []
        for data in posts_data:
            post = CommunityPost(id=str(uuid.uuid4()), **data)
            db.session.add(post)
            posts.append(post)
            print(f"  ✓ {post.title}")
        
        db.session.commit()
        print("\n✅ Posts insertados exitosamente!")
        
        # Agregar algunos comentarios de ejemplo
        print("\n💬 Agregando comentarios de ejemplo...")
        
        comments_data = [
            {
                'post_index': 0,
                'user_id': user_ids[1],
                'content': '¡Felicitaciones! La primera venta siempre es especial. Recuerdo la mía como si fuera ayer. ¡Sigue así!',
            },
            {
                'post_index': 0,
                'user_id': user_ids[2],
                'content': 'Mi primera venta fue hace 2 años y todavía la recuerdo. Es un momento único. ¡Mucho éxito!',
            },
            {
                'post_index': 1,
                'user_id': user_ids[0],
                'content': 'Te recomiendo usar la fórmula: Costo + (Costo × Margen deseado). Por ejemplo, si tu costo es Bs. 20 y quieres 50% de margen: 20 + (20 × 0.5) = Bs. 30',
            },
            {
                'post_index': 1,
                'user_id': user_ids[3],
                'content': 'También investiga los precios de la competencia. No quieres estar muy por encima ni muy por debajo del mercado.',
            },
            {
                'post_index': 2,
                'user_id': user_ids[4],
                'content': 'Totalmente de acuerdo. El fracaso es parte del proceso de aprendizaje. Lo importante es no rendirse.',
            },
            {
                'post_index': 3,
                'user_id': user_ids[1],
                'content': 'Gracias por compartir tu experiencia. Me identifico mucho. Voy a intentar practicar frente al espejo también.',
            },
            {
                'post_index': 3,
                'user_id': user_ids[2],
                'content': 'El miedo al rechazo es normal, pero como dices, la práctica ayuda mucho. ¡Sigue adelante!',
            },
        ]
        
        for comment_data in comments_data:
            post = posts[comment_data['post_index']]
            comment = CommunityComment(
                id=str(uuid.uuid4()),
                post_id=post.id,
                user_id=comment_data['user_id'],
                content=comment_data['content'],
                created_at=post.created_at + timedelta(hours=1)
            )
            db.session.add(comment)
        
        db.session.commit()
        print("  ✓ Comentarios agregados")
        
        # Agregar algunos likes de ejemplo
        print("\n❤️  Agregando likes de ejemplo...")
        
        # Cada post tendrá likes de diferentes usuarios
        for i, post in enumerate(posts):
            # Agregar likes de usuarios diferentes
            for j, user_id in enumerate(user_ids):
                if j != i % len(user_ids):  # No dar like a tu propio post
                    like = CommunityLike(
                        id=str(uuid.uuid4()),
                        post_id=post.id,
                        user_id=user_id,
                        created_at=post.created_at + timedelta(minutes=30)
                    )
                    db.session.add(like)
        
        db.session.commit()
        print("  ✓ Likes agregados")
        
        # Actualizar contadores en los posts
        print("\n📊 Actualizando contadores...")
        for post in posts:
            post.comments_count = CommunityComment.query.filter_by(post_id=post.id).count()
            post.likes_count = CommunityLike.query.filter_by(post_id=post.id).count()
        
        db.session.commit()
        print("  ✓ Contadores actualizados")
        
        print("\n✅ Comunidad poblada exitosamente!")

def seed_achievements():
    """Poblar la base de datos con logros de ejemplo"""
    with app.app_context():
        # Verificar si ya existen logros
        existing = Achievement.query.count()
        if existing > 0:
            print(f"⚠️  Ya existen {existing} logros. Limpiando...")
            UserAchievement.query.delete()
            Achievement.query.delete()
            db.session.commit()
        
        print("\n🏆 Insertando logros de ejemplo...")
        
        achievements_data = [
            {
                'name': 'Primer Paso',
                'description': 'Completa tu primer módulo de aprendizaje',
                'icon': '🎯',
                'points': 50,
                'category': 'aprendizaje',
                'requirement_type': 'first_course_completed',
                'requirement_value': None,
            },
            {
                'name': 'Estudiante Dedicado',
                'description': 'Completa 3 módulos de aprendizaje',
                'icon': '📚',
                'points': 150,
                'category': 'aprendizaje',
                'requirement_type': 'courses_completed',
                'requirement_value': '3',
            },
            {
                'name': 'Maestro del Aprendizaje',
                'description': 'Completa todos los módulos de tu ruta',
                'icon': '🎓',
                'points': 500,
                'category': 'aprendizaje',
                'requirement_type': 'all_courses_completed',
                'requirement_value': None,
            },
            {
                'name': 'Primera Venta',
                'description': 'Registra tu primera venta en el sistema',
                'icon': '💰',
                'points': 100,
                'category': 'ventas',
                'requirement_type': 'first_sale',
                'requirement_value': None,
            },
            {
                'name': 'Vendedor Estrella',
                'description': 'Registra 10 ventas en un mes',
                'icon': '⭐',
                'points': 200,
                'category': 'ventas',
                'requirement_type': 'sales_month',
                'requirement_value': '10',
            },
            {
                'name': 'Compartir es Cuidar',
                'description': 'Crea tu primer post en la comunidad',
                'icon': '💬',
                'points': 50,
                'category': 'comunidad',
                'requirement_type': 'first_post',
                'requirement_value': None,
            },
            {
                'name': 'Influencer',
                'description': 'Obtén 10 likes en tus posts',
                'icon': '🔥',
                'points': 150,
                'category': 'comunidad',
                'requirement_type': 'post_likes',
                'requirement_value': '10',
            },
            {
                'name': 'Ayudante',
                'description': 'Comenta en 5 posts diferentes',
                'icon': '🤝',
                'points': 100,
                'category': 'comunidad',
                'requirement_type': 'comments_count',
                'requirement_value': '5',
            },
        ]
        
        for data in achievements_data:
            achievement = Achievement(id=str(uuid.uuid4()), **data)
            db.session.add(achievement)
            print(f"  ✓ {achievement.icon} {achievement.name}")
        
        db.session.commit()
        print("\n✅ Logros insertados exitosamente!")

def seed_calendar_data():
    """Poblar la base de datos con datos de calendario de ejemplo"""
    with app.app_context():
        # Verificar si ya existen datos
        existing = MentorAvailability.query.count()
        if existing > 0:
            print(f"⚠️  Ya existen {existing} disponibilidades. Limpiando...")
            MentorAvailability.query.delete()
            Event.query.delete()
            db.session.commit()
        
        print("\n📅 Insertando datos de calendario...")
        
        bolivia_tz = pytz.timezone('America/La_Paz')
        now = datetime.now(bolivia_tz)
        
        # ID del mentor (fijo para ejemplo)
        mentor_id = "mentor-1"
        
        # Crear disponibilidad del mentor para las próximas 4 semanas
        print("  📆 Creando disponibilidad del mentor...")
        for week in range(4):
            for day in range(5):  # Lunes a Viernes
                date_offset = week * 7 + day
                avail_date = (now + timedelta(days=date_offset)).date()
                
                # Sesiones individuales: 9:00, 11:00, 15:00
                for hour in [9, 11, 15]:
                    availability = MentorAvailability(
                        id=str(uuid.uuid4()),
                        mentor_id=mentor_id,
                        date=avail_date,
                        start_time=time(hour, 0),
                        end_time=time(hour + 1, 0),
                        session_type='individual',
                        max_participants=1,
                        is_available=True
                    )
                    db.session.add(availability)
                
                # Sesión grupal: 17:00
                if day % 2 == 0:  # Lunes, Miércoles, Viernes
                    availability = MentorAvailability(
                        id=str(uuid.uuid4()),
                        mentor_id=mentor_id,
                        date=avail_date,
                        start_time=time(17, 0),
                        end_time=time(18, 30),
                        session_type='grupo',
                        max_participants=5,
                        is_available=True
                    )
                    db.session.add(availability)
        
        db.session.commit()
        print("  ✓ Disponibilidad del mentor creada")
        
        # Crear eventos de ejemplo
        print("  🎉 Creando eventos de ejemplo...")
        
        events_data = [
            {
                'title': 'Workshop: Marketing Digital para Emprendedores',
                'description': 'Aprende estrategias de marketing digital para hacer crecer tu negocio',
                'event_type': 'workshop',
                'start_date': now + timedelta(days=7, hours=10),
                'end_date': now + timedelta(days=7, hours=13),
                'location': 'Centro de Innovación, La Paz',
                'is_virtual': False,
                'max_participants': 30,
                'organizer_id': 'organizer-1',
            },
            {
                'title': 'Webinar: Finanzas Personales',
                'description': 'Cómo gestionar tus finanzas personales y del negocio',
                'event_type': 'webinar',
                'start_date': now + timedelta(days=10, hours=19),
                'end_date': now + timedelta(days=10, hours=20, minutes=30),
                'location': 'https://zoom.us/j/123456789',
                'is_virtual': True,
                'max_participants': 100,
                'organizer_id': 'organizer-1',
            },
            {
                'title': 'Networking: Encuentro de Emprendedores',
                'description': 'Conecta con otros emprendedores y comparte experiencias',
                'event_type': 'networking',
                'start_date': now + timedelta(days=14, hours=18),
                'end_date': now + timedelta(days=14, hours=20),
                'location': 'Café Emprendedor, El Alto',
                'is_virtual': False,
                'max_participants': 20,
                'organizer_id': 'organizer-1',
            },
            {
                'title': 'Bootcamp: Pitch Perfecto',
                'description': 'Aprende a presentar tu negocio de manera efectiva',
                'event_type': 'workshop',
                'start_date': now + timedelta(days=21, hours=9),
                'end_date': now + timedelta(days=21, hours=17),
                'location': 'Centro de Innovación, La Paz',
                'is_virtual': False,
                'max_participants': 15,
                'organizer_id': 'organizer-1',
            },
        ]
        
        for data in events_data:
            event = Event(id=str(uuid.uuid4()), **data)
            db.session.add(event)
            print(f"  ✓ {event.title}")
        
        db.session.commit()
        print("\n✅ Datos de calendario insertados exitosamente!")

if __name__ == '__main__':
    print("=" * 70)
    print("CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 70)
    print()
    
    create_tables()
    seed_data()
    seed_community_posts()
    seed_achievements()
    seed_calendar_data()
    
    print()
    print("=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    
    with app.app_context():
        total_courses = LearningCourse.query.count()
        pre = LearningCourse.query.filter_by(route_type='pre').count()
        inc = LearningCourse.query.filter_by(route_type='inc').count()
        sections = LearningSection.query.count()
        posts = CommunityPost.query.count()
        comments = CommunityComment.query.count()
        likes = CommunityLike.query.count()
        achievements = Achievement.query.count()
        availability = MentorAvailability.query.count()
        events = Event.query.count()
        
        print(f"\n📊 Resumen:")
        print(f"  📚 Total cursos: {total_courses}")
        print(f"  📗 Pre-incubadora: {pre} cursos")
        print(f"  📘 Incubadora: {inc} cursos")
        print(f"  📝 Secciones: {sections}")
        print(f"  💬 Posts de comunidad: {posts}")
        print(f"  💬 Comentarios: {comments}")
        print(f"  ❤️  Likes: {likes}")
        print(f"  🏆 Logros disponibles: {achievements}")
        print(f"  📅 Disponibilidades de mentor: {availability}")
        print(f"  🎉 Eventos: {events}")
        print()
        print("🚀 Siguiente paso: python run.py")
        print("   Luego visita: http://localhost:5000/api/learning/health")

