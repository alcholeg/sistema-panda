import pandas as pd
import sys
import os

# Agregamos la ruta de database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'database')))
from db_manager import obtener_conexion, inicializar_base_datos

def importar_excel_institucional(ruta_excel):
    if not os.path.exists(ruta_excel):
        print(f"❌ No se encontró el archivo {ruta_excel}")
        return

    # Inicializamos la base de datos por seguridad
    inicializar_base_datos()

    # Leemos el archivo Excel con pandas
    df = pd.read_excel(ruta_excel)
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    contador = 0

    for _, fila in df.iterrows():
        # Extraemos y limpiamos los datos de cada columna del Excel
        carrera = str(fila.get('carrera', '')).strip()
        codigo_asignatura = str(fila.get('codigo_asignatura', '')).strip()
        nombre_asignatura = str(fila.get('nombre_asignatura', '')).strip()
        area = str(fila.get('area', '')).strip()
        departamento = str(fila.get('departamento', '')).strip()
        dictado = str(fila.get('dictado', '')).strip()
        director_area = str(fila.get('director_area', '')).strip()
        responsable_asignatura = str(fila.get('responsable_asignatura', '')).strip()
        tipo_asignatura = str(fila.get('tipo_asignatura', '')).strip()
        ubicacion_ciclo = str(fila.get('ubicacion_ciclo', '')).strip()
        contenidos_basicos = str(fila.get('contenidos_basicos', '')).strip()
        alcances_plan = str(fila.get('alcances_plan', '')).strip()

        if not carrera or not nombre_asignatura:
            continue

        # 1. Obtener o insertar la Carrera
        cursor.execute("SELECT id FROM carreras WHERE nombre = ?", (carrera,))
        res_carrera = cursor.fetchone()
        if res_carrera:
            carrera_id = res_carrera["id"]
        else:
            cursor.execute("INSERT INTO carreras (nombre) VALUES (?)", (carrera,))
            carrera_id = cursor.lastrowid

        # 2. Obtener o insertar la Asignatura maestra
        cursor.execute("SELECT id FROM asignaturas WHERE nombre = ?", (nombre_asignatura,))
        res_asignatura = cursor.fetchone()
        if res_asignatura:
            asignatura_id = res_asignatura["id"]
        else:
            cursor.execute("INSERT INTO asignaturas (nombre) VALUES (?)", (nombre_asignatura,))
            asignatura_id = cursor.lastrowid

        # 3. Vincular en la tabla intermedia (Actualizar si ya existe la relación)
        cursor.execute("""
            SELECT id FROM carrera_asignatura WHERE carrera_id = ? AND asignatura_id = ?
        """, (carrera_id, asignatura_id))
        res_relacion = cursor.fetchone()

        if res_relacion:
            cursor.execute("""
                UPDATE carrera_asignatura 
                SET codigo_asignatura = ?, area = ?, departamento = ?, dictado = ?, 
                    director_area = ?, responsable_asignatura = ?, tipo_asignatura = ?, 
                    ubicacion_ciclo = ?, contenidos_basicos = ?, alcances_plan = ?
                WHERE id = ?
            """, (
                codigo_asignatura, area, departamento, dictado, director_area, 
                responsable_asignatura, tipo_asignatura, ubicacion_ciclo, 
                contenidos_basicos, alcances_plan, res_relacion["id"]
            ))
        else:
            cursor.execute("""
                INSERT INTO carrera_asignatura (
                    carrera_id, asignatura_id, codigo_asignatura, area, departamento, 
                    dictado, director_area, responsable_asignatura, tipo_asignatura, 
                    ubicacion_ciclo, contenidos_basicos, alcances_plan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                carrera_id, asignatura_id, codigo_asignatura, area, departamento, 
                dictado, director_area, responsable_asignatura, tipo_asignatura, 
                ubicacion_ciclo, contenidos_basicos, alcances_plan
            ))
            
        contador += 1

    conexion.commit()
    conexion.close()
    print(f"¡Importación exitosa! Se procesaron {contador} registros institucionales desde el Excel.")

if __name__ == "__main__":
    importar_excel_institucional("materias_institucionales.xlsx")