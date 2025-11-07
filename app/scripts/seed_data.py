"""
Script para poblar la base de datos con datos iniciales.
"""
from datetime import datetime, date, time, timedelta
from uuid import uuid4
from app.infraestructura.db.database import get_db_context, init_db
from app.infraestructura.seguridad.hashing import hash_password
from app.dominio.entidades import (
    Usuario, Profesional, Box, Prestacion, UsuarioSistema
)
from app.dominio.valores import RUT
from app.infraestructura.repos.usuario_repo import UsuarioRepo
from app.infraestructura.repos.profesional_repo import ProfesionalRepo
from app.infraestructura.repos.box_repo import BoxRepo
from app.infraestructura.repos.prestacion_repo import PrestacionRepo
from app.infraestructura.repos.usuario_sistema_repo import UsuarioSistemaRepo


def seed():
    """Poblar base de datos con datos iniciales"""
    print("Iniciando seed de datos...")

    # Inicializar BD (crear tablas si no existen - solo en desarrollo)
    init_db()
    print("Tablas creadas/verificadas")

    with get_db_context() as db:
        # Repositorios
        usuario_repo = UsuarioRepo(db)
        profesional_repo = ProfesionalRepo(db)
        box_repo = BoxRepo(db)
        prestacion_repo = PrestacionRepo(db)
        usuario_sistema_repo = UsuarioSistemaRepo(db)

        # === USUARIOS DEL SISTEMA ===
        print("\nCreando usuarios del sistema...")

        # Admin
        admin = UsuarioSistema(
            id=uuid4(),
            email="admin@clinica.cl",
            password_hash=hash_password("admin123"),
            rol="admin",
            activo=True
        )
        admin = usuario_sistema_repo.crear(admin)
        print(f"✓ Admin creado: {admin.email}")

        # Recepción
        recepcion = UsuarioSistema(
            id=uuid4(),
            email="recepcion@clinica.cl",
            password_hash=hash_password("recepcion123"),
            rol="recepcion",
            activo=True
        )
        recepcion = usuario_sistema_repo.crear(recepcion)
        print(f"✓ Recepción creada: {recepcion.email}")

        # === PROFESIONALES ===
        print("\nCreando profesionales...")

        prof1 = Profesional(
            id=uuid4(),
            nombre="Dr. Juan Pérez",
            profesion="Kinesiólogo",
            activo=True
        )
        prof1 = profesional_repo.crear(prof1)
        print(f"✓ Profesional creado: {prof1.nombre}")

        prof2 = Profesional(
            id=uuid4(),
            nombre="Dra. María González",
            profesion="Fonoaudióloga",
            activo=True
        )
        prof2 = profesional_repo.crear(prof2)
        print(f"✓ Profesional creado: {prof2.nombre}")

        # Usuario sistema para profesional
        prof_user = UsuarioSistema(
            id=uuid4(),
            email="juan.perez@clinica.cl",
            password_hash=hash_password("prof123"),
            rol="profesional",
            activo=True,
            profesional_id=prof1.id
        )
        prof_user = usuario_sistema_repo.crear(prof_user)
        print(f"✓ Usuario profesional: {prof_user.email}")

        # === BOXES ===
        print("\nCreando boxes...")

        box1 = Box(
            id=uuid4(),
            nombre="Box 1",
            ubicacion="Piso 1, Ala Norte",
            activo=True
        )
        box1 = box_repo.crear(box1)
        print(f"✓ Box creado: {box1.nombre}")

        box2 = Box(
            id=uuid4(),
            nombre="Box 2",
            ubicacion="Piso 1, Ala Sur",
            activo=True
        )
        box2 = box_repo.crear(box2)
        print(f"✓ Box creado: {box2.nombre}")

        box3 = Box(
            id=uuid4(),
            nombre="Box 3",
            ubicacion="Piso 2, Ala Norte",
            activo=True
        )
        box3 = box_repo.crear(box3)
        print(f"✓ Box creado: {box3.nombre}")

        # === PRESTACIONES ===
        print("\nCreando prestaciones...")

        prest1 = Prestacion(
            id=uuid4(),
            nombre="Kinesiología Respiratoria",
            duracion_minutos=45,
            periodicidad_dias=30,
            tolerancia_dias=7,
            habilitada=True
        )
        prest1 = prestacion_repo.crear(prest1)
        print(f"✓ Prestación creada: {prest1.nombre}")

        prest2 = Prestacion(
            id=uuid4(),
            nombre="Fonoaudiología",
            duracion_minutos=45,
            periodicidad_dias=15,
            tolerancia_dias=5,
            habilitada=True
        )
        prest2 = prestacion_repo.crear(prest2)
        print(f"✓ Prestación creada: {prest2.nombre}")

        prest3 = Prestacion(
            id=uuid4(),
            nombre="Terapia Ocupacional",
            duracion_minutos=60,
            periodicidad_dias=7,
            tolerancia_dias=2,
            habilitada=True
        )
        prest3 = prestacion_repo.crear(prest3)
        print(f"✓ Prestación creada: {prest3.nombre}")

        # === USUARIOS (PACIENTES) ===
        print("\nCreando usuarios (pacientes)...")

        user1 = Usuario(
            id=uuid4(),
            rut=RUT("12345678-5"),
            nombre="Pedro Sánchez",
            fecha_nacimiento=date(1980, 5, 15),
            nivel_apoyo=1,
            activo=True
        )
        user1 = usuario_repo.crear(user1)
        print(f"✓ Usuario creado: {user1.nombre} ({user1.rut.valor})")

        user2 = Usuario(
            id=uuid4(),
            rut=RUT("16432341-4"),
            nombre="Ana Martínez",
            fecha_nacimiento=date(1995, 8, 22),
            nivel_apoyo=2,
            activo=True
        )
        user2 = usuario_repo.crear(user2)
        print(f"✓ Usuario creado: {user2.nombre} ({user2.rut.valor})")

        user3 = Usuario(
            id=uuid4(),
            rut=RUT("18765432-3"),
            nombre="Carlos López",
            fecha_nacimiento=date(1970, 3, 10),
            nivel_apoyo=3,
            activo=True
        )
        user3 = usuario_repo.crear(user3)
        print(f"✓ Usuario creado: {user3.nombre} ({user3.rut.valor})")

    print("\n✅ Seed de datos completado exitosamente!")
    print("\n=== CREDENCIALES DE ACCESO ===")
    print("Admin:")
    print("  Email: admin@clinica.cl")
    print("  Password: admin123")
    print("\nRecepción:")
    print("  Email: recepcion@clinica.cl")
    print("  Password: recepcion123")
    print("\nProfesional:")
    print("  Email: juan.perez@clinica.cl")
    print("  Password: prof123")


if __name__ == "__main__":
    seed()
