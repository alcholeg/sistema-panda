import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generar_pdf_programa(datos_programa, unidades_programa, ruta_salida="programa_analitico.pdf"):
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        rightMargin=54, leftMargin=54,
        topMargin=54, bottomMargin=54
    )
    
    elementos = []
    styles = getSampleStyleSheet()
    
    # Estilos profesionales
    estilo_titulo = ParagraphStyle(
        'TituloInstitucional',
        parent=styles['Heading1'],
        fontSize=13,
        leading=16,
        alignment=1, # Centrado
        textColor=colors.HexColor("#1A365D")
    )
    
    estilo_subtitulo = ParagraphStyle(
        'SubTituloInstitucional',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor("#4A5568")
    )
    
    estilo_seccion = ParagraphStyle(
        'SeccionHeading',
        parent=styles['Heading2'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#FFFFFF"),
        spaceBefore=8,
        spaceAfter=4
    )
    
    estilo_texto = ParagraphStyle(
        'TextoNormal',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748")
    )

    # --- ENCABEZADO CON LOGO (Opcional) ---
    # Si tenés un archivo llamado 'logo_unr.png' en la carpeta, lo agrega automáticamente arriba
    if os.path.exists("logo_unr.png"):
        img = Image("logo_unr.png", width=120, height=45)
        img.hAlign = 'CENTER'
        elementos.append(img)
        elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("UNIVERSIDAD NACIONAL DE ROSARIO", estilo_subtitulo))
    elementos.append(Paragraph("FACULTAD DE CIENCIAS BIOQUÍMICAS Y FARMACÉUTICAS", estilo_subtitulo))
    elementos.append(Paragraph("<b>SISTEMA DE PROGRAMAS ANALÍTICOS (PANDA)</b>", estilo_titulo))
    elementos.append(Spacer(1, 15))

    # Función auxiliar para crear títulos de sección con fondo de color
    def agregar_titulo_seccion(texto):
        t_sec = Table([[Paragraph(f"<b>{texto}</b>", ParagraphStyle('Sec', parent=estilo_texto, textColor=colors.white))]], colWidths=[504])
        t_sec.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#2B6CB0")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elementos.append(t_sec)
        elementos.append(Spacer(1, 4))

    # --- DATOS BÁSICOS ---
    agregar_titulo_seccion("1. DATOS BÁSICOS DE LA ASIGNATURA")
    datos_tabla_basicos = [
        [Paragraph(f"<b>Asignatura:</b> {datos_programa.get('asignatura', '')}", estilo_texto),
         Paragraph(f"<b>Carreras:</b> {datos_programa.get('carreras_aplicadas', '')}", estilo_texto)],
        [Paragraph(f"<b>Horas Teóricas:</b> {datos_programa.get('horas_teoricas', 0)}", estilo_texto),
         Paragraph(f"<b>Modalidad:</b> {datos_programa.get('modalidad_virtual', '')}", estilo_texto)]
    ]
    t_basicos = Table(datos_tabla_basicos, colWidths=[252, 252])
    t_basicos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_basicos)
    elementos.append(Spacer(1, 10))

    # --- FUNDAMENTACIÓN ---
    agregar_titulo_seccion("2. FUNDAMENTACIÓN Y PROPÓSITOS")
    t_fund = Table([[Paragraph(datos_programa.get('fund_31', 'No especificado'), estilo_texto)]], colWidths=[504])
    t_fund.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_fund)
    elementos.append(Spacer(1, 10))

    # --- UNIDADES DINÁMICAS ---
    agregar_titulo_seccion("3. PROGRAMA ANALÍTICO (UNIDADES TEMÁTICAS)")
    for uni in unidades_programa:
        texto_uni = f"<b>Unidad {uni.get('numero')}: {uni.get('nombre')}</b><br/>" \
                    f"<i>Conceptos:</i> {uni.get('conceptos')}<br/>" \
                    f"<i>Trabajos Prácticos:</i> {uni.get('trabajos_practicos')}"
        
        t_uni = Table([[Paragraph(texto_uni, estilo_texto)]], colWidths=[504])
        t_uni.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elementos.append(t_uni)
        elementos.append(Spacer(1, 5))

    elementos.append(Spacer(1, 5))

    # --- BIBLIOGRAFÍA ---
    agregar_titulo_seccion("4. BIBLIOGRAFÍA")
    texto_bib = f"<b>Obligatoria:</b><br/>{datos_programa.get('bib_obligatoria', 'No especificada')}<br/><br/>" \
                f"<b>Complementaria:</b><br/>{datos_programa.get('bib_complementaria', 'No especificada')}"
    t_bib = Table([[Paragraph(texto_bib, estilo_texto)]], colWidths=[504])
    t_bib.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_bib)
    
    doc.build(elementos)
    return ruta_salida