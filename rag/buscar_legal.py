from dotenv import load_dotenv

from rag.base_vectorial import abrir_base


def buscar(pregunta: str, k: int = 3, filtro: dict | None = None) -> list:
    base = abrir_base()
    return base.similarity_search_with_relevance_scores(pregunta, k=k, filter=filtro)


def mostrar(pregunta: str, resultados: list) -> None:
    print(f"\n{pregunta}")
    for trozo, puntuacion in resultados:
        ley = trozo.metadata["ley"]
        articulo = trozo.metadata["articulo"]
        print(f"   {puntuacion:.3f}  [{ley} art. {articulo}] {trozo.page_content[:90]}...")


if __name__ == "__main__":
    load_dotenv()

    preguntas = [
        "¿Qué datos de la empresa tienen que aparecer en su web?",
        "¿Hay que pedir permiso para poner Google Analytics?",
        "¿Qué tengo que explicar en un formulario de contacto sobre los datos que recojo?",
        "¿Cuánto me pueden multar?",
    ]
    for pregunta in preguntas:
        mostrar(pregunta, buscar(pregunta))

    pregunta = "¿Cuánto me pueden multar?"
    mostrar(f"{pregunta}  (solo LSSI)", buscar(pregunta, filtro={"ley": "LSSI"}))   # El filtro: descarta todos los trozos que no tengan "ley": "LSSI" en sus metadatos.