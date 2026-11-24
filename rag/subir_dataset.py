# Sube las preguntas del examen del buscador a LangSmith como dataset
from dotenv import load_dotenv

load_dotenv()  # carga la clave de LangSmith del .env

from langsmith import Client
from rag.evaluar_buscador import PREGUNTAS

NOMBRE_DATASET = "rag-textos-legales"


def subir_dataset():
    cliente = Client()

    if cliente.has_dataset(dataset_name=NOMBRE_DATASET):
        print("El dataset ya existe, no lo vuelvo a crear.")
        return

    dataset = cliente.create_dataset(
        dataset_name=NOMBRE_DATASET,
        description="14 preguntas de cliente con el artículo de ley correcto",
    )
    cliente.create_examples(
        dataset_id=dataset.id,
        inputs=[{"pregunta": caso["pregunta"]} for caso in PREGUNTAS],
        outputs=[{"validos": caso["validos"]} for caso in PREGUNTAS],
    )
    print(f"Dataset creado con {len(PREGUNTAS)} ejemplos.")


if __name__ == "__main__":
    subir_dataset()