import json
import re

# carga el archivo json de productos
def cargar_productos(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Si el JSON tiene la forma {"productos": [...]}
            if "productos" in data:
                return data["productos"]
            
            # Si ya es una lista, devolverla como está
            return data

    except Exception as e:
        print("Error al cargar productos.json:", e)
        return []


# busca producto por nombre (búsqueda flexible)
def buscar_producto(nombre, productos_db):
    nombre = nombre.lower().strip()

    for prod in productos_db:
        if nombre in prod["producto"].lower():
            return prod

    return None


# extrae productos desde el mensaje usando regex simple
def extraer_productos(texto):
    texto = texto.lower()

    # extrae palabras separadas por "vs", "o", "contra", "-"
    patron = r"(.+?)\s+(vs|vs\.|o|ó|contra|-|vs\s+)\s+(.+)"
    match = re.search(patron, texto)

    if not match:
        return {"p1": None, "p2": None}

    p1 = match.group(1).strip()
    p2 = match.group(3).strip()

    return {"p1": p1, "p2": p2}


# decide el modo de comparación
def decidir_modo(prod1, prod2):
    if prod1 and prod2:
        return 2  # ambos existen: modo datos reales
    return 1       # modo general