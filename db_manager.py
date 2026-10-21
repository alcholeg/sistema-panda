import sqlite3
import os
import pandas as pd

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

    # --- CARGA AUTOMÁTICA Y FORZADA DEL EXCEL ---
    cursor.execute("SELECT COUNT(*) FROM asignaturas")
    count = cursor.fetchone()[0]

    # Si está vacía, leemos el Excel
    if count == 0:
        base_dir = os.path.dirname(__file__)
        excel_path = os.path.join(base_dir, 'materias_institucionales.xlsx')

        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                
                # Normalizamos las columnas a minúsculas y sin espacios
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                for _, row in df.iterrows():
                    nombre_carrera = row.get('carrera') or row.get('carreras') or 'Carrera General'
                    # AQUÍ ESTABA EL CAMBIO CLAVE: Usamos 'nombre_asignatura' que es como se llama en tu Excel
                    nombre_asignatura = row.get('nombre_asignatura') or row.get('asignatura') or row.get('materia') or ''
                    
                    if not nombre_asignatura or pd.isna(nombre_asignatura):
                        continue
                    
                    # 1. Insertar o recuperar Carrera
                    cursor.execute("INSERT OR IGNORE INTO carreras (nombre) VALUES (?)", (str(nombre_carrera).strip(),))
                    cursor.execute("SELECT id FROM carreras WHERE nombre = ?", (str(nombre_carrera).strip(),))
                    carrera_id = cursor.fetchone()[0]
                    
                    # 2. Insertar o recuperar Asignatura
                    cursor.execute("INSERT OR IGNORE INTO asignaturas (nombre) VALUES (?)", (str(nombre_asignatura).strip(),))
                    cursor.execute("SELECT id FROM asignaturas WHERE nombre = ?", (str(nombre_asignatura).strip(),))
                    asignatura_id = cursor.fetchone()[0]
                    
                    # 3. Insertar relación y datos institucionales
                    cursor.execute("""
                        INSERT INTO carrera_asignatura (
                            carrera_id, asignatura_id, codigo_asignatura, area, departamento, 
                            dictado, director_area, responsable_asignatura, tipo_asignatura, 
                            ubicacion_ciclo, contenidos_basicos, alcances_plan
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        carrera_id,
                        asignatura_id,
                        str(row.get('codigo_asignatura', row.get('codigo', ''))),
                        str(row.get('area', '')),
                        str(row.get('departamento', '')),
                        str(row.get('dictado', '')),
                        str(row.get('director_area', row.get('director', ''))),
                        str(row.get('responsable_asignatura', row.get('responsable', ''))),
                        str(row.get('tipo_asignatura', row.get('tipo', ''))),
                        str(row.get('ubicacion_ciclo', row.get('ciclo', ''))),
                        str(row.get('contenidos_basicos', row.get('contenidos', ''))),
                        str(row.get('alcances_plan', row.get('alcances', '')))
                    ))
                conexion.commit()
            except Exception as e:
                print(f"Error procesando el Excel: {e}")

    conexion.close()