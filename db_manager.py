import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'panda.db')

def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_base_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # 1. Tabla de Carreras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carreras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            codigo TEXT
        )
    """)
    
    # 2. Tabla maestra de Asignaturas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignaturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    """)
    
    # 3. Tabla intermedia (Relación Carrera <-> Asignatura con toda la info institucional)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carrera_asignatura (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrera_id INTEGER,
            asignatura_id INTEGER,
            codigo_asignatura TEXT,
            area TEXT,
            departamento TEXT,
            dictado TEXT,
            director_area TEXT,
            responsable_asignatura TEXT,
            tipo_asignatura TEXT,
            ubicacion_ciclo TEXT,
            contenidos_basicos TEXT,
            alcances_plan TEXT,
            FOREIGN KEY(carrera_id) REFERENCES carreras(id),
            FOREIGN KEY(asignatura_id) REFERENCES asignaturas(id)
        )
    """)
    
    # 4. Tabla principal del Programa Analítico (PUPA/PANDA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programas_analiticos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignatura TEXT NOT NULL,
            carreras_aplicadas TEXT,
            horas_teoricas REAL,
            horas_p1 REAL,
            horas_p2 REAL,
            horas_p3 REAL,
            horas_otras REAL,
            detalle_otros TEXT,
            modalidad_virtual TEXT,
            porcentaje_mixto TEXT,
            espacios_consulta TEXT,
            fund_31 TEXT,
            fund_32 TEXT,
            fund_33 TEXT,
            fund_34 TEXT,
            fund_35 TEXT,
            art_42 TEXT,
            art_43 TEXT,
            art_44 TEXT,
            art_45 TEXT,
            otros_criterios TEXT,
            desc_actividades_obligatorias TEXT,
            asistencia_req TEXT,
            aprobacion_req TEXT,
            cantidad_parciales INTEGER,
            eval_sumativas TEXT,
            eval_promocion TEXT,
            calif_promocion TEXT,
            final_reg_mod TEXT,
            final_reg_cont TEXT,
            final_reg_crit TEXT,
            final_lib_mod TEXT,
            final_lib_crit TEXT,
            bib_obligatoria TEXT,
            bib_complementaria TEXT,
            programas_especiales TEXT,
            desc_programas TEXT,
            conformidad INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Unidades dinámicas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unidades_programa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programa_id INTEGER,
            numero_unidad INTEGER,
            nombre_unidad TEXT,
            conceptos TEXT,
            trabajos_practicos TEXT,
            practica_p1 INTEGER,
            practica_p2 INTEGER,
            practica_p3 INTEGER,
            FOREIGN KEY(programa_id) REFERENCES programas_analiticos(id)
        )
    """)

    conexion.commit()
    conexion.close()