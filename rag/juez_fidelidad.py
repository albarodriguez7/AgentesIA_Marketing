# IA juez: ¿lo que dice el informe sobre la ley está respaldado por las fuentes?

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from auditoria.informe import texto_fuentes_legales


class VeredictoFidelidad(BaseModel):
    afirmaciones_sin_respaldo: list[str] = Field(
        description="Cada frase del informe sobre la ley que NO está respaldada por las fuentes, "
        "con el motivo en una línea. Lista vacía si todo está respaldado."
    )
    fiel: bool = Field(description="True si TODAS las afirmaciones legales del informe están respaldadas por las fuentes")


INSTRUCCIONES_JUEZ = """Eres un revisor legal estricto pero justo.
Recibes un INFORME escrito para el dueño de una web y unas FUENTES LEGALES (textos oficiales de la ley).

Tu tarea: revisar SOLO las afirmaciones del informe sobre lo que exige la ley, las obligaciones legales o las sanciones.
Ignora el resto del informe (contacto, confianza, primera impresión...).

Para cada afirmación legal, pregúntate: ¿la INFORMACIÓN de esta frase está en las fuentes, aunque sea con otras palabras?

Está RESPALDADA (no es un fallo) si:
- dice lo mismo que la fuente con palabras más sencillas (por ejemplo, "tu email" cuando la ley dice "dirección de correo electrónico");
- resume o simplifica la fuente sin cambiar su significado;
- omite detalles que sí están en la fuente (no dar todas las cifras no es inventar).

Es un FALLO solo si:
- atribuye a un artículo una obligación que ese artículo no contiene;
- añade cifras, plazos o importes que no están en las fuentes;
- exagera: dice "siempre" u "obligatorio" donde la ley pone condiciones o rangos.

Apunta en afirmaciones_sin_respaldo SOLO los fallos, con el motivo en una línea.
Si dudas, o si tú mismo crees que no es un error, NO lo apuntes.
Si no hay fallos, deja la lista vacía y fiel = true."""

modelo_juez = init_chat_model("openai:gpt-4.1-mini").with_structured_output(VeredictoFidelidad)


def juzgar_fidelidad(informe: str, fuentes: list) -> VeredictoFidelidad:
    mensajes = [
        SystemMessage(INSTRUCCIONES_JUEZ),
        HumanMessage(f"INFORME:\n{informe}\n\n{texto_fuentes_legales(fuentes)}"),
    ]
    return modelo_juez.invoke(mensajes)