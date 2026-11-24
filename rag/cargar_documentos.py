from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CARPETA = Path(__file__).parent / "documentos"

URL_LSSI = "https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758"
URL_RGPD = "https://www.boe.es/buscar/doc.php?id=DOUE-L-2016-80807"

FUENTES = {
    "lssi_art10.txt": {"ley": "LSSI", "articulo": "10", "tema": "aviso legal", "url": URL_LSSI},
    "lssi_art22.txt": {"ley": "LSSI", "articulo": "22", "tema": "cookies", "url": URL_LSSI},
    "lssi_art39.txt": {"ley": "LSSI", "articulo": "39", "tema": "sanciones", "url": URL_LSSI},
    "rgpd_art13.txt": {"ley": "RGPD", "articulo": "13", "tema": "privacidad", "url": URL_RGPD},
}


def cargar_documentos() -> list[Document]:
    documentos = []
    for nombre_archivo, metadatos in FUENTES.items():
        texto = (CARPETA / nombre_archivo).read_text(encoding="utf-8")
        documentos.append(Document(page_content=texto, metadata=metadatos))
    return documentos


def trocear_documentos(documentos, tamaño=500, solape=50):
    troceador = RecursiveCharacterTextSplitter(chunk_size=tamaño, chunk_overlap=solape)   # Solape: cada trozo repite los últimos 50 caracteres del anterior.
    return troceador.split_documents(documentos)  # trocea todos los documentos y le pone a cada trozo los metadatos de su documento


if __name__ == "__main__":
    documentos = cargar_documentos()
    print(f"Documentos cargados: {len(documentos)}")

    trozos = trocear_documentos(documentos)
    print(f"Trozos: {len(trozos)}\n")

    for trozo in trozos[:3]:
        print(trozo.metadata)
        print(f"({len(trozo.page_content)} caracteres) {trozo.page_content[:150]}...\n")