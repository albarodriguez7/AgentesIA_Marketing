# Comprobaciones del redactor: ¿cita solo los artículos que recibió?
import re

# Una cita del informe: "(LSSI, art. 10)"
PATRON_CITA = r"\(([A-Z]+), art\. (\d+)\)"


def citas_del_informe(informe: str) -> list[str]:
    # Devuelve las citas del informe en orden, como 'LSSI art. 10'
    citas = []
    for ley, articulo in re.findall(PATRON_CITA, informe):
        citas.append(f"{ley} art. {articulo}")
    return citas


def citas_inventadas(informe: str, fuentes: list) -> list[str]:
    # Citas del informe que NO están entre las fuentes que recibió el redactor
    permitidas = {f"{fuente['ley']} art. {fuente['articulo']}" for fuente in fuentes}
    inventadas = []
    for cita in citas_del_informe(informe):
        if cita not in permitidas:
            inventadas.append(cita)
    return inventadas