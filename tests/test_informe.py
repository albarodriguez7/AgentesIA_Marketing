from auditoria.informe import mejoras_ordenadas, texto_prioridades
from auditoria.primera_impresion import Criterio, ValoracionPrimeraImpresion


def crear_estado(conversion: dict, confianza: dict, impresion: dict) -> dict:
    valoracion = ValoracionPrimeraImpresion(
        que_ofrecen=Criterio(cumple=impresion["que_ofrecen"], prueba=""),
        para_quien=Criterio(cumple=impresion["para_quien"], prueba=""),
        donde=Criterio(cumple=impresion["donde"], prueba=""),
        propuesta_de_valor=Criterio(cumple=impresion["propuesta_de_valor"], prueba=""),
    )
    return {
        "url": "https://ejemplo.es",
        "conversion": conversion,
        "confianza": confianza,
        "primera_impresion": valoracion,
    }


TODO_SI = {"que_ofrecen": "si", "para_quien": "si", "donde": "si", "propuesta_de_valor": "si"}


def test_web_sin_fallos_no_tiene_mejoras():
    estado = crear_estado(
        conversion={"telefono_clicable": True, "whatsapp": True},
        confianza={"https": True, "opiniones": True},
        impresion=TODO_SI,
    )
    assert mejoras_ordenadas(estado) == []


def test_https_va_antes_que_todo():
    estado = crear_estado(
        conversion={"email_clicable": False},
        confianza={"https": False},
        impresion=TODO_SI,
    )
    assert mejoras_ordenadas(estado) == ["https", "email_clicable"]


def test_web_con_muchos_fallos_sale_ordenada_por_prioridad():
    # Los mismos resultados que la fisioterapia a domicilio
    estado = crear_estado(
        conversion={"telefono_clicable": True, "whatsapp": False,
                    "email_clicable": True, "formulario": False},
        confianza={"https": True, "textos_legales": False, "opiniones": False},
        impresion={"que_ofrecen": "parcialmente", "para_quien": "no",
                   "donde": "no", "propuesta_de_valor": "parcialmente"},
    )
    assert mejoras_ordenadas(estado) == [
        "que_ofrecen",
        "donde",
        "para_quien",
        "formulario",
        "propuesta_de_valor",
        "whatsapp",
        "opiniones",
        "textos_legales",
    ]



def test_texto_prioridades_numera_con_nombres_legibles():
    estado = crear_estado(
        conversion={"email_clicable": False},
        confianza={"https": False},
        impresion=TODO_SI,
    )
    assert texto_prioridades(estado) == (
        "MEJORAS EN ORDEN DE PRIORIDAD:\n"
        "1. Conexión segura (HTTPS)\n"
        "2. Email clicable"
    )


def test_texto_prioridades_sin_mejoras():
    estado = crear_estado(
        conversion={"telefono_clicable": True},
        confianza={"https": True},
        impresion=TODO_SI,
    )
    assert texto_prioridades(estado) == "MEJORAS EN ORDEN DE PRIORIDAD: ninguna"