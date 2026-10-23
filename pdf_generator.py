import os
import base64
from datetime import datetime

def imagen_a_base64(ruta_imagen):
    """Convierte la imagen del logo a Base64 para incrustarla directamente en el HTML del PDF."""
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    return ""

def generar_html_programa(datos_materia, datos_formulario, logo_path="logo_fbioyf.png"):
    """Construye el HTML estilizado con la paleta de colores oficial #25A09C."""
    logo_b64 = imagen_a_base64(logo_path)
    fecha_impresion = datetime.now().strftime("%d/%m/%Y a las %H:%M hs")

    # Formatear programas especiales
    progs = []
    if datos_formulario.get("prog_ltpa_cb"): progs.append("Condición LTPA (Libre con Trabajos Prácticos Aprobados)")
    if datos_formulario.get("prog_promuevo_cb"): progs.append('Programa "Yo También Promuevo"')
    if datos_formulario.get("prog_mesa_cb"): progs.append("Regularización en mesa de examen")
    if datos_formulario.get("prog_cuatrimestres_cb"): progs.append("Oferta de cursado en ambos cuatrimestres")
    if datos_formulario.get("prog_ninguno_cb"): progs.append("Ninguno de los anteriores")
    if datos_formulario.get("prog_otros_cb"): progs.append("Otros")
    str_progs = ", ".join(progs) if progs else "Ninguno"

    # Filas de criterios de evaluación
    filas_criterios_html = ""
    criterios = datos_formulario.get("criterios_evaluacion", [])
    for c in criterios:
        filas_criterios_html += f"""
        <tr>
            <td style="text-align: left;">{c.get('nombre', '')}</td>
            <td>{'X' if c.get('cursado') else ''}</td>
            <td>{'X' if c.get('regulares') else ''}</td>
            <td>{'X' if c.get('libres') else ''}</td>
            <td>{'X' if c.get('no_aplica') else ''}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm;
            }}
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                color: #333333;
                font-size: 10pt;
                line-height: 1.4;
            }}
            .header-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                border-bottom: 2px solid #25A09C;
                padding-bottom: 10px;
            }}
            .header-table td {{
                border: none;
                vertical-align: middle;
            }}
            .logo-cell {{
                width: 120px;
            }}
            .logo-img {{
                max-width: 100px;
                height: auto;
            }}
            .title-cell {{
                text-align: left;
            }}
            .title-cell h2 {{
                color: #25A09C;
                margin: 0;
                font-size: 13pt;
                text-transform: uppercase;
            }}
            .title-cell h3 {{
                color: #25A09C;
                margin: 3px 0;
                font-size: 11pt;
            }}
            .title-cell p {{
                margin: 0;
                font-size: 9pt;
                color: #555555;
            }}
            h3.section-title {{
                color: #25A09C;
                border-bottom: 1px solid #25A09C;
                padding-bottom: 3px;
                margin-top: 18px;
                margin-bottom: 8px;
                font-size: 11pt;
                text-transform: uppercase;
            }}
            .field-row {{
                margin-bottom: 6px;
            }}
            .field-label {{
                font-weight: bold;
                color: #222222;
            }}
            .field-value {{
                color: #444444;
            }}
            table.data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
                margin-bottom: 8px;
            }}
            table.data-table th {{
                background-color: #25A09C;
                color: #ffffff;
                font-size: 8.5pt;
                padding: 6px;
                border: 1px solid #25A09C;
                text-align: center;
            }}
            table.data-table td {{
                border: 1px solid #dddddd;
                padding: 5px;
                font-size: 8.5pt;
                text-align: center;
            }}
            .footer {{
                margin-top: 30px;
                text-align: right;
                font-size: 8pt;
                color: #777777;
                border-top: 1px solid #eeeeee;
                padding-top: 6px;
            }}
        </style>
    </head>
    <body>
        <table class="header-table">
            <tr>
                {f'<td class="logo-cell" style="padding-right: 15px;"><img src="{logo_b64}" class="logo-img"></td>' if logo_b64 else ''}
                <td class="title-cell">
                    <h2>Universidad Nacional de Rosario</h2>
                    <h3>Facultad de Ciencias Bioquímicas y Farmacéuticas</h3>
                    <p>SISTEMA PANDA - PROGRAMA ANALÍTICO UNIFICADO (PUPA)</p>
                </td>
            </tr>
        </table>

        <h3 class="section-title">1. Información General de la Asignatura</h3>
        <div class="field-row"><span class="field-label">Asignatura:</span> <span class="field-value">{datos_materia.get('nombre', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Carrera/s:</span> <span class="field-value">{datos_materia.get('carrera', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Código/s:</span> <span class="field-value">{datos_materia.get('codigo', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Departamento / Área:</span> <span class="field-value">{datos_materia.get('departamento', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Dictado:</span> <span class="field-value">{datos_materia.get('plan', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Ubicación en el Ciclo:</span> <span class="field-value">{datos_materia.get('ciclo', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Contenidos Básicos:</span> <span class="field-value">{datos_materia.get('contenidos_basicos', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Alcances del Plan:</span> <span class="field-value">{datos_materia.get('alcances_plan', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">Docente Responsable:</span> <span class="field-value">{datos_materia.get('equipo_docente', 'No especificado')}</span></div>

        <h3 class="section-title">2. Fundamentación</h3>
        <div class="field-row"><span class="field-label">Fundamentación:</span> <span class="field-value">{datos_formulario.get('fundamentos', 'No especificado')}</span></div>

        <h3 class="section-title">3. Carga Horaria</h3>
        <div class="field-row" style="margin-bottom: 10px; font-size: 8.5pt; color: #444444;">
            <strong>Tipos de Prácticas:</strong><br>
            • <strong>P1 (Prácticas de Ejercitación):</strong> Se incluyen aquí las prácticas de ejercitación: resolución de problemas a través de la reiteración de actividades (reconocimiento, exploración, ejercicios o problemas) tendientes a la incorporación de conceptos.<br>
            • <strong>P2 (Prácticas Experimentales):</strong> Se incluyen aquí las prácticas experimentales: actividades que promueven el desarrollo de habilidades propias basadas en la observación, exploración, experimentación y organización. Incluye prácticas de laboratorio, gabinete, en territorio o áulicas.<br>
            • <strong>P3 (Prácticas Integradoras Relacionadas con el Ejercicio Profesional):</strong> Se incluyen aquí las prácticas integradoras relacionadas con el ejercicio profesional: actividades que impliquen resolución de casos clínicos, simulación, elaboración de monografías, escritura de trabajos de divulgación, entre otras. En esta categoría también estarían incluidas análisis y discusión de trabajos científicos, búsqueda y análisis crítico de información en ciencias, entre otras.
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Teóricas</th>
                    <th>Prácticas P1</th>
                    <th>Prácticas P2</th>
                    <th>Prácticas P3</th>
                    <th>Otras Actividades</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{datos_formulario.get('num_h_teoricas', 0)} hs</td>
                    <td>{datos_formulario.get('num_h_p1', 0)} hs</td>
                    <td>{datos_formulario.get('num_h_p2', 0)} hs</td>
                    <td>{datos_formulario.get('num_h_p3', 0)} hs</td>
                    <td>{datos_formulario.get('num_h_otras', 0)} hs</td>
                </tr>
            </tbody>
        </table>    
        <div class="field-row" style="background-color: #f4f6f8; border-left: 4px solid #25A09C; padding: 6px 10px; margin: 8px 0;">
            <span class="field-label">Carga horaria total de la asignatura:</span> <span class="field-value"><strong>{datos_formulario.get('total_horas', 0)} hs</strong></span>
        </div>
        <div class="field-row"><span class="field-label">Detalle de 'Otras':</span> <span class="field-value">{datos_formulario.get('text_detalle_otros', 'N/A')}</span></div>
        <div class="field-row"><span class="field-label">Modalidad:</span> <span class="field-value">{datos_formulario.get('radio_modalidad_virtual', '100% presencial')}</span></div>
        <div class="field-row"><span class="field-label">Porcentaje Virtual:</span> <span class="field-value">{datos_formulario.get('input_porcentaje_mixto', 'N/A')}</span></div>
        <div class="field-row"><span class="field-label">Espacios de Consulta:</span> <span class="field-value">{datos_formulario.get('text_espacios_consulta', 'No especificado')}</span></div>

        <h3 class="section-title">4. Programa Analítico y Contenidos</h3>
        <div class="field-row"><span class="field-value">{datos_formulario.get('contenidos_analiticos', 'No especificado')}</span></div>

        <h3 class="section-title">5. Metodología y Estrategias Didácticas</h3>
        <div class="field-row"><span class="field-label">5.1. Teóricas:</span> <span class="field-value">{datos_formulario.get('metodologia_teoricas', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">5.2. Prácticas P1:</span> <span class="field-value">{datos_formulario.get('metodologia_p1', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">5.3. Prácticas P2:</span> <span class="field-value">{datos_formulario.get('metodologia_p2', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">5.4. Prácticas P3:</span> <span class="field-value">{datos_formulario.get('metodologia_p3', 'No especificado')}</span></div>

        <h3 class="section-title">6. Criterios de Evaluación</h3>
        {'<table class="data-table"><thead><tr><th style="text-align:left;">Criterio Evaluado</th><th>Cursado</th><th>Final Reg.</th><th>Final Lib.</th><th>N/A</th></tr></thead><tbody>' + filas_criterios_html + '</tbody></table>' if filas_criterios_html else '<p>No se especificaron criterios.</p>'}
        <div class="field-row"><span class="field-label">Otros Criterios Específicos:</span> <span class="field-value">{datos_formulario.get('otros_criterios_eval', 'N/A')}</span></div>

        <h3 class="section-title">7. Condiciones de Regularidad y Sistema de Promoción</h3>
        <div class="field-row"><span class="field-label">7.1. Definición de las Actividades Obligatorias para acceder a la Regularidad:</span> <span class="field-value">{datos_formulario.get('actividades_obligatorias', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">7.2. % de Asistencia Exigido para Regularizar:</span> <span class="field-value">{datos_formulario.get('asistencia_req', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">7.3. % de Aprobación Exigido para Regularizar:</span> <span class="field-value">{datos_formulario.get('aprobacion_req', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">7.4. Cantidad de evaluaciones parciales:</span> <span class="field-value">{datos_formulario.get('cantidad_parciales', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">7.5. Modalidad y contenidos de evaluaciones sumativas durante la cursada:</span> <span class="field-value">{datos_formulario.get('eval_sumativas', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">7.6. Modalidad y contenidos de la evaluación complementaria para promoción:</span> <span class="field-value">{datos_formulario.get('eval_promocion', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">7.7. Criterio para decidir la calificación final por promoción:</span> <span class="field-value">{datos_formulario.get('calif_promocion', 'No especificado')}</span></div>

        <h3 class="section-title">8. Acreditación por Examen Final</h3>
        <div class="field-row"><span class="field-label">8.1. Modalidad de examen final para Regulares:</span> <span class="field-value">{datos_formulario.get('final_reg_mod', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">8.2. Contenidos a evaluar en examen final Regular:</span> <span class="field-value">{datos_formulario.get('final_reg_cont', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">8.3. Criterio de calificación final para Regulares:</span> <span class="field-value">{datos_formulario.get('final_reg_crit', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">8.4. Modalidad de examen final para Libres:</span> <span class="field-value">{datos_formulario.get('final_lib_mod', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">8.5. Criterio de calificación final para Libres:</span> <span class="field-value">{datos_formulario.get('final_lib_crit', 'No especificado')}</span></div>

        <h3 class="section-title">9. Bibliografía</h3>
        <div class="field-row"><span class="field-label">9.1. Bibliografía Obligatoria:</span> <span class="field-value">{datos_formulario.get('bib_obligatoria', 'No especificado')}</span></div>
        <div class="field-row"><span class="field-label">9.2. Bibliografía Complementaria:</span> <span class="field-value">{datos_formulario.get('bib_complementaria', 'No especificado')}</span></div>

        <h3 class="section-title">10. Adhesión a Programas Especiales</h3>
        <div class="field-row"><span class="field-label">Programas:</span> <span class="field-value">{str_progs}</span></div>
        <div class="field-row"><span class="field-label">Implementación:</span> <span class="field-value">{datos_formulario.get('desc_programas_text', 'N/A')}</span></div>

        <div class="footer">
            Documento generado el {fecha_impresion} hs — Sistema PANDA (FBioyF - UNR)
        </div>
    </body>
    </html>
    """
    return html

def generar_pdf_programa(datos_materia, datos_formulario, ruta_salida="programa_analitico.pdf", logo_path="logo_fbioyf.png"):
    """
    Función requerida por app.py. Convierte la plantilla HTML a un documento PDF.
    """
    html_content = generar_html_programa(datos_materia, datos_formulario, logo_path)
    
    try:
        from xhtml2pdf import pisa
        with open(ruta_salida, "wb") as f_out:
            pisa.CreatePDF(html_content, dest=f_out)
    except ImportError:
        # Si no está instalado xhtml2pdf, guardamos temporalmente el HTML para evitar caídas
        ruta_salida_html = ruta_salida.replace(".pdf", ".html")
        with open(ruta_salida_html, "w", encoding="utf-8") as f_out:
            f_out.write(html_content)
        return ruta_salida_html
        
    return ruta_salida