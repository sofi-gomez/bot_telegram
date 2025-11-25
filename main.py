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
    decidir_modo
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


# función para enviar mensaje a telegram
def enviar_mensaje(chat_id, texto):
    data = {"chat_id": chat_id, "text": texto}
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
        print("🔍 ERROR GEMINI:", e)
        return "⚠️ Hubo un error al generar la respuesta. Revisá tu API key o intentá más tarde."

# endpoint del webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    texto_usuario = data["message"].get("text", "")

    if not texto_usuario:
        enviar_mensaje(chat_id, "no entendí el mensaje")
        return {"ok": True}

    # 1) extraer posibles productos
    prod_names = extraer_productos(texto_usuario)

    p1 = prod_names.get("p1")
    p2 = prod_names.get("p2")

    if not p1 or not p2:
        enviar_mensaje(chat_id, "necesito dos productos para comparar")
        return {"ok": True}

    # 2) buscar en la base de datos
    prod1 = buscar_producto(p1, productos_db)
    prod2 = buscar_producto(p2, productos_db)

    # 3) decidir modo
    modo = decidir_modo(prod1, prod2)

    # 4) armar prompt
    if modo == 2:
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

    else:
        with open("prompts/modo1.txt", "r", encoding="utf-8") as f:
            base_prompt = f.read()

        prompt = f"""{base_prompt}

comparar:
- {p1}
- {p2}
"""

    # 5) llamar a gemini
    respuesta = llamar_gemini(prompt)


    # 6) enviar respuesta a telegram
    enviar_mensaje(chat_id, respuesta)

    return {"ok": True}


# iniciar servidor
if __name__ == "__main__":
    print("mercadín corriendo en http://localhost:5000/webhook")
    app.run(debug=True, port=5000)