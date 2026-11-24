from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from rag.cargar_documentos import cargar_documentos, trocear_documentos

CARPETA_CHROMA = Path(__file__).parent / "chroma_db"
COLECCION = "textos_legales"


def abrir_base() -> Chroma:
    return Chroma(
        collection_name=COLECCION,
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=str(CARPETA_CHROMA),  # La carpeta del disco donde se guarda todo. Convierte el Path en texto porque Chroma lo necesita así
        collection_metadata={"hnsw:space": "cosine"},  # medir el parecido por coseno
    )


def indexar() -> int:
    base = abrir_base()
    base.reset_collection()
    trozos = trocear_documentos(cargar_documentos())
    base.add_documents(trozos)
    return len(trozos)


if __name__ == "__main__":
    load_dotenv()
    cantidad = indexar()
    print(f"Guardados {cantidad} trozos en {CARPETA_CHROMA}")