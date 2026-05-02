from app import app
from database import db, Usuario

with app.app_context():
    db.create_all()
    # Crear usuario admin por defecto si no existe
    if not Usuario.query.filter_by(username="admin").first():
        admin = Usuario(username="admin", rol="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin creado: usuario=admin, password=admin123")
    else:
        print("Admin ya existe.")