import streamlit as st
import os
import pandas as pd

# 1. Configuración de la página (DEBE ser lo primero de Streamlit)
st.set_page_config(
    page_title="PANDA - Sistema de Programas",
    page_icon="🐼",
    layout="wide"
)

# 2. Como db_manager está en la misma carpeta, lo importamos directo
from db_manager import obtener_conexion, inicializar_base_datos

# 3. Inicializamos la base de datos y cargamos el Excel automáticamente
inicializar_base_datos()

# --- BLOQUE DE DIAGNÓSTICO TEMPORAL ---
st.write("### 🔍 Diagnóstico de Excel y Base de Datos")
base_dir = os.path.dirname(__file__)
excel_path = os.path.join(base_dir, 'materias_institucionales.xlsx')

st.write(f"**Ruta esperada del Excel:** `{excel_path}`")
st.write(f"**¿El archivo Excel existe físicamente?:** {os.path.exists(excel_path)}")

if os.path.exists(excel_path):
    try:
        df_test = pd.read_excel(excel_path)
        st.success(f"¡Excel leído con éxito! Columnas encontradas: `{list(df_test.columns)}`")
        st.write(f"Cantidad de filas en el Excel: {len(df_test)}")
    except Exception as e:
        st.error(f"Error al leer el Excel con pandas/openpyxl: {e}")

# Ver qué hay en la base de datos ahora
conn = obtener_conexion()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM asignaturas")
count_asig = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM carreras")
count_carr = cursor.fetchone()[0]
conn.close()

st.write(f"**Asignaturas en SQLite:** {count_asig}")
st.write(f"**Carreras en SQLite:** {count_carr}")
st.write("---")

# Título Principal Oficial de PANDA
st.title("🐼 PANDA")
st.subheader("Facultad de Ciencias Bioquímicas y Farmacéuticas (UNR)")
st.markdown("---")

# --- CONTROL DE ACCESO / VISTA DOCENTE ---
menu = st.sidebar.selectbox("Navegación", ["Formulario Programa Analítico"], key="menu_navegacion")

if menu == "Formulario Programa Analítico":
    st.header("📋 Borrador del Programa Analítico (PUPA)")
    st.caption("Carga colaborativa del programa unificado para Secretaría Académica.")
    
    st.write("---")

    
    # --- BLOQUE 1: DATOS BÁSICOS DE LA ASIGNATURA ---
    st.subheader("1. Datos Básicos de la Asignatura")
    st.write("Seleccione la asignatura oficial. El sistema mostrará la información institucional de todas las carreras en las que se dicta.")
    
    # Cargamos el listado maestro de asignaturas desde la base de datos
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM asignaturas ORDER BY nombre")
        asignaturas_db = cursor.fetchall()
        conexion.close()
        asignaturas_opciones = [a["nombre"] for a in asignaturas_db] if asignaturas_db else ["Química General e Inorgánica", "Fisiología Humana"]
    except Exception:
        asignaturas_opciones = ["Química General e Inorgánica", "Fisiología Humana"]

    with st.form("form_bloque_1"):
        asignatura_seleccionada = st.selectbox(
            "1.1. Asignatura Oficial (Obligatorio)",
            options=asignaturas_opciones,
            key="select_asignatura_b1"
        )
        
        guardar_bloque1 = st.form_submit_button("Consultar Información Institucional")
        if guardar_bloque1:
            st.success(f"Asignatura '{asignatura_seleccionada}' seleccionada con éxito.")

# Consultamos toda la información institucional para esta asignatura
    carreras_info = []
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT c.nombre AS carrera_nombre, ca.* 
            FROM carrera_asignatura ca
            JOIN carreras c ON ca.carrera_id = c.id
            JOIN asignaturas a ON ca.asignatura_id = a.id
            WHERE a.nombre = ?
        """, (asignatura_seleccionada,))
        carreras_info = cursor.fetchall()
        conexion.close()
    except Exception:
        pass

    st.markdown("### 🗂️ Información Institucional Consolidada")
    
    if carreras_info:
        nombres_carreras_str = ", ".join([c["carrera_nombre"] for c in carreras_info])
        st.info(f"📌 **Esta asignatura se dicta en:** {nombres_carreras_str}")
        
        for info in carreras_info:
            with st.expander(f"📚 Datos oficiales para: {info['carrera_nombre']} (Código: {info['codigo_asignatura']})", expanded=True):
                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1:
                    st.write(f"**Área:** {info['area'] or '-'}")
                    st.write(f"**Departamento:** {info['departamento'] or '-'}")
                with col_i2:
                    st.write(f"**Dictado:** {info['dictado'] or '-'}")
                    st.write(f"**Tipo:** {info['tipo_asignatura'] or '-'}")
                with col_i3:
                    st.write(f"**Ubicación Ciclo:** {info['ubicacion_ciclo'] or '-'}")
                
                st.write(f"**Director/a de Área:** {info['director_area'] or '-'}")
                st.write(f"**Responsable de Asignatura:** {info['responsable_asignatura'] or '-'}")
                
                st.markdown(f"**Contenidos Básicos:**")
                st.write(info["contenidos_basicos"] if info["contenidos_basicos"] else "No especificados.")
                
                st.markdown(f"**Alcances del Plan:**")
                st.write(info["alcances_plan"] if info["alcances_plan"] else "No especificados.")
    else:
        nombres_carreras_str = "Carrera General"
        with st.container(border=True):
            st.write(f"Asignatura: **{asignatura_seleccionada}**")
            st.info("ℹ️ No hay carreras o contenidos mínimos adicionales vinculados en la base de datos para esta materia de muestra.")

    st.write("---")

    # --- BLOQUE 2: CARGA HORARIA E INTERACCIÓN DOCENTE-ESTUDIANTE ---
    st.subheader("2. Carga Horaria e Interacción Docente-Estudiante")
    st.write("Indique las horas y espacios de consulta. (El punto 2.6 y 2.8 son opcionales).")

    with st.form("form_bloque_2"):
        horas_teoricas = st.number_input("2.1. Horas Teóricas (Obligatorio)", min_value=0.0, step=0.5, key="num_h_teoricas")
        horas_p1 = st.number_input("2.2. Horas Prácticas P1 (Obligatorio)", min_value=0.0, step=0.5, key="num_h_p1")
        horas_p2 = st.number_input("2.3. Horas Prácticas P2 (Obligatorio)", min_value=0.0, step=0.5, key="num_h_p2")
        horas_p3 = st.number_input("2.4. Horas Prácticas P3 (Obligatorio)", min_value=0.0, step=0.5, key="num_h_p3")
        horas_otras = st.number_input("2.5. Horas para otras actividades (Obligatorio)", min_value=0.0, step=0.5, key="num_h_otras")
        
        detalle_otros = st.text_area(
            "2.6. Detalle de Actividades en 'Otros' (Opcional)",
            placeholder="Describa brevemente si corresponde...",
            key="text_detalle_otros"
        )
        
        modalidad_virtual = st.radio("2.7. Cursado mediante entornos virtuales (Obligatorio)", options=["100% presencial", "Mixto"], key="radio_modalidad_virtual")
        
        porcentaje_mixto = st.text_input(
            "2.8. Porcentaje de dictado virtual en caso de mixto (Opcional)",
            placeholder="Ej: 20% virtual...",
            key="input_porcentaje_mixto"
        )
        
        espacios_consulta = st.text_area(
            "2.9. Espacios de Consulta (Obligatorio)",
            placeholder="Indique días, horarios y modalidades...",
            key="text_espacios_consulta"
        )

        guardar_bloque2 = st.form_submit_button("Guardar Bloque de Carga Horaria")
        if guardar_bloque2:
            if not espacios_consulta.strip():
                st.warning("⚠️ El campo '2.9. Espacios de Consulta' es obligatorio.")
            else:
                st.success("¡Bloque 2 registrado con éxito!")

    st.write("---")

    # --- BLOQUE 3: FUNDAMENTACIÓN Y PROPUESTA ACADÉMICA ---
    st.subheader("3. Fundamentación y Propuesta Académica")
    st.write("Todos los campos de este bloque son obligatorios.")

    with st.form("form_bloque_3"):
        fund_31 = st.text_area("3.1. Sentido y rol de la asignatura en el plan de estudios (Obligatorio)", height=120, key="fund_31")
        fund_32 = st.text_area("3.2. Aporte al perfil profesional y alcances del título (Obligatorio)", height=120, key="fund_32")
        fund_33 = st.text_area("3.3. Articulación con los contenidos mínimos del Plan de Estudios (Obligatorio)", height=120, key="fund_33")
        fund_34 = st.text_area("3.4. Propuesta Pedagógica (Obligatorio)", height=120, key="fund_34")
        fund_35 = st.text_area("3.5. Habilidades transversales y pensamiento científico (Obligatorio)", height=120, key="fund_35")

        guardar_bloque3 = st.form_submit_button("Guardar Fundamentación Académica")
        if guardar_bloque3:
            if not (fund_31.strip() and fund_32.strip() and fund_33.strip() and fund_34.strip() and fund_35.strip()):
                st.warning("⚠️ Todos los puntos del 3.1 al 3.5 son obligatorios.")
            else:
                st.success("¡Bloque 3 registrado con éxito!")

    st.write("---")

    # --- BLOQUE 4: PROGRAMA ANALÍTICO DE CONTENIDOS ---
    st.subheader("4. Programa Analítico de Contenidos")
    st.write("Ingrese el programa desglosado por Unidades, Ejes o Capítulos. Todos los campos de las unidades y las articulaciones (4.2 a 4.5) son obligatorios.")

    st.markdown("#### 4.1. Desarrollo del Programa Analítico")

    if 'num_unidades' not in st.session_state:
        st.session_state.num_unidades = 1

    col_btn1, col_btn2, _ = st.columns([2, 2, 6])
    with col_btn1:
        if st.button("➕ Agregar Unidad / Eje", key="btn_add_unidad"):
            st.session_state.num_unidades += 1
            st.rerun()
    with col_btn2:
        if st.session_state.num_unidades > 1:
            if st.button("➖ Quitar última Unidad", key="btn_remove_unidad"):
                st.session_state.num_unidades -= 1
                st.rerun()

    for i in range(1, st.session_state.num_unidades + 1):
        with st.container(border=True):
            st.markdown(f"##### UNIDAD / NÚCLEO / EJE {i}")
            st.text_input(f"Nombre de la Unidad {i} (Obligatorio)", key=f"nombre_unidad_{i}", placeholder="Ej: Introducción...")
            st.text_area(f"Contenidos conceptuales - Unidad {i} (Obligatorio)", key=f"conceptos_unidad_{i}", placeholder="Describa los contenidos...")
            st.text_area(f"Trabajos Prácticos / Seminarios asociados - Unidad {i} (Obligatorio)", key=f"tp_unidad_{i}", placeholder="Describa las actividades...")
            
            st.markdown("**Categorías de actividades prácticas asociadas a esta unidad:**")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.checkbox("P1 - Ejercitación", key=f"p1_u_{i}")
            with col_p2:
                st.checkbox("P2 - Experimental / Lab", key=f"p2_u_{i}")
            with col_p3:
                st.checkbox("P3 - Integradora", key=f"p3_u_{i}")

    st.write("")
    
    with st.form("form_bloque_4_articulacion"):
        st.markdown("#### Articulación y Fundamentación por Categoría de Actividad")
        art_42 = st.text_area("4.2. Articulación y fundamentación de las actividades teóricas (Obligatorio)", height=120, key="art_42")
        art_43 = st.text_area("4.3. Articulación y fundamentación de las actividades prácticas P1 (Obligatorio)", height=120, key="art_43")
        art_44 = st.text_area("4.4. Articulación y fundamentación de las actividades prácticas P2 (Obligatorio)", height=120, key="art_44")
        art_45 = st.text_area("4.5. Articulación y fundamentación de las actividades prácticas P3 (Obligatorio)", height=120, key="art_45")

        guardar_bloque4 = st.form_submit_button("Guardar Programa Analítico y Articulaciones")
        if guardar_bloque4:
            if not (art_42.strip() and art_43.strip() and art_44.strip() and art_45.strip()):
                st.warning("⚠️ Los campos de articulación del 4.2 al 4.5 son obligatorios.")
            else:
                st.success("¡Bloque 4 registrado exitosamente!")

    st.write("---")

    # --- BLOQUE 5: CRITERIOS DE EVALUACIÓN ---
    st.subheader("5. Criterios de Evaluación")
    st.write("5.1. Marque las instancias institucionales obligatorias. (El punto 5.2 es opcional).")

    criterios_institucionales = [
        "Dominio de conceptos teóricos fundamentales",
        "Aplicación de herramientas lógico-matemáticas",
        "Manejo de lenguaje y terminología técnica",
        "Ejecución de procedimientos experimentales",
        "Cumplimiento de normas de bioseguridad e higiene",
        "Interpretación y análisis crítico de resultados",
        "Resolución de problemas de aplicación práctica",
        "Rigor y precisión en el registro de datos",
        "Capacidad de búsqueda y análisis bibliográfico",
        "Fundamentación y argumentación oral",
        "Trabajo colaborativo y en equipo",
        "Comprensión de sistemas de gestión de calidad",
        "Uso de TICs y herramientas digitales",
        "Razonamiento ético y compromiso ambiental",
        "Autonomía y capacidad de autoaprendizaje",
        "Comprensión del contexto profesional y social"
    ]

    with st.form("form_bloque_5"):
        for idx, criterio in enumerate(criterios_institucionales):
            st.markdown(f"**{idx+1}. {criterio}**")
            col_c1, col_c2, col_c3, col_c4 = st.columns(4)
            with col_c1:
                st.checkbox("Cursado", key=f"crit_{idx}_cursado")
            with col_c2:
                st.checkbox("Final (Regulares)", key=f"crit_{idx}_regulares")
            with col_c3:
                st.checkbox("Final (Libres)", key=f"crit_{idx}_libres")
            with col_c4:
                st.checkbox("No Aplica", key=f"crit_{idx}_no_aplica")
            st.write("")

        st.markdown("---")
        st.subheader("5.2. Otros Criterios de Evaluación Específicos de la Asignatura (Opcional)")
        otros_criterios = st.text_area(
            "Si existen, listar otros criterios específicos...",
            placeholder="Describa otros criterios particulares...",
            height=120,
            key="otros_criterios_eval"
        )

        guardar_bloque5 = st.form_submit_button("Guardar Criterios de Evaluación")
        if guardar_bloque5:
            st.success("¡Bloque 5 registrado con éxito!")

    st.write("---")

    # --- BLOQUE 6: EVALUACIÓN DE LA CURSADA ---
    st.subheader("6. Evaluación de la Cursada")
    st.write("Todos los campos de este bloque son obligatorios.")
    
    with st.form("form_bloque_6"):
        st.markdown("#### 6.1. Descripción de actividades obligatorias (Obligatorio)")
        desc_actividades_obligatorias = st.text_area(
            "Describa las actividades obligatorias...",
            height=120,
            key="desc_actividades_obligatorias"
        )

        st.markdown("#### 6.2. Porcentaje de asistencia requerido (Obligatorio)")
        asistencia_req = st.text_input(
            "Indique el % requerido (entre 60% y 80% o 0):",
            key="asistencia_req_input"
        )

        st.markdown("#### 6.3. Porcentaje de aprobación requerido (Obligatorio)")
        aprobacion_req = st.text_input(
            "Indique el % requerido (entre 60% y 80% o 0):",
            key="aprobacion_req_input"
        )

        st.markdown("#### 6.4. Cantidad de Evaluaciones Parciales (Obligatorio)")
        cantidad_parciales = st.radio(
            "Seleccione la cantidad:",
            options=[0, 1, 2],
            horizontal=True,
            key="cantidad_parciales_radio"
        )

        st.markdown("#### 6.5. Evaluaciones Sumativas durante la Cursada (Obligatorio)")
        eval_sumativas = st.text_area(
            "Detalle modalidad y contenidos...",
            height=120,
            key="eval_sumativas_text"
        )

        st.markdown("#### 6.6. Modalidad de evaluación complementaria para Promoción (Obligatorio)")
        eval_promocion = st.text_area(
            "Describa la instancia de promoción...",
            height=120,
            key="eval_promocion_text"
        )

        st.markdown("#### 6.7. Criterio de calificación final por Promoción (Obligatorio)")
        calif_promocion = st.text_area(
            "Describa el criterio de calificación final...",
            height=120,
            key="calif_promocion_text"
        )

        guardar_bloque6 = st.form_submit_button("Guardar Evaluación de la Cursada")
        if guardar_bloque6:
            if not (desc_actividades_obligatorias.strip() and asistencia_req.strip() and aprobacion_req.strip() and eval_sumativas.strip() and eval_promocion.strip() and calif_promocion.strip()):
                st.warning("⚠️ Todos los campos del Bloque 6 (salvo excepciones) son obligatorios.")
            else:
                st.success("¡Bloque 6 registrado con éxito!")

    st.write("---")

    # --- BLOQUE 7: ACREDITACIÓN POR EXAMEN FINAL ---
    st.subheader("7. Acreditación por Examen Final")
    st.write("Todos los campos de este bloque son obligatorios.")

    with st.form("form_bloque_7"):
        st.markdown("#### 7.1. Modalidad de examen final para Regulares (Obligatorio)")
        final_reg_mod = st.text_area("Describa la modalidad para regulares...", height=120, key="final_reg_mod_text")

        st.markdown("#### 7.2. Contenidos a evaluar en examen final Regular (Obligatorio)")
        final_reg_cont = st.text_area("Liste los contenidos...", height=120, key="final_reg_cont_text")

        st.markdown("#### 7.3. Criterio de calificación final para Regulares (Obligatorio)")
        final_reg_crit = st.text_area("Describa el criterio para regulares...", height=120, key="final_reg_crit_text")

        st.markdown("#### 7.4. Modalidad de examen final para Libres (Obligatorio)")
        final_lib_mod = st.text_area("Describa la modalidad para libres...", height=120, key="final_lib_mod_text")

        st.markdown("#### 7.5. Criterio de calificación final para Libres (Obligatorio)")
        final_lib_crit = st.text_area("Describa el criterio para libres...", height=120, key="final_lib_crit_text")

        guardar_bloque7 = st.form_submit_button("Guardar Acreditación por Examen Final")
        if guardar_bloque7:
            if not (final_reg_mod.strip() and final_reg_cont.strip() and final_reg_crit.strip() and final_lib_mod.strip() and final_lib_crit.strip()):
                st.warning("⚠️ Todos los puntos del 7.1 al 7.5 son obligatorios.")
            else:
                st.success("¡Bloque 7 registrado con éxito!")

    st.write("---")

    # --- BLOQUE 8: BIBLIOGRAFÍA ---
    st.subheader("8. Bibliografía")
    st.write("8.1 es obligatoria. 8.2 es opcional.")

    with st.form("form_bloque_8"):
        st.markdown("#### 8.1. Bibliografía Obligatoria (Obligatorio)")
        bib_obligatoria = st.text_area(
            "AUTOR, Título, Editorial, Año...",
            height=140,
            key="bib_obligatoria_text"
        )

        st.markdown("#### 8.2. Bibliografía Complementaria (Opcional)")
        bib_complementaria = st.text_area(
            "AUTOR, Título, Editorial, Año...",
            height=140,
            key="bib_complementaria_text"
        )

        guardar_bloque8 = st.form_submit_button("Guardar Bibliografía")
        if guardar_bloque8:
            if not bib_obligatoria.strip():
                st.warning("⚠️ El campo '8.1. Bibliografía Obligatoria' es obligatorio.")
            else:
                st.success("¡Bloque 8 registrado con éxito!")

    st.write("---")

    # --- BLOQUE 9: ADHESIÓN A PROGRAMAS ESPECIALES DE LA FACULTAD ---
    st.subheader("9. Adhesión a Programas Especiales de la Facultad")
    st.write("9.1 es obligatorio seleccionar al menos una opción. 9.2 es opcional.")

    with st.form("form_bloque_9"):
        st.markdown("#### 9.1. Seleccione los programas o regímenes especiales (Obligatorio):")
        prog_ltpa = st.checkbox("Condición LTPA", key="prog_ltpa_cb")
        prog_promuevo = st.checkbox('Programa "Yo También Promuevo"', key="prog_promuevo_cb")
        prog_mesa = st.checkbox("Regularización en mesa de examen", key="prog_mesa_cb")
        prog_cuatrimestres = st.checkbox("Oferta de cursado en ambos cuatrimestres", key="prog_cuatrimestres_cb")
        prog_ninguno = st.checkbox("Ninguno de los anteriores", key="prog_ninguno_cb")
        prog_otros = st.checkbox("Otros", key="prog_otros_cb")

        st.markdown("#### 9.2. Descripción de la implementación (Opcional)")
        desc_programas = st.text_area(
            "Explique la implementación...",
            height=120,
            key="desc_programas_text"
        )

        guardar_bloque9 = st.form_submit_button("Guardar Programas Especiales")
        if guardar_bloque9:
            if not (prog_ltpa or prog_promuevo or prog_mesa or prog_cuatrimestres or prog_ninguno or prog_otros):
                st.warning("⚠️ Debe tildar al menos una opción en el punto 9.1.")
            else:
                st.success("¡Bloque 9 registrado con éxito!")

    st.write("---")

    # --- BLOQUE 10: CONFORMIDAD Y GUARDADO FINAL ---
    st.subheader("10. Conformidad y Descarga de Documentos")

    with st.form("form_bloque_10"):
        st.markdown("#### 10.1. Conformidad del Equipo Docente (Obligatorio)")
        conformidad_docente = st.checkbox(
            "Declaro que la presente propuesta ha sido informada al equipo docente del Área y responde al Plan de Estudio vigente.",
            key="conformidad_docente_cb"
        )

        guardar_bloque10 = st.form_submit_button("Finalizar, Guardar y Generar Documentos")
        
        if guardar_bloque10:
            if not conformidad_docente:
                st.error("⚠️ Para finalizar y enviar la propuesta, es obligatorio tildar la declaración de conformidad del equipo docente.")
            else:
                try:
                    conexion = obtener_conexion()
                    cursor = conexion.cursor()
                    
                    # 1. Guardar datos principales del programa
                    cursor.execute("""
                        INSERT INTO programas_analiticos (
                            asignatura, carreras_aplicadas, horas_teoricas, horas_p1, horas_p2, horas_p3, 
                            horas_otras, detalle_otros, modalidad_virtual, porcentaje_mixto, 
                            espacios_consulta, fund_31, fund_32, fund_33, fund_34, fund_35, 
                            art_42, art_43, art_44, art_45, otros_criterios, 
                            desc_actividades_obligatorias, asistencia_req, aprobacion_req, 
                            cantidad_parciales, eval_sumativas, eval_promocion, calif_promocion, 
                            final_reg_mod, final_reg_cont, final_reg_crit, final_lib_mod, 
                            final_lib_crit, bib_obligatoria, bib_complementaria, 
                            programas_especiales, desc_programas, conformidad
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        asignatura_seleccionada, nombres_carreras_str, horas_teoricas, horas_p1, horas_p2, horas_p3,
                        horas_otras, detalle_otros, modalidad_virtual, porcentaje_mixto,
                        espacios_consulta, fund_31, fund_32, fund_33, fund_34, fund_35,
                        art_42, art_43, art_44, art_45, otros_criterios,
                        desc_actividades_obligatorias, asistencia_req, aprobacion_req,
                        cantidad_parciales, eval_sumativas, eval_promocion, calif_promocion,
                        final_reg_mod, final_reg_cont, final_reg_crit, final_lib_mod,
                        final_lib_crit, bib_obligatoria, bib_complementaria,
                        "Guardado institucional unificado", desc_programas, 1
                    ))
                    
                    programa_id = cursor.lastrowid # Obtenemos el ID generado

                    # 2. Guardar cada unidad dinámica del Bloque 4.1
                    for i in range(1, st.session_state.num_unidades + 1):
                        nombre_uni = st.session_state.get(f"nombre_unidad_{i}", "")
                        conceptos_uni = st.session_state.get(f"conceptos_unidad_{i}", "")
                        tp_uni = st.session_state.get(f"tp_unidad_{i}", "")
                        p1_uni = 1 if st.session_state.get(f"p1_u_{i}", False) else 0
                        p2_uni = 1 if st.session_state.get(f"p2_u_{i}", False) else 0
                        p3_uni = 1 if st.session_state.get(f"p3_u_{i}", False) else 0

                        cursor.execute("""
                            INSERT INTO unidades_programa (
                                programa_id, numero_unidad, nombre_unidad, conceptos, 
                                trabajos_practicos, practica_p1, practica_p2, practica_p3
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (programa_id, i, nombre_uni, conceptos_uni, tp_uni, p1_uni, p2_uni, p3_uni))

                    conexion.commit()
                    conexion.close()

                    # Guardamos un indicador en session_state para mostrar la descarga afuera del form
                    st.session_state.guardado_exitoso = True
                    st.session_state.asignatura_guardada = asignatura_seleccionada
                    st.session_state.carreras_guardadas = nombres_carreras_str

                except Exception as e:
                    st.error(f"Error al guardar en la base de datos: {e}")

    # Si ya se guardó con éxito, mostramos los botones de descarga fuera del form para evitar recargas raras
    if st.session_state.get("guardado_exitoso", False):
        st.success("¡Excelente! El programa analítico completo de la asignatura ha sido guardado de forma permanente en la base de datos de PANDA.")
        
        from pdf_generator import generar_pdf_programa
        from docx_generator import generar_docx_programa

        # Consolidamos datos para los generadores
        dict_datos = {
            "asignatura": st.session_state.get("asignatura_guardada", ""),
            "carreras_aplicadas": st.session_state.get("carreras_guardadas", ""),
            "horas_teoricas": horas_teoricas,
            "modalidad_virtual": modalidad_virtual,
            "fund_31": fund_31,
            "bib_obligatoria": bib_obligatoria,
            "bib_complementaria": bib_complementaria
        }

        lista_unidades_gen = []
        for i in range(1, st.session_state.num_unidades + 1):
            lista_unidades_gen.append({
                "numero": i,
                "nombre": st.session_state.get(f"nombre_unidad_{i}", ""),
                "conceptos": st.session_state.get(f"conceptos_unidad_{i}", ""),
                "trabajos_practicos": st.session_state.get(f"tp_unidad_{i}", "")
            })

        pdf_path = generar_pdf_programa(dict_datos, lista_unidades_gen)
        docx_path = generar_docx_programa(dict_datos, lista_unidades_gen)

        st.markdown("### 📥 Descarga de Documentos Oficiales")
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            with open(pdf_path, "rb") as archivo_pdf:
                st.download_button(
                    label="📄 Descargar PDF Oficial",
                    data=archivo_pdf,
                    file_name=f"Programa_{asignatura_seleccionada.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
        with col_dl2:
            with open(docx_path, "rb") as archivo_docx:
                st.download_button(
                    label="📝 Descargar Word (.docx)",
                    data=archivo_docx,
                    file_name=f"Programa_{asignatura_seleccionada.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

        st.balloons()