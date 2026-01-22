import os
import re
import requests
import psycopg2 # Librería para la base de datos
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURACIÓN ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "47d2812e-a3ae-4697-871a-10a5fa363347")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAKwmTV97XABQiXxsD2o9Q9nF2jvRkqUxxyxMXeZBEN4p3ugK9SNcWZC2iFwp5G2BZCON1MjGKrNJDxfkO7rKeK5LHYB6dEX3yvaOsQzrodwvAZCMLySsdDyXjpsKAOXY8Ba1tQBRTru8DZAYnW6DBQZApdZBIRPaREfpPpPbRkdoc6rBZAe1NYZAwfrTHHp7XcWFnCqncWw9In6Bgy0k5iiSVCAn6ZAIvBA1K8HOS1Y3M8zn7c3XjQtUhVMVFJDPqM6UhnFRn78pAjv520jJoI6HVzx0qSRB1KrDoZBdPz")
PHONE_NUMBER_ID = "916360421552548"
DATABASE_URL = os.getenv("dpg-d5panb3vbchc7391rs9g-a") # URL de la base de datos en Render

# Función para guardar en la base de datos
def guardar_mensaje(telefono, mensaje):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # Creamos la tabla si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id SERIAL PRIMARY KEY,
                telefono VARCHAR(20),
                mensaje TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Insertamos los datos
        cur.execute("INSERT INTO mensajes (telefono, mensaje) VALUES (%s, %s)", (telefono, mensaje))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error en BD: {e}")

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def handle_messages():
    body = request.get_json()
    if body.get('object') == 'whatsapp_business_account':
        try:
            entry = body.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            if 'messages' in value:
                msg = value['messages'][0]
                from_number = msg['from']
                text = msg.get('text', {}).get('body', "").strip().lower()

                # --- GUARDAR EN BASE DE DATOS ---
                guardar_mensaje(from_number, text)

                # (Aquí sigue el resto de tu lógica de respuestas igual que antes...)
                # [Lógica de respuesta_bot ...]
                
                # Ejemplo simplificado de envío
                enviar_whatsapp(from_number, "Mensaje recibido y guardado")

        except Exception as e:
            print(f"Error: {e}")
        return "EVENT_RECEIVED", 200
    return "Not Found", 404

def enviar_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
