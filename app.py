from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Ruta para que Render verifique que el bot está vivo
@app.get("/")
def home():
    return {"status": "Bot encendido y operando"}

# Ruta para el Webhook de WhatsApp (donde llegarán los mensajes)
@app.get("/webhook")
async def verify_webhook(request: Request):
    # Aquí va la lógica de verificación de Meta
    params = request.query_params
    verify_token = os.getenv("VERIFY_TOKEN")
    
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == verify_token:
        return int(params.get("hub.challenge"))
    return "Error de verificación"

@app.post("/webhook")
async def handle_whatsapp_message(request: Request):
    data = await request.json()
    # Aquí es donde pondremos la lógica de Gemini más adelante
    print(f"Mensaje recibido: {data}")
    return {"status": "recibido"}
