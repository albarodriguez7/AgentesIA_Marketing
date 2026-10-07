import sys

from dotenv import load_dotenv
from langsmith import Client

from auditoria.comprobaciones import descargar_html
from auditoria.primera_impresion import (
    ValoracionPrimeraImpresion,
    criterios_sin_prueba_valida,
    extraer_primera_impresion,
    formatear_impresion,
    valorar_primera_impresion,
)

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

load_dotenv()

NOMBRE_DATASET = "auditoria-primera-impresion"


class Veredicto(BaseModel):
    razonamiento: str = Field(
        description="Una frase explicando si la prueba habla de lo que pregunta el criterio."
    )
    prueba_pertinente: bool = Field(
        description="True si la prueba demuestra lo que pregunta el criterio. False si habla de otra cosa."
    )


class JuicioPrimeraImpresion(BaseModel):
    que_ofrecen: Veredicto
    para_quien: Veredicto
    donde: Veredicto
    propuesta_de_valor: Veredicto


INSTRUCCIONES_JUEZ = """Eres un revisor de calidad de auditorías de marketing.
Otra IA ha valorado la primera impresión de una web y, para cada criterio, ha dado una prueba: una frase copiada de la web.

Tu trabajo NO es repetir la valoración. Solo tienes que decidir, para cada criterio, si la prueba es PERTINENTE: si de verdad habla de lo que pregunta ese criterio.

Ejemplo de prueba NO pertinente: para "¿Queda claro dónde está?", la frase "Enviamos a toda España" habla de envíos, no de dónde está el negocio.

Si un criterio tiene la valoración "no", su prueba está vacía a propósito: márcala como pertinente."""




# Es la funcion que se evalua, es como si fuera la de ejecutar_agente en leads
def ejecutar_especialista(inputs: dict) -> dict:
    soup = descargar_html(inputs["url"])
    if soup is None:
        return {"descargada": False, "texto": "", "valoracion": None}

    impresion = extraer_primera_impresion(soup)
    valoracion = valorar_primera_impresion(impresion)
    return {
        "descargada": True,
        "texto": formatear_impresion(impresion),
        "valoracion": valoracion.model_dump(),   # convierte el formulario de Pydantic en un diccionario normal
    }


def web_descargada(outputs: dict) -> bool:
    return outputs["descargada"]


def pruebas_en_la_web(outputs: dict) -> dict:
    if not outputs["descargada"]:
        return {"key": "pruebas_en_la_web", "score": None, "comment": "La web no se pudo descargar"}

    valoracion = ValoracionPrimeraImpresion.model_validate(outputs["valoracion"])
    sin_prueba = criterios_sin_prueba_valida(valoracion, outputs["texto"])
    return {
        "key": "pruebas_en_la_web",
        "score": len(sin_prueba) == 0,
        "comment": f"Criterios sin prueba válida: {sin_prueba}",
    }




def formatear_para_juez(valoracion: dict) -> str:
    bloques = []
    for nombre, criterio in valoracion.items():
        pregunta = ValoracionPrimeraImpresion.model_fields[nombre].description   # le pregunta al formulario del especialista (ValoracionPrimeraImpresion) qué instrucciones le dimos para ese criterio
        bloques.append(
            f"CRITERIO: {nombre}\n"
            f"PREGUNTA: {pregunta}\n"
            f"VALORACIÓN: {criterio['cumple']}\n"
            f"PRUEBA: {criterio['prueba']}"
        )
    return "\n\n".join(bloques)


def pruebas_pertinentes(outputs: dict) -> dict:
    if not outputs["descargada"]:
        return {"key": "pruebas_pertinentes", "score": None, "comment": "La web no se pudo descargar"}

    modelo = init_chat_model("openai:gpt-4.1", temperature=0)
    juez = modelo.with_structured_output(JuicioPrimeraImpresion)
    juicio = juez.invoke([
        SystemMessage(INSTRUCCIONES_JUEZ),
        HumanMessage(formatear_para_juez(outputs["valoracion"])),
    ])

    fallos = []
    for nombre, veredicto in juicio:
        if not veredicto.prueba_pertinente:
            fallos.append(f"{nombre}: {veredicto.razonamiento}")

    return {
        "key": "pruebas_pertinentes",
        "score": len(fallos) == 0,
        "comment": " | ".join(fallos) if fallos else "Todas las pruebas son pertinentes",
    }



if __name__ == "__main__":
    Client().evaluate(
        ejecutar_especialista,
        data=NOMBRE_DATASET,
        evaluators=[web_descargada, pruebas_en_la_web, pruebas_pertinentes],
        experiment_prefix=sys.argv[1] if len(sys.argv) > 1 else "primera-impresion-v1",
        max_concurrency=4,
    )