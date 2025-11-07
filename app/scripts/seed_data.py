"""
Script para poblar la base de datos con datos iniciales.
"""
from datetime import datetime, date, time, timedelta
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
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
        admin = usuario_sistema_repo.obtener_por_email("admin@clinica.cl")
        if not admin:
            admin = UsuarioSistema(
                id=uuid4(),
                email="admin@clinica.cl",
                password_hash=hash_password("admin123"),
                rol="admin",
                activo=True
            )
            try:
                admin = usuario_sistema_repo.crear(admin)
                print(f"✓ Admin creado: {admin.email}")
            except IntegrityError:
                db.rollback()
                admin = usuario_sistema_repo.obtener_por_email("admin@clinica.cl")
                print(f"ℹ Admin ya existe: {admin.email}")
        else:
            print(f"ℹ Admin ya existe: {admin.email}")

        # Recepción
        recepcion = usuario_sistema_repo.obtener_por_email("recepcion@clinica.cl")
        if not recepcion:
            recepcion = UsuarioSistema(
                id=uuid4(),
                email="recepcion@clinica.cl",
                password_hash=hash_password("recepcion123"),
                rol="recepcion",
                activo=True
            )
            try:
                recepcion = usuario_sistema_repo.crear(recepcion)
                print(f"✓ Recepción creada: {recepcion.email}")
            except IntegrityError:
                db.rollback()
                recepcion = usuario_sistema_repo.obtener_por_email("recepcion@clinica.cl")
                print(f"ℹ Recepción ya existe: {recepcion.email}")
        else:
            print(f"ℹ Recepción ya existe: {recepcion.email}")

        # === PROFESIONALES ===
        print("\nCreando profesionales...")

        # Verificar si ya existe el profesional por nombre
        profesionales_existentes = profesional_repo.listar(activo=True)
        prof1 = next((p for p in profesionales_existentes if p.nombre == "Dr. Juan Pérez"), None)

        if not prof1:
            prof1 = Profesional(
                id=uuid4(),
                nombre="Dr. Juan Pérez",
                profesion="Kinesiólogo",
                activo=True
            )
            try:
                prof1 = profesional_repo.crear(prof1)
                print(f"✓ Profesional creado: {prof1.nombre}")
            except IntegrityError:
                db.rollback()
                profesionales_existentes = profesional_repo.listar(activo=True)
                prof1 = next((p for p in profesionales_existentes if p.nombre == "Dr. Juan Pérez"), None)
                print(f"ℹ Profesional ya existe: {prof1.nombre}")
        else:
            print(f"ℹ Profesional ya existe: {prof1.nombre}")

        prof2 = next((p for p in profesionales_existentes if p.nombre == "Dra. María González"), None)

        if not prof2:
            prof2 = Profesional(
                id=uuid4(),
                nombre="Dra. María González",
                profesion="Fonoaudióloga",
                activo=True
            )
            try:
                prof2 = profesional_repo.crear(prof2)
                print(f"✓ Profesional creado: {prof2.nombre}")
            except IntegrityError:
                db.rollback()
                profesionales_existentes = profesional_repo.listar(activo=True)
                prof2 = next((p for p in profesionales_existentes if p.nombre == "Dra. María González"), None)
                print(f"ℹ Profesional ya existe: {prof2.nombre}")
        else:
            print(f"ℹ Profesional ya existe: {prof2.nombre}")

        # Usuario sistema para profesional
        prof_user = usuario_sistema_repo.obtener_por_email("juan.perez@clinica.cl")
        if not prof_user:
            prof_user = UsuarioSistema(
                id=uuid4(),
                email="juan.perez@clinica.cl",
                password_hash=hash_password("prof123"),
                rol="profesional",
                activo=True,
                profesional_id=prof1.id
            )
            try:
                prof_user = usuario_sistema_repo.crear(prof_user)
                print(f"✓ Usuario profesional: {prof_user.email}")
            except IntegrityError:
                db.rollback()
                prof_user = usuario_sistema_repo.obtener_por_email("juan.perez@clinica.cl")
                print(f"ℹ Usuario profesional ya existe: {prof_user.email}")
        else:
            print(f"ℹ Usuario profesional ya existe: {prof_user.email}")

        # === BOXES ===
        print("\nCreando boxes...")

        boxes_existentes = box_repo.listar(activo=True)

        boxes_data = [
            {
                "nombre": "Box 1",
                "ubicacion": "Piso 1, Ala Norte",
                "piso": 1,
                "capacidad": 2,
                "equipamiento": '{"camilla": true, "escritorio": true, "silla": true}',
                "caracteristicas": '{"accesible": true, "ventana": true}'
            },
            {
                "nombre": "Box 2",
                "ubicacion": "Piso 1, Ala Sur",
                "piso": 1,
                "capacidad": 1,
                "equipamiento": '{"camilla": true, "escritorio": true}',
                "caracteristicas": '{"accesible": false, "ventana": false}'
            },
            {
                "nombre": "Box 3",
                "ubicacion": "Piso 2, Ala Norte",
                "piso": 2,
                "capacidad": 1,
                "equipamiento": '{"camilla": true, "escritorio": true, "silla": true, "equipos_especiales": true}',
                "caracteristicas": '{"accesible": true, "ventana": true, "silencioso": true}'
            },
            {
                "nombre": "Box 4",
                "ubicacion": "Piso 2, Ala Sur",
                "piso": 2,
                "capacidad": 2,
                "equipamiento": '{"camilla": true, "escritorio": true, "silla": true}',
                "caracteristicas": '{"accesible": false, "ventana": true}'
            }
        ]

        for box_data in boxes_data:
            box_existente = next((b for b in boxes_existentes if b.nombre == box_data["nombre"]), None)
            if not box_existente:
                box = Box(
                    id=uuid4(),
                    nombre=box_data["nombre"],
                    ubicacion=box_data["ubicacion"],
                    piso=box_data["piso"],
                    capacidad=box_data["capacidad"],
                    equipamiento=box_data["equipamiento"],
                    caracteristicas=box_data["caracteristicas"],
                    activo=True
                )
                try:
                    box = box_repo.crear(box)
                    print(f"✓ Box creado: {box.nombre} (Piso {box.piso})")
                except IntegrityError:
                    db.rollback()
                    print(f"ℹ Box ya existe: {box_data['nombre']}")
            else:
                print(f"ℹ Box ya existe: {box_existente.nombre}")

        # === PRESTACIONES ===
        print("\nCreando prestaciones...")

        prestaciones_existentes = prestacion_repo.listar(habilitada=True)

        prestaciones_data = [
            {
                "nombre": "Kinesiología Respiratoria",
                "duracion_minutos": 45,
                "periodicidad_dias": 30,
                "tolerancia_dias": 7
            },
            {
                "nombre": "Fonoaudiología",
                "duracion_minutos": 45,
                "periodicidad_dias": 15,
                "tolerancia_dias": 5
            },
            {
                "nombre": "Terapia Ocupacional",
                "duracion_minutos": 60,
                "periodicidad_dias": 7,
                "tolerancia_dias": 2
            }
        ]

        for prest_data in prestaciones_data:
            prest_existente = next((p for p in prestaciones_existentes if p.nombre == prest_data["nombre"]), None)
            if not prest_existente:
                prest = Prestacion(
                    id=uuid4(),
                    nombre=prest_data["nombre"],
                    duracion_minutos=prest_data["duracion_minutos"],
                    periodicidad_dias=prest_data["periodicidad_dias"],
                    tolerancia_dias=prest_data["tolerancia_dias"],
                    habilitada=True
                )
                try:
                    prest = prestacion_repo.crear(prest)
                    print(f"✓ Prestación creada: {prest.nombre}")
                except IntegrityError:
                    db.rollback()
                    print(f"ℹ Prestación ya existe: {prest_data['nombre']}")
            else:
                print(f"ℹ Prestación ya existe: {prest_existente.nombre}")

        # === USUARIOS (PACIENTES) ===
        print("\nCreando usuarios (pacientes)...")

        usuarios_existentes = usuario_repo.listar(activo=True)

        usuarios_data = [
            {
                "rut": "12345678-5",
                "nombre": "Pedro Sánchez",
                "fecha_nacimiento": date(1980, 5, 15),
                "nivel_apoyo": 1
            },
            {
                "rut": "13456789-9",
                "nombre": "Ana Martínez",
                "fecha_nacimiento": date(1995, 8, 22),
                "nivel_apoyo": 2
            },
            {
                "rut": "11111111-1",
                "nombre": "Carlos López",
                "fecha_nacimiento": date(1970, 3, 10),
                "nivel_apoyo": 3
            }
        ]

        for user_data in usuarios_data:
            user_existente = next((u for u in usuarios_existentes if u.rut.valor == user_data["rut"]), None)
            if not user_existente:
                user = Usuario(
                    id=uuid4(),
                    rut=RUT(user_data["rut"]),
                    nombre=user_data["nombre"],
                    fecha_nacimiento=user_data["fecha_nacimiento"],
                    nivel_apoyo=user_data["nivel_apoyo"],
                    activo=True
                )
                try:
                    user = usuario_repo.crear(user)
                    print(f"✓ Usuario creado: {user.nombre} ({user.rut.valor})")
                except IntegrityError:
                    db.rollback()
                    print(f"ℹ Usuario ya existe: {user_data['nombre']}")
            else:
                print(f"ℹ Usuario ya existe: {user_existente.nombre} ({user_existente.rut.valor})")

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
