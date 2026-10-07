from bs4 import BeautifulSoup

from auditoria.primera_impresion import (
    Criterio,
    ValoracionPrimeraImpresion,
    criterios_sin_prueba_valida,
    extraer_primera_impresion,
    prueba_es_valida,
)


def crear_pagina(contenido: str) -> BeautifulSoup:
    return BeautifulSoup(f"<html><body>{contenido}</body></html>", "html.parser")


def test_separa_las_palabras_que_estan_en_etiquetas_distintas():
    pagina = crear_pagina("<h1>Dentistas a tu<span>disposición</span></h1>")
    assert extraer_primera_impresion(pagina)["h1"] == ["Dentistas a tu disposición"]


def test_web_sin_nada_devuelve_todo_vacio():
    pagina = crear_pagina("")
    assert extraer_primera_impresion(pagina) == {
        "titulo": "",
        "descripcion": "",
        "h1": [],
        "subtitulos": [],
        "parrafos": [],
    }


def test_descarta_los_parrafos_demasiado_cortos():
    pagina = crear_pagina("<p>Ver más</p><p>Somos una clínica dental familiar con más de 25 años de experiencia.</p>")
    assert extraer_primera_impresion(pagina)["parrafos"] == [
        "Somos una clínica dental familiar con más de 25 años de experiencia."
    ]


def test_limita_el_numero_de_subtitulos():
    pagina = crear_pagina("".join(f"<h2>Servicio {n}</h2>" for n in range(8)))
    assert len(extraer_primera_impresion(pagina)["subtitulos"]) == 5




# --- Comprobar las pruebas de la IA ---

TEXTO_WEB = "TÍTULO: CeoDent\nPÁRRAFOS: Especialistas en odontología   integral para niños y adultos , con un enfoque preventivo."


def test_prueba_copiada_de_la_web_es_valida():
    criterio = Criterio(cumple="si", prueba="odontología integral para niños y adultos")
    assert prueba_es_valida(criterio, TEXTO_WEB) is True


def test_prueba_inventada_no_es_valida():
    criterio = Criterio(cumple="si", prueba="la mejor clínica de Madrid")
    assert prueba_es_valida(criterio, TEXTO_WEB) is False


def test_mayusculas_y_espacios_de_mas_no_importan():
    criterio = Criterio(cumple="si", prueba="ESPECIALISTAS en odontología integral")
    assert prueba_es_valida(criterio, TEXTO_WEB) is True


def test_si_no_cumple_no_hace_falta_prueba():
    criterio = Criterio(cumple="no", prueba="")
    assert prueba_es_valida(criterio, TEXTO_WEB) is True


def test_si_cumple_sin_prueba_no_es_valida():
    criterio = Criterio(cumple="parcialmente", prueba="")
    assert prueba_es_valida(criterio, TEXTO_WEB) is False


def test_lista_los_criterios_con_prueba_no_valida():
    valoracion = ValoracionPrimeraImpresion(
        que_ofrecen=Criterio(cumple="si", prueba="odontología integral"),
        para_quien=Criterio(cumple="si", prueba="para niños y adultos"),
        donde=Criterio(cumple="si", prueba="en el centro de Madrid"),
        propuesta_de_valor=Criterio(cumple="no", prueba=""),
    )
    assert criterios_sin_prueba_valida(valoracion, TEXTO_WEB) == ["donde"]