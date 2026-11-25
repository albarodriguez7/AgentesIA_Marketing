# Evalúa al redactor con webs reales: ¿cita solo los artículos que recibió?
from dotenv import load_dotenv

load_dotenv()

from langsmith import evaluate

from auditoria.agente_auditoria import agente
from rag.evaluar_redactor import citas_del_informe, citas_inventadas

DATASET_WEBS = "auditoria-primera-impresion"


def ejecutar_agente(inputs: dict) -> dict:
    # Target: pasa una web por el agente completo y devuelve lo que necesitamos evaluar
    resultado = agente.invoke({"url": inputs["url"]})
    return {
        "informe": resultado.get("informe"),
        "fuentes_legales": resultado.get("fuentes_legales"),
    }


def sin_citas_inventadas(outputs: dict) -> dict:
    # ¿Todas las citas del informe están entre las fuentes que recibió el redactor?
    if outputs["informe"] is None:
        return {"key": "sin_citas_inventadas", "score": None, "comment": "La web no se pudo descargar"}

    fuentes = outputs["fuentes_legales"]
    if fuentes is None:
        fuentes = []

    inventadas = citas_inventadas(outputs["informe"], fuentes)
    if len(inventadas) == 0:
        comentario = "Todas las citas están respaldadas"
    else:
        comentario = f"Citas inventadas: {inventadas}"
    return {"key": "sin_citas_inventadas", "score": len(inventadas) == 0, "comment": comentario}


def cita_cuando_hay_fuentes(outputs: dict) -> dict:
    # Si el redactor recibió fuentes legales, ¿las ha citado al menos una vez?
    fuentes = outputs["fuentes_legales"]
    if outputs["informe"] is None or not fuentes:
        return {"key": "cita_cuando_hay_fuentes", "score": None, "comment": "No había fuentes que citar"}

    citas = citas_del_informe(outputs["informe"])
    return {
        "key": "cita_cuando_hay_fuentes",
        "score": len(citas) > 0,
        "comment": f"Citas encontradas: {citas}",
    }


if __name__ == "__main__":
    evaluate(
        ejecutar_agente,
        data=DATASET_WEBS,
        evaluators=[sin_citas_inventadas, cita_cuando_hay_fuentes],
        experiment_prefix="redactor-citas",
        metadata={"tamaño_trozo": 500, "trozos_por_consulta": 2},
        max_concurrency=4,
    )