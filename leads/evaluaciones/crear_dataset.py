"""
Sube a LangSmith los leads de dataset.json.

Se puede ejecutar todas las veces que haga falta: crea el dataset si no existe,
añade los leads nuevos, actualiza los que hayan cambiado (respuesta correcta, caso o prueba)
y borra de LangSmith los que ya no estén en dataset.json.
Así dataset.json (que está en Git) es la única fuente de verdad del dataset.
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

NOMBRE_DATASET = "leads-cualificacion"
RUTA_DATASET = Path(__file__).with_name("dataset.json")


def cargar_ejemplos() -> list[dict]:
    with open(RUTA_DATASET, encoding="utf-8") as archivo:
        return json.load(archivo)


if __name__ == "__main__":
    cliente = Client()
    ejemplos = cargar_ejemplos()

    if cliente.has_dataset(dataset_name=NOMBRE_DATASET):
        dataset = cliente.read_dataset(dataset_name=NOMBRE_DATASET)
    else:
        dataset = cliente.create_dataset(
            dataset_name=NOMBRE_DATASET,
            description="Leads reales con la respuesta correcta comprobada a mano",
        )

    # Los ejemplos que ya están en LangSmith, indexados por el texto del lead
    existentes = {e.inputs["lead"]: e for e in cliente.list_examples(dataset_id=dataset.id)}

    nuevos, actualizados = [], 0
    for ejemplo in ejemplos:
        actual = existentes.get(ejemplo["lead"])
        metadata = {"caso": ejemplo["caso"], "prueba": ejemplo["prueba"]}
        if actual is None:
            nuevos.append({"inputs": {"lead": ejemplo["lead"]}, "outputs": ejemplo["esperado"], "metadata": metadata})
        elif actual.outputs != ejemplo["esperado"] or {k: (actual.metadata or {}).get(k) for k in metadata} != metadata:
            cliente.update_example(example_id=actual.id, outputs=ejemplo["esperado"], metadata=metadata)
            actualizados += 1

    if nuevos:
        cliente.create_examples(dataset_id=dataset.id, examples=nuevos)

    # Si se cambia el texto de un lead en dataset.json, el antiguo se queda en LangSmith: lo borramos
    leads_actuales = {ejemplo["lead"] for ejemplo in ejemplos}
    sobrantes = [e for lead, e in existentes.items() if lead not in leads_actuales]
    for ejemplo in sobrantes:
        cliente.delete_example(example_id=ejemplo.id)

    print(f"Dataset '{NOMBRE_DATASET}': {len(nuevos)} nuevos, {actualizados} actualizados, "
          f"{len(sobrantes)} borrados, {len(ejemplos)} en total.")
