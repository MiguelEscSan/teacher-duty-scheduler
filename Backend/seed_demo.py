"""
Script de población de datos (Data Seeder) con GUIDs y Departamentos.
Ejecutar desde la carpeta Backend:
    python seed_demo.py
"""
import sys
import uuid
from pathlib import Path

# Asegurar que el directorio Backend esté en el sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from sqlmodel import Session, select
from src.infrastructure.db.config import engine, init_db
from src.infrastructure.db.models import AbsenceDB, BaseScheduleDB, TeacherDB


def seed():
    print("[*] Conectando con la base de datos...")
    init_db()

    with Session(engine) as session:
        # 1. Limpieza de datos existentes
        for a in session.exec(select(AbsenceDB)).all():
            session.delete(a)
        for s in session.exec(select(BaseScheduleDB)).all():
            session.delete(s)
        for t in session.exec(select(TeacherDB)).all():
            session.delete(t)
        session.commit()
        print("[✓] Base de datos reinicializada y limpia.")

        # 2. Definición del claustro con GUIDs automáticos y Departamentos
        teachers_data = [
            ("ana", "Ana García Pérez", "Matemáticas"),
            ("carlos", "Carlos López Martín", "Lengua Castellana y Literatura"),
            ("eva", "Eva Rodríguez Silva", "Inglés / Idiomas"),
            ("david", "David Sánchez Gómez", "Ciencias Naturales / Física y Química"),
            ("lucia", "Lucía Fernández Ruiz", "Geografía e Historia"),
            ("mario", "Mario Ruiz Morales", "Educación Física"),
            ("elena", "Elena Navarro Vega", "Música"),
            ("alberto", "Alberto Romero Soto", "Tecnología e Informática"),
            ("sofia", "Sofía Torres Gil", "Filosofía"),
            ("pablo", "Pablo Jiménez Cano", "Artes Plásticas y Dibujo"),
        ]

        # Mapeo de alias local -> TeacherDB (con su GUID generado)
        t_map: dict[str, TeacherDB] = {}
        for alias, name, department in teachers_data:
            teacher_guid = str(uuid.uuid4())
            teacher_obj = TeacherDB(id=teacher_guid, name=name, department=department)
            session.add(teacher_obj)
            t_map[alias] = teacher_obj

        session.commit()
        print(f"[+] {len(t_map)} profesores registrados con GUIDs únicos y departamentos.")

        # 3. Horario Lectivo Base (Clases fijas)
        # day: 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes
        # period: 0 a 5
        base_teaching_slots = [
            # Ana (Matemáticas) - Jefa de estudios: alta docencia (4 horas diarias)
            ("ana", 0, 0), ("ana", 0, 1), ("ana", 0, 3), ("ana", 0, 4),
            ("ana", 1, 1), ("ana", 1, 2), ("ana", 1, 4), ("ana", 1, 5),
            ("ana", 2, 0), ("ana", 2, 1), ("ana", 2, 2), ("ana", 2, 3),
            ("ana", 3, 0), ("ana", 3, 2), ("ana", 3, 3), ("ana", 3, 5),
            ("ana", 4, 1), ("ana", 4, 2), ("ana", 4, 4), ("ana", 4, 5),

            # Carlos (Lengua) - Clases estándar
            ("carlos", 0, 2), ("carlos", 0, 3), ("carlos", 1, 0), ("carlos", 1, 1),
            ("carlos", 2, 4), ("carlos", 2, 5), ("carlos", 3, 1), ("carlos", 3, 2),
            ("carlos", 4, 0), ("carlos", 4, 1),

            # Eva (Inglés) - Primeras horas
            ("eva", 0, 0), ("eva", 1, 0), ("eva", 2, 0), ("eva", 3, 0), ("eva", 4, 0),
            ("eva", 0, 1), ("eva", 1, 1),

            # David (Ciencias) - Horas intermedias
            ("david", 0, 2), ("david", 1, 2), ("david", 2, 2), ("david", 3, 2), ("david", 4, 2),
            ("david", 0, 3), ("david", 2, 3),

            # Lucía (Historia) - Tardes ocupadas (P4 y P5)
            ("lucia", 0, 4), ("lucia", 0, 5), ("lucia", 1, 4), ("lucia", 1, 5),
            ("lucia", 2, 4), ("lucia", 2, 5), ("lucia", 3, 4), ("lucia", 3, 5),

            # Mario (Ed. Física) - Clases prácticas agrupadas
            ("mario", 0, 1), ("mario", 0, 2), ("mario", 2, 1), ("mario", 2, 2),
            ("mario", 4, 3), ("mario", 4, 4),

            # Elena (Música) y Alberto (Tecnología)
            ("elena", 1, 3), ("elena", 1, 4), ("elena", 3, 0), ("elena", 3, 1),
            ("alberto", 0, 5), ("alberto", 2, 5), ("alberto", 4, 5),

            # Forzar cuello de botella en Viernes P5 (13:00-14:00):
            # Ocupamos con clase a casi todos para poner a prueba la subcobertura
            ("eva", 4, 5), ("david", 4, 5), ("mario", 4, 5), ("elena", 4, 5),
        ]

        for alias, day, period in base_teaching_slots:
            session.add(BaseScheduleDB(
                teacher_id=t_map[alias].id,  # Vinculado al GUID
                day=day,
                period=period,
                status="TEACHING"
            ))

        session.commit()
        print(f"[+] {len(base_teaching_slots)} clases lectivas base registradas.")

        # 4. Ausencias puntuales para la semana del 21 al 25 de septiembre de 2026
        absences = [
            # Consulta médica de David el lunes 21
            AbsenceDB(
                teacher_id=t_map["david"].id,
                date="2026-09-21",
                period=1,
                reason="Consulta médica especialista"
            ),

            # Permiso por deber inexcusable para Elena el martes 22 (primeras horas)
            AbsenceDB(
                teacher_id=t_map["elena"].id,
                date="2026-09-22",
                period=0,
                reason="Mesa electoral / Trámite legal"
            ),
            AbsenceDB(
                teacher_id=t_map["elena"].id,
                date="2026-09-22",
                period=1,
                reason="Mesa electoral / Trámite legal"
            ),
            AbsenceDB(
                teacher_id=t_map["elena"].id,
                date="2026-09-22",
                period=2,
                reason="Mesa electoral / Trámite legal"
            ),

            # Baja médica de 2 días de Carlos (Miércoles 23 y Jueves 24 al completo)
            *[
                AbsenceDB(
                    teacher_id=t_map["carlos"].id,
                    date="2026-09-23",
                    period=p,
                    reason="Baja médica (Gripe)"
                )
                for p in range(6)
            ],
            *[
                AbsenceDB(
                    teacher_id=t_map["carlos"].id,
                    date="2026-09-24",
                    period=p,
                    reason="Baja médica (Gripe)"
                )
                for p in range(6)
            ],

            # Permiso de Pablo el viernes 25 a última hora (P5):
            # Provoca que SOLO quede Sofía disponible en Viernes P5 -> Disparará el aviso de Déficit de 1
            AbsenceDB(
                teacher_id=t_map["pablo"].id,
                date="2026-09-25",
                period=5,
                reason="Asunto propio justificado"
            ),
        ]

        session.add_all(absences)
        session.commit()
        print(f"[+] {len(absences)} ausencias puntuales registradas para la semana del 21/09/2026.")

        print("\n" + "=" * 55)
        print(" [✓] Datos de demostración listos para probar")
        print("=" * 55)
        for alias, t in t_map.items():
            print(f" • {t.name:<32} [{t.department:<32}] -> GUID: {t.id}")
        print("=" * 55)


if __name__ == "__main__":
    seed()