import os
from datetime import datetime
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Color institucional FBioyF: #25A09C -> RGB(37, 160, 156)
COLOR_HEX = "25A09C"
COLOR_RGB = RGBColor(37, 160, 156)

def set_cell_background(cell, hex_color):
    """Establece el color de fondo de una celda de tabla."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def agregar_encabezado_institucional(doc, logo_path="logo_fbioyf.png"):
    """Agrega la cabecera institucional con logo (si existe) y títulos en color institucional."""
    # Tabla superior para alinear logo y texto si existe el logo
    if os.path.exists(logo_path):
        header_table = doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_table.autofit = False
        
        # Celda del logo
        cell_logo = header_table.rows[0].cells[0]
        cell_logo.width = Inches(1.5)
        p_logo = cell_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_logo.add_run().add_picture(logo_path, width=Inches(1.2))
        
        # Celda de texto
        cell_text = header_table.rows[0].cells[1]
        cell_text.width = Inches(5.0)
        p_text = cell_text.paragraphs[0]
        p_text.alignment = WD_ALIGN_PARAGRAPH.LEFT
    else:
        p_text = doc.add_paragraph()
        p_text.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run_title1 = p_text.add_run("UNIVERSIDAD NACIONAL DE ROSARIO\n")
    run_title1.font.name = "Arial"
    run_title1.font.size = Pt(11)
    run_title1.font.bold = True
    run_title1.font.color.rgb = COLOR_RGB

    run_title2 = p_text.add_run("Facultad de Ciencias Bioquímicas y Farmacéuticas\n")
    run_title2.font.name = "Arial"
    run_title2.font.size = Pt(12)
    run_title2.font.bold = True
    run_title2.font.color.rgb = COLOR_RGB

    run_sub = p_text.add_run("SISTEMA PANDA - PROGRAMA ANALÍTICO (PUPA)")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(10)
    run_sub.font.italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

def agregar_titulo_seccion(doc, texto):
    """Agrega un encabezado de sección formateado con el color institucional."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(texto)
    run.font.name = "Arial"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = COLOR_RGB

def agregar_campo(doc, etiqueta, valor):
    """Agrega un par etiqueta - valor formateado."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    
    run_lbl = p.add_run(f"{etiqueta}: ")
    run_lbl.font.name = "Arial"
    run_lbl.font.size = Pt(10)
    run_lbl.font.bold = True
    
    val_text = str(valor) if valor is not None and str(valor).strip() != "" else "No especificado"
    run_val = p.add_run(val_text)
    run_val.font.name = "Arial"
    run_val.font.size = Pt(10)

def generar_doc_word(datos_materia, datos_formulario, ruta_salida="programa_analitico.docx", logo_path="logo_fbioyf.png"):
    """Genera el archivo Word completo combinando datos de BD y del formulario PUPA."""
    doc = docx.Document()

    # Configuración de márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Encabezado institucional
    agregar_encabezado_institucional(doc, logo_path)

    # DATOS DE LA ASIGNATURA (Base de Datos)
    agregar_titulo_seccion(doc, "1. INFORMACIÓN GENERAL DE LA ASIGNATURA")
    agregar_campo(doc, "Asignatura", datos_materia.get("nombre", ""))
    agregar_campo(doc, "Carrera", datos_materia.get("carrera", ""))
    agregar_campo(doc, "Código", datos_materia.get("codigo", ""))
    agregar_campo(doc, "Departamento / Área", datos_materia.get("departamento", ""))
    agregar_campo(doc, "Plan de Estudios / Año", datos_materia.get("plan", ""))
    agregar_campo(doc, "Equipo Docente", datos_materia.get("equipo_docente", ""))

    # BLOQUE 1: FUNDAMENTOS Y OBJETIVOS
    agregar_titulo_seccion(doc, "2. FUNDAMENTOS Y OBJETIVOS")
    agregar_campo(doc, "Fundamentos", datos_formulario.get("fundamentos", ""))
    agregar_campo(doc, "Objetivos Generales", datos_formulario.get("objetivos_generales", ""))

    # BLOQUE 2: CARGA HORARIA E INTERACCIÓN
    agregar_titulo_seccion(doc, "3. CARGA HORARIA E INTERACCIÓN DOCENTE-ESTUDIANTE")
    
    # Tabla de carga horaria
    table_h = doc.add_table(rows=2, cols=5)
    table_h.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_h = ["Teóricas", "Prácticas P1", "Prácticas P2", "Prácticas P3", "Otras Actividades"]
    
    hdr_cells = table_h.rows[0].cells
    for i, title in enumerate(headers_h):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], COLOR_HEX)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(9)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)

    vals_h = [
        f"{datos_formulario.get('num_h_teoricas', 0)} hs",
        f"{datos_formulario.get('num_h_p1', 0)} hs",
        f"{datos_formulario.get('num_h_p2', 0)} hs",
        f"{datos_formulario.get('num_h_p3', 0)} hs",
        f"{datos_formulario.get('num_h_otras', 0)} hs"
    ]
    val_cells = table_h.rows[1].cells
    for i, val in enumerate(vals_h):
        val_cells[i].text = val
        p = val_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    agregar_campo(doc, "Detalle de Otras Actividades", datos_formulario.get("text_detalle_otros", ""))
    agregar_campo(doc, "Modalidad de Cursado", datos_formulario.get("radio_modalidad_virtual", ""))
    agregar_campo(doc, "Porcentaje Virtual (si es Mixto)", datos_formulario.get("input_porcentaje_mixto", ""))
    agregar_campo(doc, "Espacios de Consulta", datos_formulario.get("text_espacios_consulta", ""))

    # BLOQUE 3: PROGRAMA ANALÍTICO Y CONTENIDOS
    agregar_titulo_seccion(doc, "4. PROGRAMA ANALÍTICO Y CONTENIDOS")
    agregar_campo(doc, "Unidades Temáticas y Contenidos", datos_formulario.get("contenidos_analiticos", ""))

    # BLOQUE 4: METODOLOGÍA Y ESTRATEGIAS
    agregar_titulo_seccion(doc, "5. METODOLOGÍA Y ESTRATEGIAS DIDÁCTICAS")
    agregar_campo(doc, "Estrategias de Enseñanza", datos_formulario.get("metodologia_ensenanza", ""))

    # BLOQUE 5: CRITERIOS DE EVALUACIÓN
    agregar_titulo_seccion(doc, "6. CRITERIOS DE EVALUACIÓN INSTITUCIONALES")
    criterios = datos_formulario.get("criterios_evaluacion", [])
    if criterios:
        table_crit = doc.add_table(rows=1, cols=5)
        table_crit.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers_crit = ["Criterio Evaluado", "Cursado", "Final Reg.", "Final Lib.", "N/A"]
        
        c_hdr = table_crit.rows[0].cells
        for i, h in enumerate(headers_crit):
            c_hdr[i].text = h
            set_cell_background(c_hdr[i], COLOR_HEX)
            p = c_hdr[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

        for item in criterios:
            row_cells = table_crit.add_row().cells
            row_cells[0].text = item.get("nombre", "")
            row_cells[1].text = "X" if item.get("cursado") else ""
            row_cells[2].text = "X" if item.get("regulares") else ""
            row_cells[3].text = "X" if item.get("libres") else ""
            row_cells[4].text = "X" if item.get("no_aplica") else ""

            for i in range(5):
                p = row_cells[i].paragraphs[0]
                if i > 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    agregar_campo(doc, "Otros Criterios Específicos", datos_formulario.get("otros_criterios_eval", ""))

    # BLOQUE 6: RÉGIMEN DE EVALUACIÓN
    agregar_titulo_seccion(doc, "7. RÉGIMEN DE EVALUACIÓN Y APROBACIÓN")
    agregar_campo(doc, "Reglamento de Cursado y Exámenes", datos_formulario.get("regimen_aprobacion", ""))

    # BLOQUE 7: CRONOGRAMA ESTIMADO
    agregar_titulo_seccion(doc, "8. CRONOGRAMA Y PLANIFICACIÓN")
    agregar_campo(doc, "Cronograma Tentativo", datos_formulario.get("cronograma_actividades", ""))

    # BLOQUE 8: BIBLIOGRAFÍA
    agregar_titulo_seccion(doc, "9. BIBLIOGRAFÍA")
    agregar_campo(doc, "Bibliografía Obligatoria y Complementaria", datos_formulario.get("bibliografia", ""))

    # BLOQUE 9: ADHESIÓN A PROGRAMAS ESPECIALES
    agregar_titulo_seccion(doc, "10. ADHESIÓN A PROGRAMAS ESPECIALES")
    progs = []
    if datos_formulario.get("prog_ltpa_cb"): progs.append("Condición LTPA (Libre con Trabajos Prácticos Aprobados)")
    if datos_formulario.get("prog_promuevo_cb"): progs.append('Programa "Yo También Promuevo"')
    if datos_formulario.get("prog_mesa_cb"): progs.append("Regularización en mesa de examen")
    if datos_formulario.get("prog_cuatrimestres_cb"): progs.append("Oferta de cursado en ambos cuatrimestres")
    if datos_formulario.get("prog_ninguno_cb"): progs.append("Ninguno de los anteriores")
    if datos_formulario.get("prog_otros_cb"): progs.append("Otros")

    agregar_campo(doc, "Programas Seleccionados", ", ".join(progs) if progs else "Ninguno")
    agregar_campo(doc, "Descripción de la Implementación", datos_formulario.get("desc_programas_text", ""))

    # PIE DE PÁGINA CON FECHA Y HORA DE IMPRESIÓN
    doc.add_paragraph().paragraph_format.space_before = Pt(20)
    p_footer = doc.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    fecha_impresion = datetime.now().strftime("%d/%m/%Y a las %H:%M hs")
    run_foot = p_footer.add_run(f"Documento generado el {fecha_impresion} - Sistema PANDA (FBioyF - UNR)")
    run_foot.font.name = "Arial"
    run_foot.font.size = Pt(8)
    run_foot.font.italic = True
    run_foot.font.color.rgb = RGBColor(120, 120, 120)

    doc.save(ruta_salida)
    return ruta_salida