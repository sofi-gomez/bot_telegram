import json
import re

# --------------------
# Cargar archivo productos
# --------------------
def cargar_productos(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            if "productos" in data:
                return data["productos"]
            return data

    except Exception as e:
        print("Error al cargar productos.json:", e)
        return []


# --------------------
# Buscar producto
# --------------------
def buscar_producto(nombre, productos_db):
    nombre = nombre.lower().strip()

    for prod in productos_db:
        if nombre in prod["producto"].lower():
            return prod

    return None


# --------------------
# Extraer productos desde texto
# --------------------
def extraer_productos(texto):
    texto = texto.lower()

    patron = r"(.+?)\s+(vs|vs\.|o|ó|contra|-|vs\s+)\s+(.+)"
    match = re.search(patron, texto)

    if not match:
        return {"p1": None, "p2": None}

    return {
        "p1": match.group(1).strip(),
        "p2": match.group(3).strip()
    }

# --------------------
# Detectar si el usuario pidió relación calidad/precio
# --------------------
def pidio_relacion_calidad_precio(texto):
    texto = texto.lower()
    claves = [
        "relación calidad precio", "calidad precio","relacion calidad precio",
        "calidad/precio", "cual conviene", "cuál conviene",
        "que conviene mas", "qué conviene mas",
        "mas conviene", "más conviene",
        "rinde más por lo que sale", "rinde mas por lo que sale"
    ]
    return any(frase in texto for frase in claves)

# --------------------
# Decidir modo
# --------------------
def decidir_modo(prod1, prod2):
    if prod1 and prod2:
        return 2
    return 1