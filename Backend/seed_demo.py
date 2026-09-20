"""
Script de población masiva (Seed) para el claustro de 58 profesores,
catálogo de grupos, horarios lectivos con co-docencia, guardias ordinarias
y listas de sustitución corta.

Ejecución desde la raíz de Backend:
    python seed_demo_58.py
"""
import random
import sys
import uuid
from pathlib import Path

# Añadir raíz de Backend al path
sys.path.append(str(Path(__file__).resolve().parent))

from sqlmodel import Session, select
from src.infrastructure.db.config import engine, init_db
from src.infrastructure.db.models import (
    AbsenceDB,
    FixedDutyDB,
    ShortTermSubstitutionDB,
    StudentGroupDB,
    SubstitutionLogDB,
    TeacherDB,
    TeacherScheduleDB,
)

# 1. Catálogo Oficial de Grupos y Aforos
GROUPS_DATA = [
    ("1ºA_ESO", 18),
    ("1ºB_ESO", 18),
    ("1ºC_ESO", 18),
    ("2ºA_ESO", 25),
    ("2ºB_ESO", 25),
    ("3ºA_ESO", 8),
    ("3ºB_ESO", 21),
    ("3ºC_ESO", 21),
    ("3ºMIXTO_ESO", None),
    ("4ºA_ESO", 12),
    ("4ºB_ESO", 24),
    ("4ºC_ESO", 24),
    ("4ºBC_ESO", None),
    ("1ºA_BACH", 17),
    ("1ºB_BACH", 17),
    ("1ºAyB_BACH", None),
    ("2ºA_BACH", 31),
]

# 2. 58 Profesores del Claustro distribuidos por Departamentos
TEACHERS_RAW = [
    # Matemáticas (7)
    ("García Pérez, Ana", "Matemáticas"),
    ("Martínez Soto, Carlos", "Matemáticas"),
    ("López Gómez, Eva", "Matemáticas"),
    ("Sánchez Ruiz, David", "Matemáticas"),
    ("Navarro Gil, Elena", "Matemáticas"),
    ("Fernández Torres, Lucía", "Matemáticas"),
    ("Jiménez Rivas, Alberto", "Matemáticas"),
    # Lengua Castellana y Literatura (8)
    ("Romero Morales, Alberto", "Lengua Castellana y Literatura"),
    ("Díaz Castro, Carmen", "Lengua Castellana y Literatura"),
    ("Torres Serrano, Sofía", "Lengua Castellana y Literatura"),
    ("Ruiz Vega, Mario", "Lengua Castellana y Literatura"),
    ("Alonso Peña, Marta", "Lengua Castellana y Literatura"),
    ("Gutiérrez Ortiz, Raúl", "Lengua Castellana y Literatura"),
    ("Moreno Campos, Irene", "Lengua Castellana y Literatura"),
    ("Vázquez Ramos, Sergio", "Lengua Castellana y Literatura"),
    # Inglés / Lenguas Extranjeras (7)
    ("Blanco Pardo, Laura", "Inglés / Idiomas"),
    ("Molina Molina, Jorge", "Inglés / Idiomas"),
    ("Ortega Cruz, Patricia", "Inglés / Idiomas"),
    ("Delgado Reyes, Daniel", "Inglés / Idiomas"),
    ("Castro Ibáñez, Paula", "Inglés / Idiomas"),
    ("Rubio Marín, Andrés", "Inglés / Idiomas"),
    ("Medina Gallego, Beatriz", "Inglés / Idiomas"),
    # Geografía e Historia (6)
    ("Suárez Vidal, Alejandro", "Geografía e Historia"),
    ("Castillo Marín, Nuria", "Geografía e Historia"),
    ("Iglesias Cano, Manuel", "Geografía e Historia"),
    ("Santos Herrera, Silvia", "Geografía e Historia"),
    ("Garrido Flores, Javier", "Geografía e Historia"),
    ("Peña Aguilar, Raquel", "Geografía e Historia"),
    # Biología y Geología (5)
    ("Calvo León, Marcos", "Biología y Geología"),
    ("Cabrera Domínguez, Cristina", "Biología y Geología"),
    ("Pérez Benítez, Gonzalo", "Biología y Geología"),
    ("Reyes Márquez, Natalia", "Biología y Geología"),
    ("Fuentes Santana, Víctor", "Biología y Geología"),
    # Física y Química (5)
    ("Aguilar Duran, Clara", "Física y Química"),
    ("Herrera Pascual, Pablo", "Física y Química"),
    ("Bravo Hidalgo, Lorena", "Física y Química"),
    ("Méndez Montero, Iván", "Física y Química"),
    ("Ríos Vicente, Isabel", "Física y Química"),
    # Educación Física (4)
    ("Campos Lorenzo, Roberto", "Educación Física"),
    ("Vega Arias, Sara", "Educación Física"),
    ("Guerrero Cruz, Diego", "Educación Física"),
    ("Carrasco Gil, Alicia", "Educación Física"),
    # Tecnología e Informática (5)
    ("Nieto Romero, Félix", "Tecnología e Informática"),
    ("Pascual Sáez, Celia", "Tecnología e Informática"),
    ("Ferrer Soler, Hugo", "Tecnología e Informática"),
    ("Vidal Mora, Teresa", "Tecnología e Informática"),
    ("Durán Giménez, Óscar", "Tecnología e Informática"),
    # Artes Plásticas y Dibujo (3)
    ("Arias Rojas, Marina", "Artes Plásticas y Dibujo"),
    ("Mora Esteban, Lucas", "Artes Plásticas y Dibujo"),
    ("Hidalgo Varela, Inés", "Artes Plásticas y Dibujo"),
    # Música (2)
    ("Santana Parra, Rubén", "Música"),
    ("Vargas Luque, Esther", "Música"),
    # Filosofía (2)
    ("Paredes Robles, Adrián", "Filosofía"),
    ("Cortes Lozano, Miriam", "Filosofía"),
    # Orientación Educativa (2)
    ("Lozano Medina, Rosa", "Orientación Educativa"),
    ("Bernal Bravo, Tomás", "Orientación Educativa"),
    # Francés / Alemán (2)
    ("Crespo Roldán, Diana", "Francés"),
    ("Salas Miranda, Héctor", "Alemán"),
]


def seed():
    # Fijar semilla pseudoaleatoria para reproducibilidad idéntica
    random.seed(42)

    init_db()

    with Session(engine) as session:
        print("[*] Limpiando tablas previas...")
        for table_model in [
            SubstitutionLogDB,
            FixedDutyDB,
            ShortTermSubstitutionDB,
            TeacherScheduleDB,
            AbsenceDB,
            StudentGroupDB,
            TeacherDB,
        ]:
            for item in session.exec(select(table_model)).all():
                session.delete(item)
        session.commit()
        print("[✓] Base de datos limpia.")

        # 1. Sembrar Catálogo de Grupos
        group_id_map: dict[str, str] = {}
        for g_name, g_count in GROUPS_DATA:
            group_obj = StudentGroupDB(
                id=str(uuid.uuid4()),
                name=g_name,
                student_count=g_count,
            )
            session.add(group_obj)
            group_id_map[g_name] = group_obj.id
        session.commit()
        print(f"[+] {len(group_id_map)} grupos creados con aforos asignados.")

        # 2. Sembrar los 58 Profesores
        teacher_objs: list[TeacherDB] = []
        for i, (name, dept) in enumerate(TEACHERS_RAW, start=1):
            # Email normalizado corporativo
            alias = (
                name.split(",")[0].strip().lower().replace(" ", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
            )
            email = f"{alias}{i}@centroeducativo.es"
            t = TeacherDB(
                id=str(uuid.uuid4()),
                name=name,
                email=email,
                department=dept,
            )
            session.add(t)
            teacher_objs.append(t)
        session.commit()
        print(f"[+] {len(teacher_objs)} profesores registrados con GUID y correo institucional.")

        # 3. Asignación Semanal de Horarios, Guardias y Sustitución Corta
        group_names = list(group_id_map.keys())

        # Estructura para registrar asignaciones de aula por franja y evitar colisiones
        # (day, period, group_id) -> lista de teacher_ids
        classroom_assignments: dict[tuple[int, int, str], list[str]] = {}

        # Mapeo de slots ocupados por profesor: teacher_id -> set((day, period))
        teacher_busy_slots: dict[str, set[tuple[int, int]]] = {t.id: set() for t in teacher_objs}

        # A) Clases lectivas: cada profesor imparte entre 18 y 21 horas de clase a la semana
        print("[*] Generando horarios lectivos y escenarios de co-docencia...")
        for t in teacher_objs:
            target_teaching_hours = random.randint(18, 21)
            assigned_hours = 0

            # Todas las 30 franjas de la semana
            all_slots = [(d, p) for d in range(5) for p in range(6)]
            random.shuffle(all_slots)

            for d, p in all_slots:
                if assigned_hours >= target_teaching_hours:
                    break

                # Comprobar que el profesor no esté ocupado en ese slot
                if (d, p) in teacher_busy_slots[t.id]:
                    continue

                # Seleccionar un grupo que no tenga ya docencia en ese periodo
                available_groups = [
                    g_name for g_name in group_names
                    if (d, p, group_id_map[g_name]) not in classroom_assignments
                ]

                if not available_groups:
                    continue

                chosen_group_name = random.choice(available_groups)
                g_id = group_id_map[chosen_group_name]

                # Registrar docencia
                session.add(TeacherScheduleDB(
                    teacher_id=t.id,
                    day_of_week=d,
                    period=p,
                    group_id=g_id,
                    is_teaching=True,
                ))
                teacher_busy_slots[t.id].add((d, p))
                classroom_assignments[(d, p, g_id)] = [t.id]
                assigned_hours += 1

        # B) Inserción intencionada de Co-Docencia (Asignaturas compartidas / Desdobles)
        # Ejemplo: Lunes P2 en "1ºA_ESO" y Miércoles P3 en "3ºMIXTO_ESO" con 2 docentes titulares
        co_teaching_cases = [
            (0, 2, "1ºA_ESO", teacher_objs[0], teacher_objs[1]),  # Ana García y Carlos Martínez en 1ºA_ESO
            (2, 3, "3ºMIXTO_ESO", teacher_objs[2], teacher_objs[3]), # Eva López y David Sánchez en 3ºMixto
        ]

        for d, p, g_name, t1, t2 in co_teaching_cases:
            g_id = group_id_map[g_name]
            # Asegurar que ambos tengan el registro para ese grupo
            for t_doc in (t1, t2):
                existing = session.exec(
                    select(TeacherScheduleDB).where(
                        TeacherScheduleDB.teacher_id == t_doc.id,
                        TeacherScheduleDB.day_of_week == d,
                        TeacherScheduleDB.period == p,
                    )
                ).first()
                if existing:
                    existing.group_id = g_id
                    existing.is_teaching = True
                    session.add(existing)
                else:
                    session.add(TeacherScheduleDB(
                        teacher_id=t_doc.id,
                        day_of_week=d,
                        period=p,
                        group_id=g_id,
                        is_teaching=True,
                    ))
                teacher_busy_slots[t_doc.id].add((d, p))
            classroom_assignments[(d, p, g_id)] = [t1.id, t2.id]

        session.commit()
        print("[✓] Horarios lectivos y casos de co-docencia consolidados.")

        # C) Asignación de Guardias Ordinarias Fijas (FixedDutyDB) y Sustitución Corta (ShortTermSubstitutionDB)
        # Para cada franja (5 días x 6 periodos = 30 franjas):
        # - 3 a 5 profesores en guardia ordinaria fija (al menos 1 retén en sala de profesores).
        # - 2 a 3 profesores designados para sustitución corta.
        fixed_duty_count = 0
        short_sub_count = 0

        for d in range(5):
            for p in range(6):
                # Profesores totalmente libres en esta franja
                free_teachers = [t for t in teacher_objs if (d, p) not in teacher_busy_slots[t.id]]
                random.shuffle(free_teachers)

                # Tomar entre 3 y 5 para guardia ordinaria
                n_fixed = min(len(free_teachers), random.randint(3, 5))
                fixed_assigned = free_teachers[:n_fixed]

                for t_fixed in fixed_assigned:
                    session.add(FixedDutyDB(
                        teacher_id=t_fixed.id,
                        day_of_week=d,
                        period=p,
                    ))
                    # Añadir al horario como no lectivo (guardia)
                    session.add(TeacherScheduleDB(
                        teacher_id=t_fixed.id,
                        day_of_week=d,
                        period=p,
                        group_id=None,
                        is_teaching=False,
                    ))
                    fixed_duty_count += 1

                # De los restantes libres, tomar 2 o 3 para la lista de sustitución corta
                remaining_free = free_teachers[n_fixed:]
                n_short = min(len(remaining_free), random.randint(2, 3))
                short_assigned = remaining_free[:n_short]

                for t_short in short_assigned:
                    session.add(ShortTermSubstitutionDB(
                        teacher_id=t_short.id,
                        day_of_week=d,
                        period=p,
                    ))
                    short_sub_count += 1

        session.commit()
        print(f"[+] {fixed_duty_count} asignaciones de guardia fija ordinaria creadas.")
        print(f"[+] {short_sub_count} asignaciones a listas de sustitución corta creadas.")

        # 4. Caso de Demostración Operativa: Baja médica completa del profesor Carlos Martínez (índice 1)
        # para el lunes 21 de septiembre de 2026 (2026-09-21)
        carlos = teacher_objs[1]
        demo_date = "2026-09-21"

        # Registrar la ausencia en los periodos donde tiene clase
        carlos_monday_slots = session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.teacher_id == carlos.id,
                TeacherScheduleDB.day_of_week == 0,
                TeacherScheduleDB.group_id.is_not(None),
            )
        ).all()

        for slot in carlos_monday_slots:
            session.add(AbsenceDB(
                teacher_id=carlos.id,
                date=demo_date,
                period=slot.period,
                reason="Baja médica imprevista (Gripe)",
            ))

        session.commit()
        print(f"[✓] Ausencia médica de prueba registrada para {carlos.name} el {demo_date}.")

        print("\n" + "=" * 65)
        print(" [✓] PROCESO DE SEED COMPLETADO CON ÉXITO")
        print("=" * 65)
        print(f" • Total Docentes:       {len(teacher_objs)}")
        print(f" • Total Grupos:         {len(group_id_map)}")
        print(f" • Co-docencia activa:   Lunes P2 (1ºA_ESO) y Miércoles P3 (3ºMIXTO_ESO)")
        print(f" • Profesor para test:   {carlos.name} (GUID: {carlos.id})")
        print("=" * 65)


if __name__ == "__main__":
    seed()