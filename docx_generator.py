import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generar_docx_programa(datos_programa, unidades_programa, ruta_salida="programa_analitico.docx"):
    doc = docx.Document()
    
    # --- ENCABEZADO CON LOGO (Opcional) ---
    if os.path.exists("logo_unr.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture("logo_unr.png", width=Inches(1.5))
    
    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_univ = p_univ.add_run("UNIVERSIDAD NACIONAL DE ROSARIO\nFACULTAD DE CIENCIAS BIOQUÍMICAS Y FARMACÉUTICAS")
    run_univ.font.size = Pt(10)
    run_univ.font.color.rgb = RGBColor(74, 85, 104)
    
    p_titulo = doc.add_heading("SISTEMA DE PROGRAMAS ANALÍTICOS (PANDA)", level=1)
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # --- DATOS BÁSICOS ---
    doc.add_heading("1. DATOS BÁSICOS DE LA ASIGNATURA", level=2)
    doc.add_paragraph(f"• Asignatura: {datos_programa.get('asignatura', '')}")
    doc.add_paragraph(f"• Carreras: {datos_programa.get('carreras_aplicadas', '')}")
    doc.add_paragraph(f"• Horas Teóricas: {datos_programa.get('horas_teoricas', 0)}")
    doc.add_paragraph(f"• Modalidad: {datos_programa.get('modalidad_virtual', '')}")
    
    # --- FUNDAMENTACIÓN ---
    doc.add_heading("2. FUNDAMENTACIÓN Y PROPÓSITOS", level=2)
    doc.add_paragraph(datos_programa.get('fund_31', 'No especificado'))
    
    # --- UNIDADES DINÁMICAS ---
    doc.add_heading("3. PROGRAMA ANALÍTICO (UNIDADES TEMÁTICAS)", level=2)
    for uni in unidades_programa:
        doc.add_heading(f"Unidad {uni.get('numero')}: {uni.get('nombre')}", level=3)
        doc.add_paragraph(f"Conceptos: {uni.get('conceptos')}")
        doc.add_paragraph(f"Trabajos Prácticos: {uni.get('trabajos_practicos')}")
        
    # --- BIBLIOGRAFÍA ---
    doc.add_heading("4. BIBLIOGRAFÍA", level=2)
    doc.add_paragraph(f"Obligatoria: {datos_programa.get('bib_obligatoria', 'No especificada')}")
    doc.add_paragraph(f"Complementaria: {datos_programa.get('bib_complementaria', 'No especificada')}")
    
    doc.save(ruta_salida)
    return ruta_salida