from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage





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




INSTRUCCIONES_REDACTOR = """Eres un consultor de marketing local que escribe al dueño de un pequeño negocio.
Recibirás los resultados de una auditoría de su web. Escribe un informe breve para él.

Cómo escribirlo:
- Lenguaje sencillo, sin tecnicismos. Habla de "tu web" y trata al dueño de tú.
- Empieza con una frase que resuma cómo está la web.
- Después, "Lo que ya funciona bien": 2 o 3 puntos, muy breves.
- Después, "Lo que mejoraría primero": SOLO los puntos que en la auditoría salen como NO o PARCIALMENTE, ordenados de más a menos importante (como máximo 3). Si solo hay uno, pon solo uno. En cada uno, di qué pasa, por qué le hace perder clientes y qué haría para arreglarlo.
- Si un resultado incluye una frase de la web, puedes citarla para que el dueño vea a qué te refieres.

Reglas:
- Usa solo la información de la auditoría. No inventes datos sobre el negocio.
- Si un apartado está bien, dilo. No te inventes problemas.
- Máximo 200 palabras.
- No propongas mejoras sobre cosas que la auditoría no ha revisado (por ejemplo, imágenes, diseño o redes sociales).
"""


def redactar_informe(estado: dict) -> str:
    modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0.3)
    mensajes = [
        SystemMessage(INSTRUCCIONES_REDACTOR),
        HumanMessage(formatear_resultados(estado)),
    ]
    respuesta = modelo.invoke(mensajes)
    return respuesta.content