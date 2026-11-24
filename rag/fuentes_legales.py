from dotenv import load_dotenv

from rag.buscar_legal import buscar


TROZOS_POR_CONSULTA = 2  # con trozos de 500, 2 trozos ≈ el texto de antes

CONSULTAS_TEXTOS_LEGALES = [
    {
        "consulta": "Información que el prestador de servicios debe facilitar: nombre o denominación social, domicilio, dirección de correo electrónico y número de identificación fiscal",
        "filtro": {"tema": "aviso legal"},
    },
    {
        "consulta": "Información que debe facilitarse al interesado cuando se obtienen sus datos personales: identidad del responsable, fines del tratamiento y derechos",
        "filtro": {"tema": "privacidad"},
    },
    {
        "consulta": "Multas por la comisión de infracciones muy graves, graves y leves",
        "filtro": {"tema": "sanciones"},
    },
]


def buscar_fuentes_legales(consultas: list) -> list[dict]:
    fuentes = []
    for consulta in consultas:
        resultados = buscar(consulta["consulta"], k=TROZOS_POR_CONSULTA, filtro=consulta["filtro"])
        for trozo, puntuacion in resultados:
            fuentes.append({
                "ley": trozo.metadata["ley"],
                "articulo": trozo.metadata["articulo"],
                "url": trozo.metadata["url"],
                "texto": trozo.page_content,
                "relevancia": round(puntuacion, 3),
            })
    return fuentes


if __name__ == "__main__":
    load_dotenv()

    fuentes = buscar_fuentes_legales(CONSULTAS_TEXTOS_LEGALES)
    print(f"Fuentes encontradas: {len(fuentes)}\n")

    for fuente in fuentes:
        print(f"[{fuente['ley']} art. {fuente['articulo']}]  relevancia {fuente['relevancia']}")
        print(f"{fuente['texto'][:200]}...\n")