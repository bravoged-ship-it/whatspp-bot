from fastapi import FastAPI, Request
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configurar Gemini (Usamos el nombre que pusiste en Render)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/")
def home():
    return {"status": "Bot encendido y operando"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    verify_token = os.getenv("VERIFY_TOKEN")
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == verify_token:
        return int(params.get("hub.challenge"))
    return "Error de verificación"

@app.post("/webhook")
async def handle_whatsapp_message(request: Request):
    data = await request.json()
    
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message_obj = data["entry"][0]["changes"][0]["value"]["messages"][0]
            user_number = message_obj["from"]
            user_text = message_obj["text"]["body"]
            
            print(f"Pregunta del usuario: {user_text}")

            # 1. Gemini genera la respuesta
            response = model.generate_content(user_text)
            bot_answer = response.text
            print(f"Respuesta de Gemini: {bot_answer}")

            # 2. Enviar a WhatsApp (Corregido: headers=headers)
            url = f"https://graph.facebook.com/v21.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
            headers = {"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"}
            json_data = {
                "messaging_product": "whatsapp",
                "to": user_number,
                "text": {"body": bot_answer}
            }
            
            r = requests.post(url, headers=headers, json=json_data)
            print(f"Estado de envío a WhatsApp: {r.status_code}")
            
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        
    return {"status": "ok"}
