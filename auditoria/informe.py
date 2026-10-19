NOMBRES_COMPROBACIONES = {
    "telefono_clicable": "Teléfono clicable (se puede llamar con un toque)",
    "whatsapp": "Enlace a WhatsApp",
    "email_clicable": "Email clicable",
    "formulario": "Formulario de contacto",
    "https": "Conexión segura (HTTPS)",
    "textos_legales": "Aviso legal y política de privacidad",
    "opiniones": "Enlace a opiniones de clientes",
}

NOMBRES_CRITERIOS = {
    "que_ofrecen": "¿Se entiende qué ofrece?",
    "para_quien": "¿Se entiende para quién es?",
    "donde": "¿Se sabe dónde está?",
    "propuesta_de_valor": "¿Se entiende por qué elegirlo?",
}


def lineas_comprobaciones(comprobaciones: dict) -> list[str]:
    lineas = []
    for clave, valor in comprobaciones.items():
        nombre = NOMBRES_COMPROBACIONES.get(clave, clave)
        marca = "SÍ" if valor else "NO"
        lineas.append(f"- {nombre}: {marca}")
    return lineas


def formatear_resultados(estado: dict) -> str:
    lineas = [f"WEB ANALIZADA: {estado['url']}"]

    lineas.append("")
    lineas.append("CONVERSIÓN (¿le es fácil contactar?):")
    lineas += lineas_comprobaciones(estado["conversion"])

    lineas.append("")
    lineas.append("CONFIANZA (¿se fía?):")
    lineas += lineas_comprobaciones(estado["confianza"])

    lineas.append("")
    lineas.append("PRIMERA IMPRESIÓN (¿lo entiende?):")
    for nombre, criterio in estado["primera_impresion"]:
        pregunta = NOMBRES_CRITERIOS.get(nombre, nombre)
        linea = f"- {pregunta} {criterio.cumple.upper()}"
        if criterio.prueba:
            linea += f' (la web dice: "{criterio.prueba}")'
        lineas.append(linea)

    return "\n".join(lineas)