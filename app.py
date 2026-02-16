import os
import re
import requests
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURACIÓN ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = "975359055662384"

def obtener_respuesta_gemini(mensaje_usuario):
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Probamos con la ruta estable v1
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"Eres el asistente de ULMA Packaging México. Responde breve y amable en español: {mensaje_usuario}"}]
        }]
    }
    # ... resto del código igual ...

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_json = response.json()
        
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Error Gemini API: {res_json}")
            return "Lo siento, por ahora no puedo procesar esa duda. Escribe 'A' para ver el menú."
    except Exception as e:
        print(f"Error conexión Gemini: {e}")
        return "Hubo un error de conexión con la IA."

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
                text = msg.get('text', {}).get('body', "").strip()
                text_lower = text.lower()

                # Normalización de número México
                if from_number.startswith("521") and len(from_number) == 13:
                    from_number = "52" + from_number[3:]
                
                respuesta_bot = ""
                saludos = ["hola", "buen", "dia", "tarde", "noche", "menu", "inicio", "empezar"]
                es_saludo = any(s in text_lower for s in saludos)
                tiene_datos = ("@" in text_lower and "." in text_lower) or bool(re.search(r'\d{8,}', text_lower))

                # --- LÓGICA DE MENÚS ---
                if es_saludo or text_lower == "a":
                    respuesta_bot = "🙌 ¡Hola! Gracias por comunicarte a *ULMA Packaging México*.\n\nElija una opción:\n\n1️⃣ Venta de maquinaria\n2️⃣ Servicio técnico y repuestos\n3️⃣ Administración y Finanzas\n4️⃣ Atención personalizada"
                elif text == "1":
                    respuesta_bot = "🏭 *Venta de Maquinaria*\nSeleccione:\n\n5️⃣ Cárnico 🥩\n6️⃣ Avícola 🍗\n7️⃣ Queso 🧀\n8️⃣ Hortofrutícola 🍎\n9️⃣ Panadería 🍪\n1️⃣0️⃣ Comida prep. 🍕\n1️⃣1️⃣ Pescado 🐟\n1️⃣2️⃣ Médical 💉\n\n🅰️ Menú principal."
                elif text == "2":
                    respuesta_bot = "🔩 *Servicio Técnico*\n1️⃣3️⃣ Refacciones ⚙️\n1️⃣4️⃣ Agendar servicio 📅\n1️⃣5️⃣ Pólizas 👷🏻‍♂️\n\n🅰️ Menú principal."
                elif text == "3":
                    respuesta_bot = "🏢 *Administración*\n1️⃣6️⃣ Tesorería\n1️⃣7️⃣ RH\n1️⃣8️⃣ CxC Repuestos\n1️⃣9️⃣ CxC Máquinas\n2️⃣0️⃣ CxP\n\n🅰️ Menú principal."
                elif text == "4":
                    respuesta_bot = "👤 *Agente Humano:*\nPor favor comparta un correo y teléfono para contactarlo."
                elif text == "5":
                    respuesta_bot = "🥩 *Cárnico*\nEdith Camacho: maria.edith@ulmapackaging.com.mx | Mob:5587602480\n🅰️ Volver con *A*."
                elif text == "6":
                    respuesta_bot = "🍗 *Avícola*\nAndres Jacome: joseandres.jacome@ulmapackaging.com.mx | Mob:5587423015\n🅰️ Volver con *A*."
                elif text == "7":
                    respuesta_bot = "🧀 *Queso*\nEdgar Martínez: edgar.martinez@ulmapackaging.com.mx | Mob:5574239851\n🅰️ Volver con *A*."
                elif text == "8":
                    respuesta_bot = "🍎 *Hortofrutícola*\nJorge Fernández: jorge.fernandez@ulmapackaging.com.mx | Mob:5524698043\n🅰️ Volver con *A*."
                elif text == "9":
                    respuesta_bot = "🍪 *Panadería*\nRoberto Sánchez: jrsanchez@ulmapackaging.com.mx | Mob:5547804369\n🅰️ Volver con *A*."
                elif text == "10":
                    respuesta_bot = "🍕 *Comida Prep.*\nDaniel Muñoz: daniel.muñoz@ulmapackaging.com.mx | Mob:5578946247\n🅰️ Volver con *A*."
                elif text == "11":
                    respuesta_bot = "🐟 *Pescado*\nJesus Delgado: jesus.emmanuel@ulmapackaging.com.mx | Mob:5571648907\n🅰️ Volver con *A*."
                elif text == "12":
                    respuesta_bot = "💉 *Médical*\nDiego Beato: diego.beato@ulmapackaging.com.mx | Mob:5587602480\n🅰️ Volver con *A*."
                elif text == "13":
                    respuesta_bot = "⚙️ *Refacciones*\n2️⃣1️⃣ Cotización\n2️⃣2️⃣ Estatus Cotización\n2️⃣3️⃣ Recepción OC\n2️⃣4️⃣ Estatus OC\n🅰️ Volver con *A*."
                elif text == "14":
                    respuesta_bot = "👷🏻‍♂️ *Servicio*\n2️⃣5️⃣ Solicitar fecha\n2️⃣6️⃣ Reagendar\n2️⃣7️⃣ Asesoría telefónica\n2️⃣8️⃣ Capacitación\n🅰️ Volver con *A*."
                elif text == "15":
                    respuesta_bot = "🛠️ *Pólizas*\n2️⃣9️⃣ Cotización\n3️⃣0️⃣ Renovación\n3️⃣1️⃣ Informes\n🅰️ Volver con *A*."
                elif text in ["16", "17", "18", "19", "20"]:
                    respuesta_bot = "💼 *Administración*\nComparta su nombre y motivo. 🅰️ Volver con *A*."
                elif text in [str(i) for i in range(21, 32)]:
                    respuesta_bot = "📋 *Servicio Técnico*\nIndique Modelo y Serie de su máquina. 🅰️ Volver con *A*."
                elif tiene_datos:
                    respuesta_bot = "👍🏻 *Datos registrados.* Un asesor lo contactará pronto."
                elif len(text) > 2:
                    respuesta_bot = obtener_respuesta_gemini(text)
                else:
                    respuesta_bot = "⚠️ Escribe *A* para ver el menú."

                enviar_whatsapp(from_number, respuesta_bot)

        except Exception as e:
            print(f"Error general: {e}")
        return "EVENT_RECEIVED", 200
    return "Not Found", 404

def enviar_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": texto}}
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
