import pytest
from leads.evaluar_lead import DatosLead, puntuar, decidir

# Tienen que empezar siempre por test_ porque sino pytest los ignora

def test_lead_perfecto_saca_10():
    datos = DatosLead(sector="estetica", numero_sedes=4, en_madrid=True, intencion="alta")  # Nos inventamos los datos como si la IA los hubiera extraído y comprobamos solo las reglas
    assert puntuar(datos) == 10   # assert significa "compruebo que esto es verdad"


def test_lead_que_no_encaja_en_nada_saca_0():
    datos = DatosLead(sector="otro", numero_sedes=None, en_madrid=False, intencion="baja")  # Nos inventamos los datos como si la IA los hubiera extraído y comprobamos solo las reglas
    assert puntuar(datos) == 0



# Funcion nueva!!
@pytest.mark.parametrize("puntos, accion_esperada", [
    (10, "contactar"),
    (8, "contactar"),
    (7, "nutrir"),
    (5, "nutrir"),
    (4, "descartar"),
    (0, "descartar"),
])

# Es como un bucle for. Le doy una tabla de casos y por cada vuelta va eligiendo una fila. 
# Primero sustituye "puntos" por 10 y "accion_esperada" por "contactar". Y asi  todo el rato...


def test_decidir(puntos, accion_esperada):
    assert decidir(puntos) == accion_esperada


def test_sedes_desconocidas_no_suman_puntos():   # comprueba que None (sedes desconocidas) no suma puntos y que no da error
    datos = DatosLead(sector="salud", numero_sedes=None, en_madrid=True, intencion="media")
    assert puntuar(datos) == 7


def test_una_sede_no_suma_puntos():
    datos = DatosLead(sector="salud", numero_sedes=1, en_madrid=True, intencion="media")
    assert puntuar(datos) == 7


def test_dos_sedes_ya_suman_puntos():
    datos = DatosLead(sector="salud", numero_sedes=2, en_madrid=True, intencion="media")
    assert puntuar(datos) == 9



# Pruebo Test-Driven Development (TDD)

def test_diez_sedes_todavia_suman_puntos():
    datos = DatosLead(sector="salud", numero_sedes=10, en_madrid=True, intencion="media")
    assert puntuar(datos) == 9


def test_once_sedes_ya_no_suman_puntos():
    datos = DatosLead(sector="salud", numero_sedes=11, en_madrid=True, intencion="media")
    assert puntuar(datos) == 7


def test_cadena_muy_grande_no_suma_puntos():
    datos = DatosLead(sector="salud", numero_sedes=400, en_madrid=True, intencion="media")
    assert puntuar(datos) == 7


# Descartar negocios fuera de Madrid: 

def test_lead_fuera_de_madrid_no_suma_ningun_punto():
    datos = DatosLead(sector="educacion", numero_sedes=5, en_madrid=False, intencion="alta")
    assert puntuar(datos) == 0


def test_lead_fuera_de_madrid_se_descarta():
    datos = DatosLead(sector="educacion", numero_sedes=5, en_madrid=False, intencion="alta")
    assert decidir(puntuar(datos)) == "descartar"