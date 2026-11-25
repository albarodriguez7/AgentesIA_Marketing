from rag.evaluar_redactor import citas_del_informe, citas_inventadas

FUENTES_FISIO = [
    {"ley": "LSSI", "articulo": "10"},
    {"ley": "RGPD", "articulo": "13"},
    {"ley": "LSSI", "articulo": "39"},
]


def test_encuentra_las_citas_en_orden():
    informe = "La ley exige que informes de quién eres (LSSI, art. 10). Además, debes explicar cómo tratas los datos (RGPD, art. 13)."
    assert citas_del_informe(informe) == ["LSSI art. 10", "RGPD art. 13"]


def test_informe_sin_citas():
    assert citas_del_informe("Tu web tiene una base sólida.") == []


def test_todas_las_citas_respaldadas():
    informe = "Quién eres (LSSI, art. 10), tus datos (RGPD, art. 13) y multas (LSSI, art. 39)."
    assert citas_inventadas(informe, FUENTES_FISIO) == []


def test_detecta_una_cita_inventada():
    informe = "Quién eres (LSSI, art. 10) y es una infracción leve (LSSI, art. 38)."
    assert citas_inventadas(informe, FUENTES_FISIO) == ["LSSI art. 38"]


def test_sin_fuentes_cualquier_cita_es_inventada():
    informe = "Recuerda cumplir la ley (LSSI, art. 10)."
    assert citas_inventadas(informe, []) == ["LSSI art. 10"]