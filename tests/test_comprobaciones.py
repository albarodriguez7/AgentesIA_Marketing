from bs4 import BeautifulSoup

from auditoria.comprobaciones import comprobar_conversion


def crear_pagina(contenido: str) -> BeautifulSoup:
    return BeautifulSoup(f"<html><body>{contenido}</body></html>", "html.parser")


def test_detecta_whatsapp_con_wa_me():
    pagina = crear_pagina('<a href="https://wa.me/34600000000">Escríbenos</a>')
    assert comprobar_conversion(pagina)["whatsapp"] is True


def test_detecta_whatsapp_con_wa_link():
    pagina = crear_pagina('<a href="https://wa.link/567bgr">Escríbenos</a>')
    assert comprobar_conversion(pagina)["whatsapp"] is True


def test_detecta_whatsapp_por_el_texto_del_enlace():
    pagina = crear_pagina('<a href="https://bit.ly/abc123">Escríbenos por WhatsApp</a>')
    assert comprobar_conversion(pagina)["whatsapp"] is True


def test_sin_whatsapp():
    pagina = crear_pagina('<a href="/contacto">Contacto</a>')
    assert comprobar_conversion(pagina)["whatsapp"] is False


def test_detecta_telefono_clicable():
    pagina = crear_pagina('<a href="tel:+34913825257">Llamar</a>')
    assert comprobar_conversion(pagina)["telefono_clicable"] is True


def test_telefono_solo_escrito_no_cuenta_como_clicable():
    pagina = crear_pagina("<p>Llámanos al 913 82 52 57</p>")
    assert comprobar_conversion(pagina)["telefono_clicable"] is False