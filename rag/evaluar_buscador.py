# Examen del buscador legal: ¿encuentra el artículo correcto para cada pregunta?

from dotenv import load_dotenv

load_dotenv()  # lee el .env y deja la clave de OpenAI disponible

from rag.buscar_legal import buscar

# Las respuestas correctas que has decidido tú en la hoja
PREGUNTAS = [
    {"pregunta": "¿Tengo que poner mi NIF en la web?", "validos": ["LSSI art. 10"]},
    {"pregunta": "¿Puedo usar cookies sin avisar a nadie?", "validos": ["LSSI art. 22", "RGPD art. 13"]},
    {"pregunta": "¿Qué pasa si no cumplo la ley de servicios de internet?", "validos": ["LSSI art. 39"]},
    {"pregunta": "Si alguien me deja su email en un formulario, ¿qué le tengo que contar?", "validos": ["RGPD art. 13"]},
    {"pregunta": "¿Tengo que decir cuánto tiempo guardo los datos de mis clientes?", "validos": ["RGPD art. 13"]},
    {"pregunta": "¿Tengo que indicar en qué registro mercantil está inscrita mi empresa?", "validos": ["LSSI art. 10"]},
    {"pregunta": "¿Puedo poner el píxel de Facebook en mi web?", "validos": ["LSSI art. 22"]},
    {"pregunta": "¿Me pueden prohibir trabajar en España?", "validos": ["LSSI art. 39"]},
    {"pregunta": "¿Tengo que mostrar los precios con los impuestos incluidos?", "validos": ["LSSI art. 10"]},
    {"pregunta": "¿Puede un cliente pedirme que borre sus datos?", "validos": ["RGPD art. 13"]},
    {"pregunta": "¿Necesito un banner de cookies?", "validos": ["LSSI art. 22"]},
    {"pregunta": "¿Cuál es la multa por una infracción leve?", "validos": ["LSSI art. 39"]},
    {"pregunta": "¿Debo poner un email de contacto en mi web?", "validos": ["LSSI art. 10", "RGPD art. 13"]},
    {"pregunta": "¿Tengo que avisar si uso los datos para algo distinto de lo que dije?", "validos": ["RGPD art. 13"]},
]


def etiqueta(trozo) -> str:
    # Convierte los metadatos de un trozo en el mismo formato que la hoja: 'LSSI art. 10'.
    return f"{trozo.metadata['ley']} art. {trozo.metadata['articulo']}"


def acierta(pregunta: str, validos: list, k: int) -> bool:
    # True si alguno de los k primeros trozos viene de un artículo válido.
    resultados = buscar(pregunta, k=k)
    for trozo, puntuacion in resultados:
        if etiqueta(trozo) in validos:
            return True
    return False


def nota(k: int) -> float:
    # hit@k: proporción de preguntas acertadas mirando los k primeros resultados.
    aciertos = 0
    for caso in PREGUNTAS:
        if acierta(caso["pregunta"], caso["validos"], k):
            aciertos += 1
    return aciertos / len(PREGUNTAS)


if __name__ == "__main__":
    # Detalle: qué saca primero el buscador en cada pregunta
    for caso in PREGUNTAS:
        trozo, puntuacion = buscar(caso["pregunta"], k=1)[0]
        marca = "✅" if etiqueta(trozo) in caso["validos"] else "❌"
        print(f"{marca} {caso['pregunta']}")
        print(f"   encontró: {etiqueta(trozo)} ({puntuacion:.3f}) · correcto: {caso['validos']}")

    print()
    for k in [1, 3]:
        print(f"hit@{k}: {nota(k):.2f}")