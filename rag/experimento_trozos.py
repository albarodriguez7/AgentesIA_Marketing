# Compara trozos de 500 y 1000 caracteres con el examen del buscador, en LangSmith
from dotenv import load_dotenv

load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langsmith import evaluate

from rag.cargar_documentos import cargar_documentos, trocear_documentos
from rag.evaluar_buscador import etiqueta
from rag.subir_dataset import NOMBRE_DATASET

TAMAÑOS = [500, 1000]


def crear_base_de_prueba(tamaño: int) -> Chroma:
    # Base en memoria (sin carpeta) con los textos troceados a ese tamaño
    base = Chroma(
        collection_name=f"prueba_{tamaño}",
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
        collection_metadata={"hnsw:space": "cosine"},
    )
    base.reset_collection()
    trozos = trocear_documentos(cargar_documentos(), tamaño=tamaño, solape=50)
    base.add_documents(trozos)
    print(f"Base de prueba con trozos de {tamaño}: {len(trozos)} trozos")
    return base


def crear_buscador(base):
    # Fabrica el target: una función que busca en ESTA base
    def buscador(inputs: dict) -> dict:
        resultados = base.similarity_search_with_relevance_scores(inputs["pregunta"], k=3)
        return {"articulos": [etiqueta(trozo) for trozo, puntuacion in resultados]}
    return buscador


def hit_1(outputs: dict, reference_outputs: dict) -> bool:
    # ¿El primer artículo encontrado es uno de los válidos?
    return outputs["articulos"][0] in reference_outputs["validos"]


def hit_3(outputs: dict, reference_outputs: dict) -> bool:
    # ¿Alguno de los 3 primeros es válido?
    for articulo in outputs["articulos"][:3]:
        if articulo in reference_outputs["validos"]:
            return True
    return False


if __name__ == "__main__":
    for tamaño in TAMAÑOS:
        base = crear_base_de_prueba(tamaño)
        evaluate(
            crear_buscador(base),
            data=NOMBRE_DATASET,
            evaluators=[hit_1, hit_3],
            experiment_prefix=f"trozos-{tamaño}",
            metadata={"tamaño": tamaño, "solape": 50, "k": 3},
        )