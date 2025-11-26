import json
import re

def cargar_productos(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "productos" in data:
                return data["productos"]
            return data
    except:
        return []

def buscar_producto(nombre, productos_db):
    nombre = nombre.lower().strip()
    for prod in productos_db:
        if nombre in prod["producto"].lower():
            return prod
    return None

def extraer_productos(texto):
    texto = texto.lower()
    patron = r"(.+?)\s+(vs|vs\.|o|ó|contra|-|vs\s+)\s+(.+)"
    m = re.search(patron, texto)
    if not m:
        return {"p1": None, "p2": None}
    return {"p1": m.group(1).strip(), "p2": m.group(3).strip()}

def pidio_relacion_calidad_precio(texto):
    texto = texto.lower()
    claves = [
        "relación calidad precio", "relacion calidad precio", "calidad precio",
        "calidad/precio", "cuál conviene", "cual conviene",
        "que conviene mas", "qué conviene mas",
        "más conviene", "mas conviene",
        "rinde más por lo que sale", "rinde mas por lo que sale"
    ]
    return any(c in texto for c in claves)

def decidir_modo(prod1, prod2):
    return 2 if (prod1 and prod2) else 1
