from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from auditoria.comprobaciones import (
    comprobar_confianza,
    comprobar_conversion,
    crear_soup,
    descargar_html,
)
from auditoria.primera_impresion import (
    ValoracionPrimeraImpresion,
    extraer_primera_impresion,
    valorar_primera_impresion,
)

from auditoria.informe import formatear_resultados, redactar_informe

from rag.fuentes_legales import CONSULTAS_TEXTOS_LEGALES, buscar_fuentes_legales


class EstadoAuditoria(TypedDict):
    url: str
    html: str | None
    conversion: dict | None
    confianza: dict | None
    primera_impresion: ValoracionPrimeraImpresion | None
    informe: str | None
    fuentes_legales: list | None


def descargar(estado: EstadoAuditoria) -> dict:
    soup = descargar_html(estado["url"])
    if soup is None:
        return {"html": None}
    return {"html": str(soup)}  # str(soup) convierte el soup de vuelta en texto HTML





def especialista_conversion(estado: EstadoAuditoria) -> dict:
    soup = crear_soup(estado["html"])
    return {"conversion": comprobar_conversion(soup)}


def especialista_confianza(estado: EstadoAuditoria) -> dict:
    soup = crear_soup(estado["html"])
    return {"confianza": comprobar_confianza(estado["url"], soup)}


def especialista_primera_impresion(estado: EstadoAuditoria) -> dict:
    soup = crear_soup(estado["html"])
    impresion = extraer_primera_impresion(soup)
    return {"primera_impresion": valorar_primera_impresion(impresion)}


def buscar_ley(estado):
    if estado["confianza"]["textos_legales"]:
        return {"fuentes_legales": []}
    return {"fuentes_legales": buscar_fuentes_legales(CONSULTAS_TEXTOS_LEGALES)}


def redactar(estado):
    return {"informe": redactar_informe(estado)}



ESPECIALISTAS = [
    "especialista_conversion",
    "especialista_confianza",
    "especialista_primera_impresion",
]


def decidir_tras_descarga(estado: EstadoAuditoria) -> list[str] | str:
    if estado["html"] is None:
        return END
    return ESPECIALISTAS


constructor = StateGraph(EstadoAuditoria)
constructor.add_node("descargar", descargar)
constructor.add_node("especialista_conversion", especialista_conversion)
constructor.add_node("especialista_confianza", especialista_confianza)
constructor.add_node("especialista_primera_impresion", especialista_primera_impresion)
constructor.add_node("redactar", redactar)
constructor.add_node("buscar_ley", buscar_ley)

constructor.add_edge(START, "descargar")
constructor.add_conditional_edges("descargar", decidir_tras_descarga, ESPECIALISTAS + [END])  
constructor.add_edge(ESPECIALISTAS, "buscar_ley")
constructor.add_edge("buscar_ley", "redactar")
constructor.add_edge("redactar", END)

# Es como escribir esto:
# constructor.add_edge("especialista_conversion", END)
# constructor.add_edge("especialista_confianza", END)
# constructor.add_edge("especialista_primera_impresion", END)


agente = constructor.compile()




if __name__ == "__main__":
    load_dotenv()
    resultado = agente.invoke({"url": "https://fisioterapiadomiciliomanuel.com/"})

    if resultado["html"] is None:
        print("No se pudo descargar la web")
    else:
        print(formatear_resultados(resultado))
        print("\n========== INFORME ==========\n")
        print(resultado["informe"])
