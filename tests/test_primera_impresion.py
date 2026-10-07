from bs4 import BeautifulSoup

from auditoria.primera_impresion import extraer_primera_impresion


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