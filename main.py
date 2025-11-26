import os
import json
from dotenv import load_dotenv
from flask import Flask, request
import requests
from google import genai

from utils import (
    cargar_productos,
    buscar_producto,
    extraer_productos,
    decidir_modo,
    pidio_relacion_calidad_precio
)

# cargar variables del .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("OPENAI_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# cargar base de datos de productos
productos_db = cargar_productos("productos.json")

# flask server
app = Flask(__name__)

# memoria por usuario
contexto_usuarios = {}

# función para enviar mensaje a telegram
def enviar_mensaje(chat_id, texto):
    data = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    }
    requests.post(TELEGRAM_URL, json=data)

# función para llamar a gemini
def llamar_gemini(prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)

    try:
        respuesta = client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=prompt
        )
        return respuesta.text

    except Exception as e:
        print("ERROR GEMINI:", e)
        return "Hubo un problema al generar la respuesta, intentá de nuevo."


# endpoint del webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    texto_usuario = data["message"].get("text", "").lower().strip()

    if not texto_usuario:
        enviar_mensaje(chat_id, "No entendí tu mensaje.")
        return {"ok": True}

    # bienvenida
    if texto_usuario in ["/start", "hola", "buenas", "hey"]:
        contexto_usuarios.pop(chat_id, None)
        bienvenida = (
            "¡Hola! Soy *Mercadín*, tu asistente para comparar productos.\n\n"
            "Podés escribir cosas como:\n"
            "• `Coca-Cola vs Pepsi`\n"
            "• `Shampoo Dove contra Pantene`\n\n"
            "También podés preguntar *calidad/precio* después de comparar.\n\n¿En qué te ayudo?"
        )
        enviar_mensaje(chat_id, bienvenida)
        return {"ok": True}

    # detectar productos en el mensaje
    nombres = extraer_productos(texto_usuario)
    p1, p2 = nombres["p1"], nombres["p2"]

    # 📌 Caso: el usuario envió productos nuevos → guardar en memoria
    if p1 and p2:
        contexto_usuarios[chat_id] = {"p1": p1, "p2": p2}

    # 📌 Caso: NO envió productos, pero pidió calidad/precio → usar últimos productos
    elif pidio_relacion_calidad_precio(texto_usuario):
        if chat_id not in contexto_usuarios:
            enviar_mensaje(chat_id, "Primero decime qué dos productos querés comparar 😊")
            return {"ok": True}
        else:
            p1 = contexto_usuarios[chat_id]["p1"]
            p2 = contexto_usuarios[chat_id]["p2"]

    # 📌 Caso: no envió productos y no pidió calidad/precio
    else:
        enviar_mensaje(
            chat_id,
            "Necesito *dos productos* para comparar.\nEjemplos:\n• Coca-Cola vs Sprite\n• Dove vs Pantene"
        )
        return {"ok": True}

    # buscar productos en JSON
    prod1 = buscar_producto(p1, productos_db)
    prod2 = buscar_producto(p2, productos_db)

    # si no están en base → modo general
    if not prod1 or not prod2:
        if pidio_relacion_calidad_precio(texto_usuario):
            # respuesta especial solo calidad/precio sin repetir comparación entera
            with open("prompts/calidad_precio.txt", "r", encoding="utf-8") as f:
                base_prompt = f.read()

            prompt = f"""{base_prompt}

productos:
- {p1}
- {p2}

hacer SOLO una conclusión de calidad/precio.
"""
            respuesta = llamar_gemini(prompt)
            enviar_mensaje(chat_id, respuesta)
            return {"ok": True}

        enviar_mensaje(chat_id, "Estos productos no están en mi base, pero te doy una comparación general:")

        with open("prompts/modo1.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()

        prompt = f"""{base_prompt}

comparar:
- {p1}
- {p2}
"""
        respuesta = llamar_gemini(prompt)
        enviar_mensaje(chat_id, respuesta)
        return {"ok": True}

    # modo 2: ambos están en la base
    if pidio_relacion_calidad_precio(texto_usuario):
        with open("prompts/calidad_precio.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()

        productos_json = json.dumps([prod1, prod2], ensure_ascii=False, indent=2)

        prompt = f"""{base_prompt}

productos reales JSON:
{productos_json}

comparar SOLO relación calidad/precio entre:
- {prod1['producto']}
- {prod2['producto']}
"""
        respuesta = llamar_gemini(prompt)
        enviar_mensaje(chat_id, respuesta)
        return {"ok": True}

    # comparación normal (modo 2)
    with open("prompts/modo2.txt", "r", encoding="utf-8") as f:
        base_prompt = f.read()

    productos_json = json.dumps([prod1, prod2], ensure_ascii=False, indent=2)

    prompt = f"""{base_prompt}

productos disponibles:
{productos_json}

comparar:
- {prod1['producto']}
- {prod2['producto']}
"""

    respuesta = llamar_gemini(prompt)
    enviar_mensaje(chat_id, respuesta)

    return {"ok": True}


# iniciar servidor
if __name__ == "__main__":
    print("Mercadín corriendo en http://localhost:5000/webhook")
    app.run(debug=True, port=5000)
