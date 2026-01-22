import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Se recomienda usar variables de entorno por seguridad
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "47d2812e-a3ae-4697-871a-10a5fa363347")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAKwmTV97XABQrvzfgKSBA5HUUfEvEyy1d6imFdLaGJEVPIpGIU0RSDGtqyVZBXA4g9nf7gTL80c4O5COvwFQE4A9hVanvIRVj0Cdfv0bjRy4hvu64GebT1FKxVH5nHFmZCvHjO0ei6y33DlcolSic7q7gYMm7WSs1Nk2cwvymAQSPF2MxPgrZAw5O6c2xq1m5gu7AlZAv9DsuQZAErO4WROt0oxmkSaQHiiNaWNpyIYx2aiEv21wGKrIrm1aaHYyhMmIDw8cxeZBAJf2J3INgRRhsUNiFuLHFSwZDZD")
PHONE_NUMBER_ID = "916360421552548"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Verificación del Webhook de Facebook
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def handle_messages():
    body = request.get_json()

    if body.get('object') == 'whatsapp_business_account':
        try:
            # Navegamos por el JSON de WhatsApp
            entry = body.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            if 'messages' in value:
                msg = value['messages'][0]
                from_number = msg['from']
                
                # Extraer texto del mensaje
                text = ""
                if 'text' in msg:
                    text = msg['text']['body'].strip().lower()

                # Lógica para limpiar el número de México (521 -> 52)
                numero_destino = from_number
                if from_number.startswith("521"):
                    numero_destino = "52" + from_number[3:]

                respuesta_bot = ""

                # --- LÓGICA DE VALIDACIÓN ---
                tiene_correo = "@" in text and "." in text
                tiene_telefono = bool(re.search(r'\d{8,}', text))
                
                saludos = ["hola", "buen", "dia", "tarde", "noche", "menu", "inicio", "empezar"]
                es_saludo = any(s in text for s in saludos)

                # --- FLUJO DE DECISIÓN ---
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
                url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                payload = {
                    "messaging_product": "whatsapp",
                    "to": numero_destino,
                    "type": "text",
                    "text": {"body": respuesta_bot}
                }

                response = requests.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(f"Error al enviar: {response.text}")

        except Exception as e:
            print(f"Error procesando el mensaje: {e}")

        return "EVENT_RECEIVED", 200
    else:
        return "Not Found", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
