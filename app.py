import os
import streamlit as st

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

# Título Principal Oficial de PANDA
st.title("🐼 Sistema PANDA - Sistema de Programas Analíticos con Núcleos de Datos Automatizados")
st.subheader("Facultad de Ciencias Bioquímicas y Farmacéuticas (UNR)")
st.markdown("---")

# --- CONTROL DE ACCESO / VISTA DOCENTE ---
menu = st.sidebar.selectbox("Navegación", ["Formulario Programa Analítico"], key="menu_navegacion_principal")

if menu == "Formulario Programa Analítico":
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

    asignatura_seleccionada = st.selectbox(
        "1.1. Asignatura Oficial (Obligatorio)",
        options=asignaturas_opciones,
        key="select_asignatura_b1"
    )
    
    st.session_state["asignatura_guardada"] = asignatura_seleccionada

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
        """, (st.session_state["asignatura_guardada"],))
        carreras_info = cursor.fetchall()
        conexion.close()
    except Exception:
        pass

    st.markdown("### 🗂️ Información Institucional Consolidada")

    if carreras_info:
        nombres_carreras_str = ", ".join([c["carrera_nombre"] for c in carreras_info if c["carrera_nombre"]])
        
        # Usamos set() y sorted() para evitar códigos, departamentos, dictados o ciclos repetidos
        codigos_str = ", ".join(sorted(list(set([str(c["codigo_asignatura"]) for c in carreras_info if c["codigo_asignatura"]]))))
        deptos_str = ", ".join(sorted(list(set([c["departamento"] for c in carreras_info if c["departamento"]]))))
        planes_str = ", ".join(sorted(list(set([c["dictado"] for c in carreras_info if c["dictado"]]))))
        ciclos_str = ", ".join(sorted(list(set([c["ubicacion_ciclo"] for c in carreras_info if c["ubicacion_ciclo"]]))))
        
        # Rescatamos los contenidos básicos y alcances de la información institucional de forma segura
        primer_registro = carreras_info[0] if carreras_info else None
        contenidos_basicos_str = primer_registro["contenidos_basicos"] if (primer_registro and primer_registro["contenidos_basicos"]) else "-"
        alcances_plan_str = primer_registro["alcances_plan"] if (primer_registro and primer_registro["alcances_plan"]) else "-"

        responsables = set([c["responsable_asignatura"] for c in carreras_info if c["responsable_asignatura"]])
        equipo_str = ", ".join(responsables) if responsables else "A determinar"

        # Guardamos todo en Session State para la exportación a PDF / Word
        st.session_state["carreras_guardadas"] = nombres_carreras_str
        st.session_state["codigo_materia"] = codigos_str
        st.session_state["departamento_materia"] = deptos_str
        st.session_state["plan_materia"] = planes_str
        st.session_state["ciclo_materia"] = ciclos_str
        st.session_state["contenidos_basicos_materia"] = contenidos_basicos_str
        st.session_state["alcances_plan_materia"] = alcances_plan_str
        st.session_state["equipo_docente_materia"] = equipo_str

        st.info(f"📌 **Esta asignatura se dicta en:** {nombres_carreras_str}")
        
        for info in carreras_info:
            with st.expander(f"📚 Datos oficiales para: {info['carrera_nombre']} (Código: {info['codigo_asignatura']})", expanded=False):
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
        st.session_state["carreras_guardadas"] = nombres_carreras_str
        st.session_state["codigo_materia"] = "-"
        st.session_state["departamento_materia"] = "-"
        st.session_state["plan_materia"] = "-"
        st.session_state["ciclo_materia"] = "-"
        st.session_state["contenidos_basicos_materia"] = "-"
        st.session_state["alcances_plan_materia"] = "-"
        st.session_state["equipo_docente_materia"] = "-"
        
        with st.container(border=True):
            st.write(f"Asignatura: **{st.session_state['asignatura_guardada']}**")
            st.info("ℹ️ No hay carreras o contenidos mínimos adicionales vinculados en la base de datos para esta materia de muestra.")

    st.write("---")

    # --- BLOQUE 2: CARGA HORARIA E INTERACCIÓN DOCENTE-ESTUDIANTE ---
    st.subheader("2. Carga Horaria e Interacción Docente-Estudiante")
    st.write("Indique la cantidad de  horas para cada categoría y describa los espacios de consulta.")

    st.info(
        "**Tipos de Prácticas:**\n"
        "- **P1 (Prácticas de Ejercitación):** Resolución de problemas a través de la reiteración de actividades para la incorporación de conceptos.\n"
        "- **P2 (Prácticas Experimentales):** Actividades de laboratorio, gabinete, en territorio o áulicas.\n"
        "- **P3 (Prácticas Integradoras Relacionadas con el Ejercicio Profesional):** Casos clínicos, simulación, monografías, análisis de trabajos científicos, etc."
    )

    horas_teoricas = st.number_input("2.1. Horas Teóricas (Obligatorio)", min_value=0.0, step=0.5, key="num_h_teoricas")
    horas_p1 = st.number_input("2.2. Horas Prácticas P1 - Ejercitación (Obligatorio)", min_value=0.0, step=0.5, key="num_h_p1")
    horas_p2 = st.number_input("2.3. Horas Prácticas P2 - Experimentales (Obligatorio)", min_value=0.0, step=0.5, key="num_h_p2")
    horas_p3 = st.number_input("2.4. Horas Prácticas P3 - Integradoras (Obligatorio)", min_value=0.0, step=0.5, key="num_h_p3")
    horas_otras = st.number_input("2.5. Horas para otras actividades (Obligatorio)", min_value=0.0, step=0.5, key="num_h_otras")

    # Cuadradito informativo con la suma total (excluyendo horas de consulta)
    total_horas_calc = horas_teoricas + horas_p1 + horas_p2 + horas_p3 + horas_otras
    st.info(f"⏱️ **Carga horaria total de la asignatura:** {total_horas_calc} hs")

    detalle_otros = st.text_area(
        "2.6. Detalle de Actividades en 'Otros' (Opcional)", 
        placeholder="Describa brevemente qué tipo de instancias se desarrollan en el tiempo indicado arriba.",
        key="text_detalle_otros"
    )
    modalidad_virtual = st.radio("2.7. Cursado mediante entornos virtuales (Obligatorio)", options=["100% presencial", "Mixto"], key="radio_modalidad_virtual")
    porcentaje_mixto = st.text_input("2.8. Porcentaje de dictado virtual en caso de mixto (Opcional)", key="input_porcentaje_mixto")
    espacios_consulta = st.text_area(
        "2.9. Espacios de Consulta (Obligatorio)", 
        placeholder="Indique días, horarios aproximados, modalidades (presencial / virtual) y régimen de consultas para las/os estudiantes. (Aclaración: las horas de consulta no se contabilizan dentro de la carga horaria total de la materia).",
        key="text_espacios_consulta"
    )

    st.write("---")

    # --- BLOQUE 3: FUNDAMENTACIÓN Y PROPUESTA ACADÉMICA ---
    st.subheader("3. Fundamentación y Propuesta Académica")
    st.markdown("Complete las 5 preguntas redactando un único párrafo articulado por cada respuesta. Estas respuestas se unificarán automáticamente para formar el texto continuo de la fundamentación del programa.")
    
    fund_31 = st.text_area(
        "3.1. Sentido y rol de la asignatura en el plan de estudios (Obligatorio)", 
        placeholder='Explique de qué trata la materia y por qué es necesario que el estudiante la curse en el año/cuatrimestre en el que está ubicada. Mencione qué saberes previos necesita el alumno (de materias anteriores) o qué base general aporta para el trayecto que inicia. Ejemplo de inicio: "La asignatura [Nombre] se ubica en el [año/cuatrimestre] de la carrera de [Carrera] y tiene como propósito fundamental introducir/profundizar..."',
        height=120, 
        key="fund_31"
    )
    fund_32 = st.text_area(
        "3.2. Aporte al perfil profesional y alcances del título (Obligatorio)", 
        placeholder='Vincule los contenidos con la práctica profesional real (en laboratorio, farmacia, investigación, industria o salud pública) y con las incumbencias o actividades reservadas al título. ¿Para qué le va a servir esta materia cuando se gradúe? Ejemplo de inicio: "En el marco del perfil profesional del [Bioquímico/Farmacéutico/etc.], esta materia aporta herramientas críticas para..."',
        height=120, 
        key="fund_32"
    )
    fund_33 = st.text_area(
        "3.3. Articulación con los contenidos mínimos del Plan de Estudios (Obligatorio)", 
        placeholder='Resuma los ejes temáticos o bloques de contenidos mínimos exigidos por el plan de estudios y explique la lógica con la que se ordenaron (por ejemplo: de lo teórico a lo práctico, de lo molecular a lo clínico, de lo general a lo aplicado). Ejemplo de inicio: "Para responder a los contenidos mínimos del plan de estudios, el programa se articula en [número] ejes temáticos principales que van desde..."',
        height=120, 
        key="fund_33"
    )
    fund_34 = st.text_area(
        "3.4. Propuesta Pedagógica (Obligatorio)", 
        placeholder='Describa brevemente la dinámica de trabajo (clases magistrales, laboratorios individuales/grupales, discusión de casos clínicos/farmacéuticos, aprendizaje basado en problemas, etc.) y justifique por qué esa metodología es la más adecuada para su materia. Ejemplo de inicio: "La propuesta pedagógica combina instancias de [clases magistrales / laboratorios / resolución de casos], priorizando un enfoque donde el estudiante..."',
        height=120, 
        key="fund_34"
    )
    fund_35 = st.text_area(
        "3.5. Habilidades transversales y pensamiento científico (Obligatorio)", 
        placeholder='Indique si la materia promueve el pensamiento crítico, la capacidad de análisis de datos, el trabajo en equipo, la bioseguridad, el rigor experimental o el compromiso ético en el área de las ciencias bioquímicas y farmacéuticas, entre otras habilidades transversales. Ejemplo de inicio: "A lo largo del cursado, se busca de manera transversal fomentar en el alumnado el pensamiento crítico, la destreza en la manipulación de..."',
        height=120, 
        key="fund_35"
    )

    st.write("---")

    # --- BLOQUE 4: PROGRAMA ANALÍTICO DE CONTENIDOS ---
    st.subheader("4. Programa Analítico de Contenidos")
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
    st.markdown("#### Articulación y Fundamentación por Categoría de Actividad")
    art_42 = st.text_area(
        "4.2. Articulación y fundamentación de las actividades teóricas (Obligatorio)", 
        placeholder='Describa brevemente qué habilidades específicas se desarrollan en los espacios teóricos y por qué se eligieron las metodologías de enseñanza escogidas.',
        height=120, 
        key="art_42"
    )
    art_43 = st.text_area(
        "4.3. Articulación y fundamentación de las actividades prácticas P1 (Obligatorio)", 
        placeholder='Describa brevemente qué competencias o técnicas específicas se desarrollan en los espacios de práctica de ejercitación áulica y por qué se eligieron las metodologías de enseñanza escogidas.',
        height=120, 
        key="art_43"
    )
    art_44 = st.text_area(
        "4.4. Articulación y fundamentación de las actividades prácticas P2 (Obligatorio)", 
        placeholder='Describa brevemente qué competencias o técnicas específicas se desarrollan en los espacios de prácticas experimentales o en territorio, y por qué se eligieron las metodologías de enseñanza escogidas.',
        height=120, 
        key="art_44"
    )
    art_45 = st.text_area(
        "4.5. Articulación y fundamentación de las actividades prácticas P3 (Obligatorio)", 
        placeholder='Describa brevemente qué competencias o técnicas específicas se desarrollan en los espacios de prácticas integradoras relacionadas con el ejercicio profesional, y por qué se eligieron las metodologías de enseñanza escogidas.',
        height=120, 
        key="art_45"
    )

    st.write("---")

    # --- BLOQUE 5: CRITERIOS DE EVALUACIÓN ---
    st.subheader("5. Criterios de Evaluación")
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
        "Uso de TIC y herramientas digitales",
        "Razonamiento ético y compromiso ambiental",
        "Autonomía y capacidad de autoaprendizaje",
        "Comprensión del contexto profesional y social"
    ]

    for idx, criterio in enumerate(criterios_institucionales):
        st.markdown(f"**5.1.{idx+1}. {criterio}**")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.checkbox("Cursado", key=f"crit_{idx}_cursado")
        with col_c2:
            st.checkbox("Final (Regulares)", key=f"crit_{idx}_regulares")
        with col_c3:
            st.checkbox("Final (Libres)", key=f"crit_{idx}_libres")
        with col_c4:
            st.checkbox("No Aplica", key=f"crit_{idx}_no_aplica")

    st.markdown("#### 5.2. Otros Criterios de Evaluación Específicos (Opcional)")
    otros_criterios = st.text_area(
        "Si la materia cuenta con criterios particulares, indíquelos a continuación:",
        placeholder="Si existen, listar otros criterios de evaluación específicos de la asignatura y aclarar en qué instancia/s se evalúan.",
        height=120,
        key="otros_criterios_eval"
    )

    st.write("---")

    # --- BLOQUE 6: CONDICIONES DE REGULARIDAD Y SISTEMA DE PROMOCIÓN ---
    st.subheader("6. Condiciones de Regularidad y Sistema de Promoción")
    
    # 6.1
    actividades_obligatorias = st.text_area(
        "6.1. Definición de las Actividades Obligatorias para acceder a la Regularidad (Obligatorio)",
        placeholder="Describir brevemente qué actividades de las ofrecidas en la asignatura se considerarán obligatorias...",
        height=120,
        key="actividades_obligatorias_text"
    )

    # 6.2 y 6.3
    col_pct1, col_pct2 = st.columns(2)
    with col_pct1:
        pct_asistencia = st.text_input(
            "6.2. % de Asistencia Exigido para Regularizar (Obligatorio)",
            placeholder="Indique el % requerido (entre el 60% y el 80%)...",
            key="pct_asistencia_input"
        )
    with col_pct2:
        pct_aprobacion = st.text_input(
            "6.3. % de Aprobación Exigido para Regularizar (Obligatorio)",
            placeholder="Indique el % requerido (entre el 60% y el 80%)...",
            key="pct_aprobacion_input"
        )

    # 6.4 Cantidad de parciales
    cantidad_parciales = st.radio(
        "6.4. Cantidad de Evaluaciones Parciales (Obligatorio)", 
        options=[0, 1, "2 (solo anuales)"], 
        horizontal=True, 
        key="cantidad_parciales_radio"
    )
    
    # 6.5
    detalle_eval_sumativas = st.text_area(
        "6.5. Detalle de Evaluaciones Sumativas (Obligatorio)",
        placeholder="Se incluyen dentro de las evaluaciones sumativas a los exámenes parciales...",
        height=130,
        key="detalle_eval_sumativas_text"
    )
    
    # 6.6 y 6.7 ahora marcados como Obligatorio en la interfaz
    eval_complementaria_promo = st.text_area(
        "6.6. Evaluación Complementaria para Promoción (Obligatorio)",
        placeholder="Si la asignatura considera que quienes regularizan acceden directamente a la promoción, indique expresamente 'No aplica'. En caso de existir, describa la evaluación complementaria...",
        height=120,
        key="eval_complementaria_promo_text"
    )

    calificacion_final_promo = st.text_area(
        "6.7. Calificación Final en Promoción (Obligatorio)",
        placeholder="Describa cómo se decidirá la calificación final de la asignatura si se aprueba en la cursada (por promoción)...",
        height=100,
        key="calificacion_final_promo_text"
    )

    st.write("---")

# --- BLOQUE 7: RÉGIMEN DE EXAMEN FINAL Y ESTUDIANTES LIBRES ---
    st.subheader("7. Régimen de Examen Final y Estudiantes Libres")

    st.markdown("##### 7.1 a 7.3. Examen Final para Estudiantes Regulares")
    
    eval_regular_modalidad = st.text_area(
        "7.1. Modalidad del Examen Regular (Obligatorio)",
        placeholder="Describa la modalidad (oral, escrito, presentación de monografía, etc.), instancias de la evaluación, si requiere la entrega previa de algún trabajo escrito, etc.",
        height=120,
        key="eval_regular_modalidad_text"
    )

    eval_regular_contenidos = st.text_area(
        "7.2. Contenidos del Examen Regular (Obligatorio)",
        placeholder="Listar brevemente los contenidos de la asignatura que se evaluarán en el examen final (considere los contenidos explicitados en 4.1).",
        height=120,
        key="eval_regular_contenidos_text"
    )

    eval_regular_calificacion = st.text_area(
        "7.3. Calificación Final (Examen Regular) (Obligatorio)",
        placeholder="Describir cómo se decidirá la calificación final de la asignatura si se aprueba el examen final.",
        height=100,
        key="eval_regular_calificacion_text"
    )

    st.markdown("---")
    st.markdown("##### 7.4 y 7.5. Examen para Estudiantes Libres")

    eval_libre_modalidad = st.text_area(
        "7.4. Modalidad del Examen para Libres (Obligatorio)",
        placeholder="Describa la modalidad (oral, escrito, presentación de monografía, etc.), instancias de la evaluación, si requiere la entrega previa de algún trabajo escrito, etc.",
        height=120,
        key="eval_libre_modalidad_text"
    )

    eval_libre_calificacion = st.text_area(
        "7.5. Calificación Final (Estudiantes Libres) (Obligatorio)",
        placeholder="Describir cómo se decidirá la calificación final de la asignatura si se aprueba el examen final.",
        height=100,
        key="eval_libre_calificacion_text"
    )

    st.write("---")

# --- BLOQUE 8: BIBLIOGRAFÍA ---
    st.subheader("8. Bibliografía")

    biblio_obligatoria = st.text_area(
        "8.1. Bibliografía Obligatoria (Obligatorio)",
        placeholder="Formato sugerido: AUTOR, Título, Editorial, Año, Edición. Indique si está disponible en la Biblioteca de la Facultad o en formato digital/acceso abierto.",
        height=130,
        key="biblio_obligatoria_text"
    )

    biblio_complementaria = st.text_area(
        "8.2. Bibliografía Complementaria (Opcional)",
        placeholder="Formato sugerido: AUTOR, Título, Editorial, Año, Edición. Indique si está disponible en la Biblioteca de la Facultad o en formato digital/acceso abierto.",
        height=130,
        key="biblio_complementaria_text"
    )

    st.write("---")

# --- BLOQUE 9: ADHESIÓN A PROGRAMAS ESPECIALES ---
    st.subheader("9. Adhesión a Programas Especiales de la Facultad")
    prog_ltpa = st.checkbox("Condición LTPA (Libre con Trabajos Prácticos Aprobados)", key="prog_ltpa_cb")
    prog_promuevo = st.checkbox('Programa "Yo También Promuevo"', key="prog_promuevo_cb")
    prog_mesa = st.checkbox("Regularización en mesa de examen", key="prog_mesa_cb")
    prog_cuatrimestres = st.checkbox("Oferta de cursado en ambos cuatrimestres", key="prog_cuatrimestres_cb")
    prog_ninguno = st.checkbox("Ninguno de los anteriores", key="prog_ninguno_cb")
    prog_otros = st.checkbox("Otros", key="prog_otros_cb")

    desc_programas = st.text_area(
        "9.2. Descripción de la implementación (Opcional)",
        placeholder="Explique cómo el área lleva a la práctica los beneficios o mecanismos contemplados en los programas seleccionados arriba.",
        height=120,
        key="desc_programas_text"
    )

    st.write("---")

    # --- BLOQUE 10: CONFORMIDAD Y GUARDADO FINAL ---
    st.subheader("10. Conformidad y Descarga de Documentos")
    conformidad_docente = st.checkbox(
        "Declaro que la presente propuesta ha sido informada al equipo docente del Área y responde al Plan de Estudio vigente. (Obligatorio)",
        key="conformidad_docente_cb"
    )

    st.write("")
    btn_finalizar = st.button("🚀 Finalizar, Guardar y Generar Documentos", type="primary", use_container_width=True)

    if btn_finalizar:
    # Validaciones obligatorias principales
        errores = []
        if not espacios_consulta.strip():
            errores.append("El campo '2.9. Espacios de Consulta' es obligatorio.")
        if not (fund_31.strip() and fund_32.strip() and fund_33.strip() and fund_34.strip() and fund_35.strip()):
            errores.append("Todos los puntos del Bloque 3 (Fundamentación) son obligatorios.")
        if not (art_42.strip() and art_43.strip() and art_44.strip() and art_45.strip()):
            errores.append("Los campos de articulación del Bloque 4 (4.2 al 4.5) son obligatorios.")
            
        # Validación actualizada para Bloque 6
        if not (
            str(actividades_obligatorias).strip() and 
            str(pct_asistencia).strip() and 
            str(pct_aprobacion).strip() and 
            str(detalle_eval_sumativas).strip() and 
            str(eval_complementaria_promo).strip() and 
            str(calificacion_final_promo).strip()
        ):
            errores.append("Todos los campos del Bloque 6 (Condiciones de Regularidad y Sistema de Promoción) son obligatorios (en caso de no poseer promoción, indicar 'No aplica').")
            
        # Validación corregida para Bloque 7 (Examen Final Regulares y Libres)
        if not (str(eval_regular_modalidad).strip() and str(eval_regular_contenidos).strip() and str(eval_regular_calificacion).strip() and str(eval_libre_modalidad).strip() and str(eval_libre_calificacion).strip()):
            errores.append("Todos los puntos del Bloque 7 (Examen Final y Estudiantes Libres) son obligatorios.")
            
        # Validación corregida para Bibliografía Obligatoria
        if not str(biblio_obligatoria).strip():
            errores.append("El campo '8.1. Bibliografía Obligatoria' es obligatorio.")
            
        if not (prog_ltpa or prog_promuevo or prog_mesa or prog_cuatrimestres or prog_ninguno or prog_otros):
            errores.append("Debe tildar al menos una opción en el punto 9.1 (Programas Especiales).")
        if not conformidad_docente:
            errores.append("Es obligatorio tildar la declaración de conformidad del equipo docente.")

        if errores:
            for err in errores:
                st.error(f"⚠️ {err}")
        else:
            try:
                conexion = obtener_conexion()
                cursor = conexion.cursor()
                
                asig_nombre = st.session_state.get("asignatura_guardada", "Asignatura")
                carreras_str = st.session_state.get("carreras_guardadas", "General")
                
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
                    asig_nombre, carreras_str, 
                    horas_teoricas, horas_p1, horas_p2, horas_p3,
                    horas_otras, detalle_otros, modalidad_virtual, porcentaje_mixto,
                    espacios_consulta, fund_31, fund_32, fund_33, fund_34, fund_35,
                    art_42, art_43, art_44, art_45, otros_criterios,
                    actividades_obligatorias, pct_asistencia, pct_aprobacion, 
                    cantidad_parciales, detalle_eval_sumativas, eval_complementaria_promo, calificacion_final_promo, 
                    eval_regular_modalidad, eval_regular_contenidos, eval_regular_calificacion, eval_libre_modalidad, 
                    eval_libre_calificacion, biblio_obligatoria, biblio_complementaria,
                    "Guardado institucional unificado", desc_programas, 1
                ))
                
                programa_id = cursor.lastrowid

                # 2. Guardar cada unidad dinámica del Bloque 4
                for i in range(1, st.session_state.get("num_unidades", 1) + 1):
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

                st.session_state.guardado_exitoso = True

            except Exception as e:
                st.error(f"Error al guardar en la base de datos: {e}")

# --- SECCIÓN DE DESCARGA Y GENERACIÓN ---
if st.session_state.get("guardado_exitoso", False):
    st.success("¡Excelente! El programa analítico completo de la asignatura ha sido guardado de forma permanente y se generaron los documentos.")
    
    from pdf_generator import generar_pdf_programa
    from docx_generator import generar_docx_programa

    datos_materia = {
        "nombre": st.session_state.get("asignatura_guardada", ""),
        "carrera": st.session_state.get("carreras_guardadas", ""),
        "codigo": st.session_state.get("codigo_materia", "-"),
        "departamento": st.session_state.get("departamento_materia", "-"),
        "plan": st.session_state.get("plan_materia", "-"),
        "ciclo": st.session_state.get("ciclo_materia", "-"),
        "contenidos_basicos": st.session_state.get("contenidos_basicos_materia", "-"),
        "alcances_plan": st.session_state.get("alcances_plan_materia", "-"),
        "equipo_docente": st.session_state.get("equipo_docente_materia", "-")
    }

    lista_unidades_gen = []
    texto_unidades = ""
    for i in range(1, st.session_state.get("num_unidades", 1) + 1):
        num = i
        nom = st.session_state.get(f"nombre_unidad_{i}", "")
        con = st.session_state.get(f"conceptos_unidad_{i}", "")
        tp = st.session_state.get(f"tp_unidad_{i}", "")
        
        p1 = "Sí" if st.session_state.get(f"p1_u_{i}", False) else "No"
        p2 = "Sí" if st.session_state.get(f"p2_u_{i}", False) else "No"
        p3 = "Sí" if st.session_state.get(f"p3_u_{i}", False) else "No"
        tipos_practica = f"P1 (Ejercitación): {p1} | P2 (Experimental): {p2} | P3 (Integradora): {p3}"

        lista_unidades_gen.append({
            "numero": num,
            "nombre": nom,
            "conceptos": con,
            "trabajos_practicos": tp,
            "tipos": tipos_practica
        })
        
        texto_unidades += f"<b>UNIDAD {num}: {nom}</b><br><br>"
        texto_unidades += f"<b>Contenidos:</b><br>{con}<br><br>"
        texto_unidades += f"<b>Trabajos Prácticos:</b><br>{tp}<br><br>"
        texto_unidades += f"<b>Tipo de Prácticas:</b><br>{tipos_practica}<br><br><hr style='border: 0; border-top: 1px solid #ccc; margin: 10px 0;'>"

    criterios_eval_lista = []
    criterios_nombres = [
        "Dominio de conceptos teóricos fundamentales", "Aplicación de herramientas lógico-matemáticas",
        "Manejo de lenguaje y terminología técnica", "Ejecución de procedimientos experimentales",
        "Cumplimiento de normas de bioseguridad e higiene", "Interpretación y análisis crítico de resultados",
        "Resolución de problemas de aplicación práctica", "Rigor y precisión en el registro de datos",
        "Capacidad de búsqueda y análisis bibliográfico", "Fundamentación y argumentación oral",
        "Trabajo colaborativo y en equipo", "Comprensión de sistemas de gestión de calidad",
        "Uso de TIC y herramientas digitales", "Razonamiento ético y compromiso ambiental",
        "Autonomía y capacidad de autoaprendizaje", "Comprensión del contexto profesional y social"
    ]
    
    for idx, crit_nom in enumerate(criterios_nombres):
        criterios_eval_lista.append({
            "nombre": crit_nom,
            "cursado": st.session_state.get(f"crit_{idx}_cursado", False),
            "regulares": st.session_state.get(f"crit_{idx}_regulares", False),
            "libres": st.session_state.get(f"crit_{idx}_libres", False),
            "no_aplica": st.session_state.get(f"crit_{idx}_no_aplica", False)
        })

    datos_formulario_completos = {
        "fundamentos": (
            f"{st.session_state.get('fund_31', '')}\n\n"
            f"{st.session_state.get('fund_32', '')}\n\n"
            f"{st.session_state.get('fund_33', '')}\n\n"
            f"{st.session_state.get('fund_34', '')}\n\n"
            f"{st.session_state.get('fund_35', '')}"
        ),
        "num_h_teoricas": st.session_state.get("num_h_teoricas", 0.0),
        "num_h_p1": st.session_state.get("num_h_p1", 0.0),
        "num_h_p2": st.session_state.get("num_h_p2", 0.0),
        "num_h_p3": st.session_state.get("num_h_p3", 0.0),
        "num_h_otras": st.session_state.get("num_h_otras", 0.0),
        "total_horas": (
            st.session_state.get("num_h_teoricas", 0.0) +
            st.session_state.get("num_h_p1", 0.0) +
            st.session_state.get("num_h_p2", 0.0) +
            st.session_state.get("num_h_p3", 0.0) +
            st.session_state.get("num_h_otras", 0.0)
        ),
        "text_detalle_otros": st.session_state.get("text_detalle_otros", ""),
        "radio_modalidad_virtual": st.session_state.get("radio_modalidad_virtual", "100% presencial"),
        "input_porcentaje_mixto": st.session_state.get("input_porcentaje_mixto", ""),
        "text_espacios_consulta": st.session_state.get("text_espacios_consulta", ""),
        "contenidos_analiticos": texto_unidades,
        "unidades_lista": lista_unidades_gen,
        "metodologia_teoricas": st.session_state.get('art_42', ''),
        "metodologia_p1": st.session_state.get('art_43', ''),
        "metodologia_p2": st.session_state.get('art_44', ''),
        "metodologia_p3": st.session_state.get('art_45', ''),
        "criterios_evaluacion": criterios_eval_lista,
        "otros_criterios_eval": st.session_state.get("otros_criterios_eval", ""),
        
        # Bloque 6
        "actividades_obligatorias": actividades_obligatorias,
        "asistencia_req": pct_asistencia,
        "aprobacion_req": pct_aprobacion,
        "cantidad_parciales": cantidad_parciales,
        "eval_sumativas": detalle_eval_sumativas,
        "eval_promocion": eval_complementaria_promo,
        "calif_promocion": calificacion_final_promo,
        
        # Bloque 7 (Exámenes Finales Regulares y Libres)
        "final_reg_mod": eval_regular_modalidad,
        "final_reg_cont": eval_regular_contenidos,
        "final_reg_crit": eval_regular_calificacion,
        "final_lib_mod": eval_libre_modalidad,
        "final_lib_crit": eval_libre_calificacion,
        
        # Bloque 8 (Bibliografía)
        "bib_obligatoria": biblio_obligatoria,
        "bib_complementaria": biblio_complementaria,
        
        # Bloque 9 (Programas Especiales)
        "prog_ltpa_cb": prog_ltpa,
        "prog_promuevo_cb": prog_promuevo,
        "prog_mesa_cb": prog_mesa,
        "prog_cuatrimestres_cb": prog_cuatrimestres,
        "prog_ninguno_cb": prog_ninguno,
        "prog_otros_cb": prog_otros,
        "desc_programas_text": desc_programas
    }

    # ¡Estas líneas estaban fuera del if y por eso fallaban!
    pdf_path = generar_pdf_programa(datos_materia, datos_formulario_completos)
    docx_path = generar_docx_programa(datos_materia, datos_formulario_completos)

    st.markdown("### 📥 Descarga de Documentos Oficiales")
    col_dl1, col_dl2 = st.columns(2)

    nombre_raw = datos_materia.get("nombre", "")
    nombre_str = "_".join(map(str, nombre_raw)) if isinstance(nombre_raw, list) else (str(nombre_raw) if nombre_raw else "Asignatura")
    nombre_archivo = nombre_str.replace(" ", "_")

    with col_dl1:
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as archivo_pdf:
                st.download_button(
                    label="📄 Descargar PUPA en PDF",
                    data=archivo_pdf,
                    file_name=f"Programa_{nombre_archivo}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("El archivo PDF no pudo generarse.")
            
    with col_dl2:
        if os.path.exists(docx_path):
            with open(docx_path, "rb") as archivo_docx:
                st.download_button(
                    label="📝 Descargar PUPA en Word",
                    data=archivo_docx,
                    file_name=f"Programa_{nombre_archivo}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        else:
            st.warning("El archivo Word no pudo generarse.")

    st.balloons()