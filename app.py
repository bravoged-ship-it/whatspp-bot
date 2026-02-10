import os
import re
import requests
import psycopg2
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURACIÓN ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = "975359055662384"
DATABASE_URL = os.getenv("DATABASE_URL")

# --- CONFIGURACIÓN GEMINI IA ---
# IMPORTANTE: Con la versión 0.8.3, esto funcionará directo
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def obtener_respuesta_gemini(mensaje_usuario):
    try:
        prompt = (
            "Eres el asistente virtual de ULMA Packaging México. Responde de forma breve y amable. "
            f"Usuario: {mensaje_usuario}"
        )
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return "Por el momento no tengo esa información. ¿Deseas hablar con un asesor? Marca '4'."
    except Exception as e:
        print(f"DEBUG ERROR GEMINI: {e}")
        return "Sigo ajustando mi sistema inteligente. ¿Puedo ayudarte con el menú escribiendo 'A'?"

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
                text = msg.get('text', {}).get('body', "").strip()
                text_lower = text.lower()

                if from_number.startswith("521") and len(from_number) == 13:
                    from_number = "52" + from_number[3:]
                
                guardar_mensaje(from_number, text)

                # --- VARIABLES DE CONTROL ---
                respuesta_bot = ""
                tiene_correo = "@" in text_lower and "." in text_lower
                tiene_telefono = bool(re.search(r'\d{8,}', text_lower))
                saludos = ["hola", "buen", "dia", "tarde", "noche", "menu", "inicio", "empezar"]
                es_saludo = any(s in text_lower for s in saludos)

                # --- LÓGICA DE MENÚS ---
                if es_saludo or text_lower == "a":
                    respuesta_bot = (
                        "🙌 ¡Hola! Gracias por comunicarte a *ULMA Packaging México*.\n\n"
                        "Elija una opción:\n\n"
                        "1️⃣ Venta de maquinaria\n"
                        "2️⃣ Servicio técnico y repuestos\n"
                        "3️⃣ Administración y Finanzas\n"
                        "4️⃣ Atención personalizada"
                    )

                elif text == "1":
                    respuesta_bot = ("🏭 *Venta de Maquinaria*\n"
                                    "Seleccione una solución de envasado:\n\n"
                                    "5️⃣ Cárnico 🥩\n6️⃣ Avícola 🍗\n7️⃣ Queso 🧀\n8️⃣ Hortofrutícola 🍎\n"
                                    "9️⃣ Panadería y Pastelería 🍪\n1️⃣0️⃣ Comida preparada 🍕\n"
                                    "1️⃣1️⃣ Pescado y Mariscos 🐟\n1️⃣2️⃣ Médical y Farmacéutica 💉\n\n"
                                    "🅰️ Indique la letra *A* para regresar.")

                elif text == "2":
                    respuesta_bot = ("🔩 *Servicio Técnico y Repuestos*\n"
                                    "¿En qué lo podemos ayudar?\n\n"
                                    "1️⃣3️⃣ Refacciones ⚙️\n1️⃣4️⃣ Agendar servicio 📅\n1️⃣5️⃣ Pólizas de mantenimiento 👷🏻‍♂️\n\n"
                                    "🅰️ Indique la letra *A* para regresar.")

                elif text == "3":
                    respuesta_bot = ("🏢 *Administración y Finanzas*\n"
                                    "Seleccione el área:\n\n"
                                    "1️⃣6️⃣ Tesorería 📊\n1️⃣7️⃣ Recursos Humanos 🏢\n1️⃣8️⃣ Cuentas por cobrar repuestos 💵\n"
                                    "1️⃣9️⃣ Cuentas por cobrar máquinas 💵\n2️⃣0️⃣ Cuentas por pagar 🏦\n\n"
                                    "🅰️ Indique la letra *A* para regresar.")

                elif text == "4":
                    respuesta_bot = "👤 *Agente Humano:*\nPor favor comparta un **correo electrónico** y **número telefónico** y en un momento un asesor se pondrá en contacto con usted."

                # --- SUBMENÚS (Resumidos para no hacer el código gigante, funcionan igual) ---
                elif text == "5":
                    respuesta_bot = "🥩 *Cárnico*\nContacte a Edith Camacho: maria.edith@ulmapackaging.com.mx | Mob:5587602480\n🅰️ Regresar con *A*."
                elif text == "6":
                    respuesta_bot = "🍗 *Avícola*\nContacte a Andres Jacome: joseandres.jacome@ulmapackaging.com.mx | Mob:5587423015\n🅰️ Regresar con *A*."
                elif text == "7":
                    respuesta_bot = "🧀 *Queso*\nContacte a Edgar Martínez: edgar.martinez@ulmapackaging.com.mx | Mob:5574239851\n🅰️ Regresar con *A*."
                elif text == "8":
                    respuesta_bot = "🍎 *Hortofrutícola*\nContacte a Jorge Fernández: jorge.fernandez@ulmapackaging.com.mx | Mob:5524698043\n🅰️ Regresar con *A*."
                elif text == "9":
                    respuesta_bot = "🍪 *Panadería*\nContacte a Roberto Sánchez: jrsanchez@ulmapackaging.com.mx | Mob:5547804369\n🅰️ Regresar con *A*."
                elif text == "10":
                    respuesta_bot = "🍕 *Comida Prep.*\nContacte a Daniel Muñoz: daniel.muñoz@ulmapackaging.com.mx | Mob:5578946247\n🅰️ Regresar con *A*."
                elif text == "11":
                    respuesta_bot = "🐟 *Pescado*\nContacte a Jesus Delgado: jesus.emmanuel@ulmapackaging.com.mx | Mob:5571648907\n🅰️ Regresar con *A*."
                elif text == "12":
                    respuesta_bot = "💉 *Médical*\nContacte a Diego Beato: diego.beato@ulmapackaging.com.mx | Mob:5587602480\n🅰️ Regresar con *A*."
                
                elif text == "13":
                    respuesta_bot = "⚙️ *Refacciones*\n2️⃣1️⃣ Cotización\n2️⃣2️⃣ Estatus Cotización\n2️⃣3️⃣ Recepción OC\n2️⃣4️⃣ Estatus OC\n🅰️ Regresar con *A*."
                elif text == "14":
                    respuesta_bot = "👷🏻‍♂️ *Servicio*\n2️⃣5️⃣ Solicitar fecha\n2️⃣6️⃣ Reagendar\n2️⃣7️⃣ Asesoría telefónica\n2️⃣8️⃣ Capacitación\n🅰️ Regresar con *A*."
                elif text == "15":
                    respuesta_bot = "🛠️ *Pólizas*\n2️⃣9️⃣ Cotización\n3️⃣0️⃣ Renovación\n3️⃣1️⃣ Informes\n🅰️ Regresar con *A*."

                elif text in ["16", "17", "18", "19", "20"]:
                    respuesta_bot = "💼 *Área Administrativa*\nComparta su nombre y motivo de contacto.\n🅰️ Regresar con *A*."
                elif text in [str(i) for i in range(21, 32)]: # Del 21 al 31
                    respuesta_bot = "📋 *Servicio Técnico*\nIndique Modelo, Serie o Código de repuesto.\n🅰️ Regresar con *A*."

                # --- VALIDACIÓN DE DATOS ---
                elif tiene_correo or tiene_telefono:
                    respuesta_bot = "👍🏻 *Datos registrados.* Un asesor se comunicará pronto."

                # --- GEMINI IA ---
                elif len(text) > 2:
                    respuesta_bot = obtener_respuesta_gemini(text)

                else:
                    respuesta_bot = "⚠️ Opción no válida. Escribe *A* para volver al menú."

                enviar_whatsapp(from_number, respuesta_bot)

        except Exception as e:
            print(f"Error general: {e}")
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
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
