# Examen del juez de fidelidad con casos cuya respuesta ya conocemos

from dotenv import load_dotenv

load_dotenv()

from rag.fuentes_legales import CONSULTAS_TEXTOS_LEGALES, buscar_fuentes_legales
from rag.juez_fidelidad import juzgar_fidelidad

INICIO = "Aviso legal: No hemos encontrado en la web un aviso legal ni una política de privacidad. "

CASOS = [
    {
        "nombre": "Fiel (el informe real de la fisio)",
        "informe": INICIO + "La ley exige que informes sobre quién eres, dónde estás y cómo contactarte de forma clara "
        "y accesible (LSSI, art. 10). Además, cuando recoges datos personales, debes explicar cómo los tratas y cuánto "
        "tiempo los conservas (RGPD, art. 13). La normativa prevé multas según la gravedad de la infracción (LSSI, art. 39).",
        "esperado": True,
    },
    {
        "nombre": "Obligación inventada (horario)",
        "informe": INICIO + "La ley exige que publiques tu horario de apertura en la página principal (LSSI, art. 10).",
        "esperado": False,
    },
    {
        "nombre": "Plazo inventado",
        "informe": INICIO + "Debes borrar los datos de tus clientes como máximo a los 2 años (RGPD, art. 13).",
        "esperado": False,
    },
    {
        "nombre": "Multa exagerada",
        "informe": INICIO + "No tener aviso legal se castiga siempre con una multa de 600.000 euros (LSSI, art. 39).",
        "esperado": False,
    },
]

if __name__ == "__main__":
    fuentes = buscar_fuentes_legales(CONSULTAS_TEXTOS_LEGALES)
    aciertos = 0
    for caso in CASOS:
        veredicto = juzgar_fidelidad(caso["informe"], fuentes)
        acierta = veredicto.fiel == caso["esperado"]
        if acierta:
            aciertos += 1
        marca = "✅" if acierta else "❌"
        print(f"{marca} {caso['nombre']} → fiel={veredicto.fiel} (esperado {caso['esperado']})")
        for afirmacion in veredicto.afirmaciones_sin_respaldo:
            print(f"     · {afirmacion}")
    print(f"\nEl juez acierta {aciertos} de {len(CASOS)}")