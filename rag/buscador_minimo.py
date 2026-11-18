from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

modelo = OpenAIEmbeddings(model="text-embedding-3-small")

DOCUMENTOS = [
    "Aviso legal: la web de una empresa debe indicar su nombre o razón social, su NIF, su dirección y un email de contacto.",
    "Política de privacidad: si la web recoge datos personales, debe explicar qué datos guarda, para qué los usa y cómo ejercer los derechos.",
    "Cookies: si la web usa cookies de análisis o de publicidad, necesita un aviso para pedir permiso antes de instalarlas.",
    "Formularios: junto a un formulario de contacto hay que informar de quién trata los datos y con qué finalidad.",
    "Accesibilidad: los textos deben tener buen contraste y las imágenes un texto alternativo que las describa.",
    "Velocidad: si una web tarda en cargar en el móvil, muchos visitantes se van antes de verla.",
]


def similitud(a: list, b: list) -> float:
    producto = sum(x * y for x, y in zip(a, b))
    largo_a = sum(x * x for x in a) ** 0.5
    largo_b = sum(y * y for y in b) ** 0.5
    return producto / (largo_a * largo_b)


def indexar(textos: list) -> list:
    vectores = modelo.embed_documents(textos)
    indice = []
    for texto, vector in zip(textos, vectores):
        indice.append({"texto": texto, "vector": vector})
    return indice


def por_similitud(ficha: dict) -> float:
    return ficha["similitud"]


def buscar(pregunta: str, indice: list, k: int = 2, minimo: float = 0.4) -> list:
    vector_pregunta = modelo.embed_query(pregunta)

    resultados = []
    for ficha in indice:
        parecido = similitud(vector_pregunta, ficha["vector"])
        if parecido >= minimo:
            resultados.append({"texto": ficha["texto"], "similitud": parecido})

    ordenados = sorted(resultados, key=por_similitud, reverse=True)
    return ordenados[:k]


if __name__ == "__main__":
    indice = indexar(DOCUMENTOS)

    preguntas = [
        "¿Necesito pedir permiso para usar Google Analytics?",
        "Mi web tarda mucho en abrir en el teléfono",
        "¿Cuál es la mejor receta de paella?",
        "¿Qué pasa si mi web NO tiene cookies?",
    ]

    for pregunta in preguntas:
        print(f"\n{pregunta}")
        resultados = buscar(pregunta, indice)
        if len(resultados) == 0:
            print("   (no he encontrado nada relevante)")
        for resultado in resultados:
            print(f"   {resultado['similitud']:.3f}  {resultado['texto']}")