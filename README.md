🌟 Mercadín – Bot Inteligente de Comparación de Productos (Telegram)

Mercadín es un bot conversacional para Telegram que compara productos del supermercado usando IA (Google Gemini) y datos reales de una base JSON.
El bot permite al usuario tomar mejores decisiones de compra mediante comparaciones claras, breves y visuales.

🧠 Características principales

✔ Comparación entre dos productos

Si están en la base → usa datos reales (precio, rendimiento, características…).

Si no están → genera una comparación general usando IA.

✔ Dos modos de funcionamiento

Modo 1 – Comparación general
Cuando los productos no están en la base.

Modo 2 – Comparación con datos reales
Usa exclusivamente la información del archivo productos.json.

✔ Cálculo de relación calidad/precio (solo si el usuario lo pide)

Si la base contiene datos numéricos → se calcula de forma real.

Si no → responde sin inventar valores.

Usa memoria para recordar qué productos comparar.

📁 Estructura del Proyecto

bot_telegram/

│

├── main.py                  # Logica principal del bot y servidor Flask

├── utils.py                 # Funciones auxiliares: extraccion, busqueda, memoria

├── productos.json           # Base de datos de productos reales

├── requirements.txt         # Dependencias del proyecto

├── .env                     # Variables de entorno (NO subir a GitHub)

│
├── prompts/

│   ├── modo1.txt            # Comparacion general sin datos reales

│   ├── modo2.txt            # Comparacion con datos reales del JSON

│   └── calidad_precio.txt   # Prompt para la relacion calidad/precio

│
├── README.md                # Documentacion del proyecto

└── .gitignore               # Exclusiones para el repo




⚙️ Tecnologías utilizadas

Python 3

Flask

Regex

JSON

Telegram Bot API

Google Gemini API (modelo gratuito: gemini-2.0-flash)

Ngrok para exponer el webhook

Variables de entorno (.env) para:

TELEGRAM_TOKEN

OPENAI_API_KEY (Gemini)

🚀 Instalación y Ejecución
1. Clonar el repositorio
git clone https://github.com/tu-usuario/mercadin-bot.git
cd mercadin-bot

2. Crear entorno virtual (opcional)
python -m venv venv
venv\Scripts\activate   # Windows

3. Instalar dependencias
pip install -r requirements.txt

4. Crear archivo .env
TELEGRAM_TOKEN=tu_token
OPENAI_API_KEY=tu_api_key

5. Ejecutar el bot
python main.py

6. Exponer el webhook con Ngrok
ngrok http 5000


Copiar la URL generada y configurarla en BotFather:

https://xxxxxxx.ngrok-free.app/webhook

🛒 Cómo usar el bot
📌 Iniciar el bot

Escribir:

/start

📌 Comparar productos

Ejemplo:

Dove vs Pantene

📌 Preguntar cuál conviene más

Después de comparar:

cual conviene más?
calidad precio
rinde más por lo que sale?

El bot usa memoria y responde con información real si está disponible.

🏁 Conclusión

Mercadín es un bot funcional, robusto y extensible que integra múltiples conceptos de Inteligencia Artificial, APIs externas y programación backend.
Ofrece una excelente experiencia de usuario y cumple todos los requisitos del proyecto final.
