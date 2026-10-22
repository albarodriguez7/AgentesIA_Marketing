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


VEREDICTOS = {
    "si": "SÍ",
    "parcialmente": "PARCIALMENTE",
    "no": "NO",
}



PRIORIDAD = {
    "https": 1,
    "que_ofrecen": 2,
    "donde": 3,
    "telefono_clicable": 4,
    "para_quien": 5,
    "formulario": 6,
    "propuesta_de_valor": 7,
    "whatsapp": 8,
    "opiniones": 9,
    "textos_legales": 10,
    "email_clicable": 11,
}


def prioridad(nombre: str) -> int:
    return PRIORIDAD.get(nombre, 99)


def mejoras_ordenadas(estado: dict) -> list[str]:
    mejoras = []

    for area in ["conversion", "confianza"]:
        for nombre, valor in estado[area].items():
            if not valor:
                mejoras.append(nombre)

    for nombre, criterio in estado["primera_impresion"]:
        if criterio.cumple != "si":
            mejoras.append(nombre)

    return sorted(mejoras, key=prioridad)




def nombre_legible(clave: str) -> str:
    if clave in NOMBRES_COMPROBACIONES:
        return NOMBRES_COMPROBACIONES[clave]
    return NOMBRES_CRITERIOS.get(clave, clave)


def texto_prioridades(estado: dict) -> str:
    mejoras = mejoras_ordenadas(estado)
    if len(mejoras) == 0:
        return "MEJORAS EN ORDEN DE PRIORIDAD: ninguna"

    lineas = ["MEJORAS EN ORDEN DE PRIORIDAD:"]
    for numero, clave in enumerate(mejoras, start=1):
        lineas.append(f"{numero}. {nombre_legible(clave)}")
    return "\n".join(lineas)





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
        linea = f"- {pregunta} {VEREDICTOS[criterio.cumple]}"
        if criterio.prueba:
            linea += f' (la web dice: "{criterio.prueba}")'
        lineas.append(linea)

    return "\n".join(lineas)




INSTRUCCIONES_REDACTOR = """Eres un consultor de marketing digital. Escribes al dueño de un pequeño negocio para explicarle qué tal funciona su web para conseguir clientes, a partir de una auditoría.

Recibes:
- Los resultados de la auditoría, por áreas.
- Una lista de MEJORAS EN ORDEN DE PRIORIDAD, ya decidida.

Escribe el informe con esta estructura:

1. Una frase de resumen con la valoración general.

2. "Lo que ya funciona bien": de 2 a 3 puntos, solo con cosas que en la auditoría salen como SÍ.

3. "Lo que mejoraría primero": las mejoras de la lista, EN EL MISMO ORDEN y como máximo las 3 primeras. No cambies el orden ni añadas otras. Si la lista dice "ninguna", escribe que no hay nada urgente que mejorar. Empieza cada mejora con un título corto que diga qué hacer (por ejemplo, "Explica qué servicios ofreces"), no con el nombre de la comprobación. Después, explica en una o dos frases qué pasa y por qué le hace perder clientes.

4. Solo si en la auditoría el aviso legal y la política de privacidad salen como NO: termina con un párrafo aparte que empiece por "Aviso legal:", explicando que la ley obliga a tenerlos en una web de negocio y que no tenerlos puede acarrear sanciones. Hazlo aunque no esté entre las 3 primeras mejoras.

Reglas:
- Usa solo la información de la auditoría. No propongas mejoras sobre cosas que la auditoría no ha revisado (por ejemplo, imágenes, diseño o redes sociales).
- Sé prudente: la auditoría solo comprueba si existen enlaces o elementos, no si su contenido es correcto. Di "hay un enlace a la política de privacidad", no "tienes toda la información legal en regla". Cuando algo sale como NO, di "no hemos encontrado...", no "no tienes...".
- Tutea al dueño, con un tono cercano y profesional, sin tecnicismos.
- Máximo 250 palabras.
"""




def redactar_informe(estado: dict) -> str:
    modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0.3)
    mensajes = [
        SystemMessage(INSTRUCCIONES_REDACTOR),
        HumanMessage(formatear_resultados(estado) + "\n\n" + texto_prioridades(estado)),
    ]
    respuesta = modelo.invoke(mensajes)
    return respuesta.content


