import os
import re
import requests
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURACIÓN ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = "975359055662384"

# Configuración de IA con la librería oficial
def obtener_respuesta_gemini(mensaje_usuario):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Usamos el modelo estable 2.5
        model = genai.GenerativeModel('gemini-2.5-flash')

        contexto_ulma = (
            "Eres el experto de ULMA Packaging México. Tu objetivo es asesorar sobre máquinas de empaque y servicios de mantenimiento a las máquinas ULMA. "
            "REGLAS CRÍTICAS: NO respondas con 'Hola' ni saludos iniciales, ve directo a la respuesta. "
            "CONOCIMIENTO DE NUESTRA WEB: Ofrecemos soluciones de Flow Pack (HFFS), Termoformado, Termosellado, "
            "Vertical (VFFS) y Stretch Film. Tenemos presencia local en México para soporte técnico. "
            "Si el cliente pregunta algo técnico, pídele el modelo de su máquina o número de serie. "
            "Nuestra web oficial es: https://www.ulmapackaging.mx"
        )
        
        prompt = f"{contexto_ulma}\n\nPregunta del cliente: {mensaje_usuario}"
        
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return "Lo siento, por ahora no puedo procesar esa duda. Escribe 'A' para ver el menú."
            
    except Exception as e:
        print(f"Error con Librería Gemini: {e}")
        return "Hubo un error al consultar a la IA. Intenta de nuevo o escribe 'A'."

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

                # Normalización de número para México
                if from_number.startswith("521") and len(from_number) == 13:
                    from_number = "52" + from_number[3:]
                
                respuesta_bot = ""
                saludos = ["hola", "buen", "dia", "tarde", "noche", "menu", "inicio", "empezar"]
                es_saludo = any(s in text_lower for s in saludos)
                
                # CORRECCIÓN: Definimos la validación de datos
                tiene_datos = ("@" in text_lower and "." in text_lower) or bool(re.search(r'\d{8,}', text_lower))

                # --- LÓGICA DE MENÚS (TEXTOS INTACTOS) ---
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
                                    "5️⃣ Cárnico 🥩\n"
                                    "6️⃣ Avícola 🍗\n"
                                    "7️⃣ Queso 🧀\n"
                                    "8️⃣ Hortofrutícola 🍎\n"
                                    "9️⃣ Panadería y Pastelería 🍪\n"
                                    "1️⃣0️⃣ Comida preparada 🍕\n"
                                    "1️⃣1️⃣ Pescado y Mariscos 🐟\n"
                                    "1️⃣2️⃣ Médical y Farmacéutica 💉\n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "2":
                    respuesta_bot = ("🔩 *Servicio Técnico y Repuestos*\n"
                                    "¿En qué lo podemos ayudar?\n\n"
                                    "1️⃣3️⃣ Refacciones ⚙️\n"
                                    "1️⃣4️⃣ Agendar servicio 📅\n"
                                    "1️⃣5️⃣ Pólizas de mantenimiento 👷🏻‍♂️\n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "3":
                    respuesta_bot = ("🏢 *Administración y Finanzas*\n"
                                    "Seleccione el área:\n\n"
                                    "1️⃣6️⃣ Tesorería 📊\n"
                                    "1️⃣7️⃣ Recursos Humanos 🏢\n"
                                    "1️⃣8️⃣ Cuentas por cobrar repuestos 💵\n"
                                    "1️⃣9️⃣ Cuentas por cobrar máquinas 💵\n"
                                    "2️⃣0️⃣ Cuentas por pagar 🏦\n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "4":
                    respuesta_bot = "👤 *Agente Humano:*\nPor favor comparta un **correo electrónico** y **número telefónico** y en un momento un asesor se pondrá en contacto con usted."

                elif text == "5":
                    respuesta_bot = ("🥩 *Cárnico*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestra asesora Edith Camacho *mail: maria.edith@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "6":
                    respuesta_bot = ("🍗 *Avícola*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestro asesor Andres Jacome *mail: joseandres.jacome@ulmapackaging.com.mx* *Mob:5587423015 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "7":
                    respuesta_bot = ("🧀 *Queso*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestro asesor Edgar Martínez *mail: edgar.martinez@ulmapackaging.com.mx* *Mob:5574239851 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "8":
                    respuesta_bot = ("🍎 *Hortofrutícola*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestro asesor Jorge Fernández *mail: jorge.fernandez@ulmapackaging.com.mx* *Mob:5524698043 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "9":
                    respuesta_bot = ("🍪 *Panadería y Pastelería*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestro asesor Roberto Sánchez *mail: jrsanchez@ulmapackaging.com.mx* *Mob:5547804369 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "10":
                    respuesta_bot = ("🍕 *Comida preparada*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestro asesor Daniel Muñoz *mail: daniel.muñoz@ulmapackaging.com.mx* *Mob:5578946247 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "11":
                    respuesta_bot = ("🐟 *Pescado y Mariscos*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestro asesor Jesus Delgado *mail: jesus.emmanuel@ulmapackaging.com.mx* *Mob:5571648907 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "12":
                    respuesta_bot = ("💉 *Médical y Farmacéutica*\n"
                                    "Ayúdenos con estos datos:\n"
                                    "• ¿De qué parte de la república se comunica?\n"
                                    "• ¿Qué productos desea empacar?\n\n"
                                    "• O bien, si lo desea, por favor póngase en contacto con nuestro asesor Diego Beato *mail: diego.beato@ulmapackaging.com.mx* *Mob:5587602480 \n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "13":
                    respuesta_bot = ("⚙️ *Refacciones*\n"
                                    "¿En qué le podemos servir?:\n"
                                    "2️⃣1️⃣ Cotización de refacciones\n"
                                    "2️⃣2️⃣ Estatus de cotizaciones\n"
                                    "2️⃣3️⃣ Recepción de ordenes de compra\n"
                                    "2️⃣4️⃣ Estatus de ordenes de compra\n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "14":
                    respuesta_bot = ("👷🏻‍♂️ *Agendar servicio*\n"
                                    "¿En qué le podemos servir?:\n"
                                    "2️⃣5️⃣ Solicitar fecha de servicio\n"
                                    "2️⃣6️⃣ Reagendar servicio\n"
                                    "2️⃣7️⃣ Asesoría telefónica\n"
                                    "2️⃣8️⃣ Capacitación programada\n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text == "15":
                    respuesta_bot = ("🛠️ *Pólizas de mantenimiento*\n"
                                    "¿En qué le podemos servir?:\n"
                                    "2️⃣9️⃣ Cotización póliza de mantenimiento\n"
                                    "3️⃣0️⃣ Renovación de póliza\n"
                                    "3️⃣1️⃣ Más informes de las pólizas\n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                elif text in ["16", "17", "18", "19", "20"]:
                    respuesta_bot = ("💼 *Área Administrativa*\n"
                                    "Por favor comparta su nombre y el motivo de su contacto para canalizarlo.\n\n"
                                    "🅰️ Indique la letra *A* para regresar.")

                elif text in ["21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]:
                    respuesta_bot = ("📋 *Información recibida por el Departamento de Servicio Técnico*\n"
                                    "Para agilizar su atención, por favor indique:\n"
                                    "• Modelo de su máquina a 6 dígitos\n"
                                    "• No. de serie a 5 dígitos y/o\n"
                                    "• Código de repuesto a 8 dígitos\n\n"
                                    "🅰️ Indique la letra *A* para regresar al menú principal.")

                # --- VALIDACIONES DE DATOS ---
                elif tiene_datos:
                    respuesta_bot = "👍🏻 *Datos registrados con éxito.* Un asesor de ULMA Packaging se comunicará con usted a la brevedad. ¡Que tenga un excelente día! 👋"

                # --- INTEGRACIÓN CON GEMINI IA ---
                elif len(text) > 2:
                    respuesta_bot = obtener_respuesta_gemini(text)

                else:
                    respuesta_bot = "⚠️ Opción no válida. Por favor elija un número de la lista o escriba *A* para volver al menú inicial."

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
