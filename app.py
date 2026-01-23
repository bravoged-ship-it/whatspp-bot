import os
import re
import requests
import psycopg2
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURACIÓN ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = "916360421552548"
DATABASE_URL = os.getenv("DATABASE_URL")

def guardar_mensaje(telefono, mensaje):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id SERIAL PRIMARY KEY,
                telefono VARCHAR(20),
                mensaje TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
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

                # --- LÓGICA DE LIMPIEZA PARA MÉXICO (521 -> 52) ---
                if from_number.startswith("521") and len(from_number) == 13:
                    from_number = "52" + from_number[3:]
                
                # --- GUARDAR EN BASE DE DATOS ---
                guardar_mensaje(from_number, text)

                # --- LÓGICA DE RESPUESTAS (MENÚ ULMA) ---
                respuesta_bot = ""
                tiene_correo = "@" in text and "." in text
                tiene_telefono = bool(re.search(r'\d{8,}', text))
                saludos = ["hola", "buen", "dia", "tarde", "noche", "menu", "inicio", "empezar"]
                es_saludo = any(s in text for s in saludos)

                if es_saludo:
                    respuesta_bot = "🙌 ¡Hola! Gracias por comunicarte a *ULMA Packaging México*.\n\n¿Cómo te podemos ayudar? Elige una opción indicando el número:\n\n1️⃣ Venta de maquinaria \n2️⃣ Servicio técnico y repuestos\n3️⃣ Administración y Finanzas \n4️⃣ Atención personalizada"
                elif text == "1":
                    respuesta_bot = "🏭 *Ayúdenos a ofrecerle la mejor solución, por favor indíque los datos necesarios:* \n\n¿De qué parte de la república se comunica? \n¿Qué tecnología de envasado es de su interés? \n¿Qué productos desea empacar?"
                elif text == "2":
                    respuesta_bot = "🔩 *Que podemos hacer por usted en Servicio técnico?:* \n\nVenta de repuestos. \nVenta de servicios de mantenimiento. \n\nPara ofrecerle la mejor atención indíque el modelo de su equipo, no. de serie y/o código de repuesto."
                elif text == "3":
                    respuesta_bot = "🏢 *¿A qué área te gustaría contactar?:* \n\n• Facturación de equipos \n• Facturación de servicios/refacciones \n• Cuentas por cobrar/pagar \n• Recursos Humanos"
                elif text == "4":
                    respuesta_bot = "👤 *Agente Humano:*\nEn un momento un asesor se pondrá en contacto con usted."
                elif tiene_correo or tiene_telefono:
                    respuesta_bot = "✅ *Datos registrados con éxito.* Hemos recibido su contacto. Un asesor de ULMA Packaging se comunicará con usted a la brevedad. ¡Que tenga un excelente día! 👋"
                elif len(text) > 5:
                    respuesta_bot = "✅ *Información recibida.* Por favor comparta un **correo electrónico** y **número telefónico** para que un asesor pueda contactarlo formalmente. ¡Gracias!"
                else:
                    respuesta_bot = "🙌 ¡Hola! Gracias por comunicarte a *ULMA Packaging México*. Por favor elige una opción del 1 al 4."

                # --- ENVÍO DEL MENSAJE ---
                enviar_whatsapp(from_number, respuesta_bot)

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
    response = requests.post(url, json=payload, headers=headers)
    print(f"Respuesta de Meta: {response.status_code} - {response.text}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
