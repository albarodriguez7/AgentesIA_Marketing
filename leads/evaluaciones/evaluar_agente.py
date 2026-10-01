from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langsmith import Client

from leads.agente_grafo import agente
from leads.evaluar_lead import MIN_SEDES, MAX_SEDES

load_dotenv()

NOMBRE_DATASET = "leads-cualificacion"    # El nombre que se ha puesto en LangSmith al dataset


# Definido en "evaluar_lead.py"
# MIN_SEDES = 2
# MAX_SEDES = 10

def calcular_tramo(numero_sedes: int | None) -> str:
    if numero_sedes is None:
        return "desconocido"
    if numero_sedes < MIN_SEDES:
        return "1"
    if numero_sedes <= MAX_SEDES:
        return "2 a 10"
    return "mas de 10"


def ejecutar_agente(inputs: dict) -> dict:
    resultado = agente.invoke({
        "messages": [HumanMessage(inputs["lead"])],
        "datos": None,
        "puntos": None,
        "accion": None,
    })
    datos = resultado["datos"]    # Definí en "agente_grafo.py" que  --> datos: DatosLead | None   por eso se que lo que hay dentro de "datos" son esos "campos"
    return {
        "sector": datos.sector,
        "en_madrid": datos.en_madrid,
        "tramo_sedes": calcular_tramo(datos.numero_sedes),       # agente.invoke(...)  →  resultado (la ficha final)
                                                                                          # └─ ["datos"]  →  DatosLead (lo rellenó el nodo extraer)
                                                                                                             #  └─ .numero_sedes  →  4
        "accion": resultado["accion"],
    }


# Evaluators: 
# Breve explicacion: "outputs" es el diccionario que devuelve la funcion "ejecutar_agente" y "reference_outputs" es el diccionario que yo he creado a mano (crear_dataset.py)
# Entonces depués los evaluators lo que hacen es comparar ambos diccionarios para ver si coinciden los resultados




def sector_correcto(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["sector"] == reference_outputs["sector"]


def madrid_correcto(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["en_madrid"] == reference_outputs["en_madrid"]


def sedes_correctas(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["tramo_sedes"] == reference_outputs["tramo_sedes"]


def accion_correcta(outputs: dict, reference_outputs: dict) -> bool:
    return outputs["accion"] == reference_outputs["accion"]


if __name__ == "__main__":
    cliente = Client()
    cliente.evaluate(    # EVALUATE() es quien hace todo, conecta los dos dicts(outputs y reference_outputs) para que "evaluators" ejecute
        ejecutar_agente,   
        data=NOMBRE_DATASET,
        evaluators=[sector_correcto, madrid_correcto, sedes_correctas, accion_correcta],
        experiment_prefix="grafo-v2",  # este nombre se lo doy yo
        max_concurrency=2,    # ejecuta 2 leads a la vez, en paralelo, como hacía batch
    ) 