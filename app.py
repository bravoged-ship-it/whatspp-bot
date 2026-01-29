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
                # Limpiamos el texto para procesarlo
                text = msg.get('text', {}).get('body', "").strip()
                text_lower = text.lower()

                # --- LÓGICA DE LIMPIEZA PARA MÉXICO (521 -> 52) ---
                if from_number.startswith("521") and len(from_number) == 13:
                    from_number = "52" + from_number[3:]
                
                # --- GUARDAR EN BASE DE DATOS ---
                guardar_mensaje(from_number, text)

                # --- LÓGICA DE RESPUESTAS (MENÚ ULMA) ---
                respuesta_bot = ""
                tiene_correo = "@" in text_lower and "." in text_lower
                tiene_telefono = bool(re.search(r'\d{8,}', text_lower))
                saludos = ["hola", "buen", "dia", "tarde", "noche", "menu", "inicio", "empezar"]
                es_saludo = any(s in text_lower for s in saludos)

                menu_principal = (
                    "🙌 ¡Hola! Gracias por comunicarte a *ULMA Packaging México*.\n\n"
                    "Elija una opción:\n\n"
                    "1️⃣ Venta de maquinaria\n"
                    "2️⃣ Servicio técnico y repuestos\n"
                    "3️⃣ Administración y Finanzas\n"
                    "4️⃣ Atención personalizada"
                )

                # Regresar al menú principal con Saludo o con la letra "A"
                if es_saludo or text_lower == "a":
                    respuesta_bot = menu_principal

                # --- SUBMENÚS ---
                elif text == "1":
                    respuesta_bot = ("🏭 *Venta de Maquinaria*\n"
                                    "Seleccione una solución de envasado:\n\n"
                                    "5 Cárnico\n"
                                    "6 Avícola\n"
                                    "7 Queso\n\n"
                                    "8 Hortofrutícola\n\n"
                                    "9 Panadería y Pastelería\n\n"
                                    "10 Comida preparada\n\n"
                                    "11 Pescado y Mariscos\n\n"
                                    "12 Médical y Farmacéutica\n\n"
                                    "Indique la letra *A* para regresar al menú principal.")

                elif text == "2":
                    respuesta_bot = ("🔩 *Servicio Técnico y Repuestos*\n"
                                    "¿En qué lo podemos ayudar?\n\n"
                                    "13 Refacciones\n"
                                    "14 Agendar servicio\n"
                                    "15 Pólizas de mantenimiento\n\n"
                                    "Indique la letra *A* para regresar al menú principal.")

                elif text == "3":
                    respuesta_bot = ("🏢 *Administración y Finanzas*\n"
                                    "Seleccione el área:\n\n"
                                    "16 Tesorería\n"
                                    "17 Recursos Humanos\n"
                                    "18 Cuentas por cobrar repuestos\n"
                                    "19 Cuentas por cobrar máquinas\n"
                                    "20 Cuentas por pagar\n\n"                        
                                    "Indique la letra *A* para regresar al menú principal.")

                elif text == "4":
                    respuesta_bot = "👤 *Agente Humano:*\nPor favor comparta un **correo electrónico** y **número telefónico** y en un momento un asesor se pondrá en contacto con usted."

                # --- LÓGICA DE RESPUESTAS PARA SUB-OPCIONES (4 al 12) ---
                elif text == "5":
                    respuesta_bot = ("🥩 *Cárnico*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")

                elif text == "6":
                    respuesta_bot = ("🍗 *Avícola*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")

                elif text == "7":
                    respuesta_bot = ("🧀 *Queso*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")

                elif text == "8":
                    respuesta_bot = ("🍎 *Hortofrutícola*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                    
                elif text == "9":
                    respuesta_bot = ("🍪 *Panadería y Pastelería*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                    
                elif text == "10":
                    respuesta_bot = ("🍕 *Comida preparada*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                
                elif text == "11":
                    respuesta_bot = ("🐟 *Pescado y Mariscos*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                
                elif text == "12":
                    respuesta_bot = ("💉 *Médical y Farmacéutica*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                    
                elif text == "13":
                    respuesta_bot = ("💉 *Refacciones*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                    
                elif text == "14":
                    respuesta_bot = ("💉 *Agendar servicio*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                    
                elif text == "15":
                    respuesta_bot = ("💉 *Pólizas de mantenimiento*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "Indique la letra *A* para regresar.")
                    #Si es 7; 13:Cotizaciones de repuestos, 14: Estatus de cotizaciones, 15: Recepción de ordenes de compra, 16: Estatus de ordenes de compra
                    

                elif text in ["16", "17", "18", "19", "20"]:
                    respuesta_bot = ("💼 *Área Administrativa*\n"
                                    "Por favor comparta su nombre y el motivo de su contacto para canalizarlo.\n\n"
                                    "Indique la letra *A* para regresar.")

                # --- VALIDACIONES FINALES ---
                elif tiene_correo or tiene_telefono:
                    respuesta_bot = "👍🏻 *Datos registrados con éxito.* Un asesor de ULMA Packaging se comunicará con usted a la brevedad. ¡Que tenga un excelente día! 👋"
                
                elif len(text) > 5:
                    respuesta_bot = "✅ *Información recibida.* Por favor comparta un **correo electrónico** y **número telefónico** para que podamos contactarlo formalmente."
                
                else:
                    respuesta_bot = "⚠️ Opción no válida. Por favor elija un número de la lista o escriba *A* para volver al menú inicial."

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
