from bs4 import BeautifulSoup

from auditoria.comprobaciones import comprobar_conversion, usa_https, tiene_textos_legales, tiene_opiniones, comprobar_confianza

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


def test_web_con_https_es_segura():
    assert usa_https("https://clinicaceodent.es/") is True


def test_web_con_http_no_es_segura():
    assert usa_https("http://clinicaceodent.es/") is False



def test_detecta_aviso_legal():
    pagina = crear_pagina('<a href="/aviso-legal">Aviso Legal</a>')
    assert tiene_textos_legales(pagina) is True


def test_detecta_politica_de_privacidad():
    pagina = crear_pagina('<a href="/privacidad">Política de privacidad</a>')
    assert tiene_textos_legales(pagina) is True


def test_sin_textos_legales():
    pagina = crear_pagina('<a href="/">Inicio</a><a href="/contacto">Contacto</a>')
    assert tiene_textos_legales(pagina) is False


def test_texto_legal_fuera_de_un_enlace_no_cuenta():
    pagina = crear_pagina("<p>Consulta nuestro aviso legal</p>")
    assert tiene_textos_legales(pagina) is False



def test_detecta_testimonios():
    pagina = crear_pagina('<a href="/testimonios/">Testimonios</a>')
    assert tiene_opiniones(pagina) is True


def test_detecta_opiniones_en_un_texto_largo():
    pagina = crear_pagina('<a href="/opiniones">Opiniones de nuestros pacientes</a>')
    assert tiene_opiniones(pagina) is True


def test_detecta_experiencias_como_en_ceodent():
    pagina = crear_pagina('<a href="/testimonios/">Experiencias</a>')
    assert tiene_opiniones(pagina) is True


def test_sin_opiniones():
    pagina = crear_pagina('<a href="/">Inicio</a><a href="/contacto">Contacto</a>')
    assert tiene_opiniones(pagina) is False


def test_testimonios_no_cuenta_como_texto_legal():
    pagina = crear_pagina('<a href="/testimonios/">Testimonios</a>')
    assert tiene_textos_legales(pagina) is False


def test_confianza_con_todo():
    pagina = crear_pagina('<a href="/aviso-legal">Aviso legal</a><a href="/testimonios/">Testimonios</a>')
    resultado = comprobar_confianza("https://clinica.es/", pagina)
    assert resultado == {"https": True, "textos_legales": True, "opiniones": True}


def test_confianza_sin_nada():
    pagina = crear_pagina('<a href="/">Inicio</a>')
    resultado = comprobar_confianza("http://clinica.es/", pagina)
    assert resultado == {"https": False, "textos_legales": False, "opiniones": False}