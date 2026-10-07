"""
Sube a LangSmith las webs para evaluar la primera impresión.

Usa las mismas webs que el dataset de leads (leads/evaluaciones/dataset.json),
sin respuestas correctas: de momento se evalúa con señales de calidad y una IA evaluadora.
Se puede ejecutar varias veces: solo añade las webs que aún no estén.
"""

from dotenv import load_dotenv
from langsmith import Client

from leads.evaluaciones.crear_dataset import cargar_ejemplos

load_dotenv()

NOMBRE_DATASET = "auditoria-primera-impresion"


def extraer_url(lead: str) -> str:
    return lead.split()[1].rstrip(".")


if __name__ == "__main__":
    cliente = Client()
    urls = [extraer_url(ejemplo["lead"]) for ejemplo in cargar_ejemplos()]

    if cliente.has_dataset(dataset_name=NOMBRE_DATASET):
        dataset = cliente.read_dataset(dataset_name=NOMBRE_DATASET)
    else:
        dataset = cliente.create_dataset(
            dataset_name=NOMBRE_DATASET,
            description="Webs reales para evaluar la valoración de la primera impresión",
        )

    existentes = {ejemplo.inputs["url"] for ejemplo in cliente.list_examples(dataset_id=dataset.id)}
    nuevas = [{"inputs": {"url": url}} for url in urls if url not in existentes]

    if nuevas:
        cliente.create_examples(dataset_id=dataset.id, examples=nuevas)

    print(f"Dataset '{NOMBRE_DATASET}': {len(nuevas)} webs nuevas, {len(urls)} en total.")