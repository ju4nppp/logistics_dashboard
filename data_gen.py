import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

ZONAS = {
    "Noroeste": ["Sinaloa", "Sonora", "Baja California"],
    "Noreste":  ["Nuevo León", "Tamaulipas", "Chihuahua"],
    "Centro":   ["CDMX", "Estado de México", "Jalisco"],
    "Sur":      ["Oaxaca", "Chiapas", "Veracruz"],
    "Bajío":    ["Guanajuato", "Querétaro", "Aguascalientes"],
}

SERVICIOS = {
    "Express":   {"precio_base": 180, "dias_entrega": 1, "puntualidad": 0.93},
    "Estándar":  {"precio_base": 110, "dias_entrega": 3, "puntualidad": 0.85},
    "Económico": {"precio_base": 70,  "dias_entrega": 6, "puntualidad": 0.74},
}

ESTADOS_ENVIO = ["Entregado", "En tránsito", "Retrasado", "Devuelto", "Extraviado"]
PESOS_ESTADO  = [0.78, 0.10, 0.07, 0.04, 0.01]

VOLUMEN_ZONA = {
    "Centro": 3.0, "Noreste": 1.6, "Bajío": 1.3,
    "Noroeste": 1.0, "Sur": 0.7,
}


def generar_envios(n: int = 5000, meses: int = 12) -> pd.DataFrame:
    fecha_inicio = datetime(2024, 1, 1)
    registros = []

    for _ in range(n):
        zona   = random.choices(list(ZONAS), weights=[VOLUMEN_ZONA[z] for z in ZONAS])[0]
        estado = random.choice(ZONAS[zona])
        svc    = random.choices(list(SERVICIOS), weights=[2, 4, 3])[0]
        cfg    = SERVICIOS[svc]

        dias_offset = random.randint(0, meses * 30)
        fecha_envio = fecha_inicio + timedelta(days=dias_offset)

        es_puntual  = random.random() < cfg["puntualidad"]
        dias_real   = cfg["dias_entrega"] + (0 if es_puntual else random.randint(1, 5))
        fecha_entrega = fecha_envio + timedelta(days=dias_real)

        estado_envio = random.choices(ESTADOS_ENVIO, weights=PESOS_ESTADO)[0]
        peso_kg = round(random.uniform(0.5, 30), 2)
        precio  = round(cfg["precio_base"] + peso_kg * random.uniform(3, 8), 2)

        registros.append({
            "id_envio":      f"PKT{random.randint(100000, 999999)}",
            "fecha_envio":   fecha_envio,
            "fecha_entrega": fecha_entrega,
            "zona":          zona,
            "estado":        estado,
            "servicio":      svc,
            "estado_envio":  estado_envio,
            "peso_kg":       peso_kg,
            "precio":        precio,
            "dias_entrega":  dias_real,
            "a_tiempo":      es_puntual,
        })

    return pd.DataFrame(registros)


if __name__ == "__main__":
    df = generar_envios()
    print(df.head())
    print(df.shape)