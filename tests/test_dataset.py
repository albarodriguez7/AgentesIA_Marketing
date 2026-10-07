import json
from pathlib import Path

import pytest

from leads.evaluar_lead import DatosLead, decidir, puntuar

RUTA_DATASET = Path(__file__).resolve().parents[1] / "leads" / "evaluaciones" / "dataset.json"
EJEMPLOS = json.loads(RUTA_DATASET.read_text(encoding="utf-8"))

# Un número de sedes representativo de cada tramo, para poder aplicar las reglas
SEDES_POR_TRAMO = {"1": 1, "2 a 10": 5, "mas de 10": 50, "desconocido": None}


def test_no_hay_leads_repetidos():
    webs = [e["lead"].split()[1] for e in EJEMPLOS]
    assert len(webs) == len(set(webs))


@pytest.mark.parametrize("ejemplo", EJEMPLOS, ids=lambda e: e["lead"].split()[1])
def test_respuesta_correcta_bien_formada(ejemplo):
    esperado = ejemplo["esperado"]
    assert set(esperado) == {"sector", "en_madrid", "tramo_sedes", "intencion", "accion"}
    assert esperado["tramo_sedes"] in SEDES_POR_TRAMO
    assert ejemplo["caso"], "Cada lead tiene que decir qué caso cubre"


@pytest.mark.parametrize("ejemplo", EJEMPLOS, ids=lambda e: e["lead"].split()[1])
def test_accion_coincide_con_las_reglas(ejemplo):
    esperado = ejemplo["esperado"]
    datos = DatosLead(
        sector=esperado["sector"],
        numero_sedes=SEDES_POR_TRAMO[esperado["tramo_sedes"]],
        en_madrid=esperado["en_madrid"],
        intencion=esperado["intencion"],
    )  # Pydantic también valida que sector e intención sean valores permitidos
    assert decidir(puntuar(datos)) == esperado["accion"]
