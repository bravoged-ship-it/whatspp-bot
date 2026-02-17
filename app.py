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
        
        # Usamos el modelo estable 2.5 como acordamos
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
                                    "1️⃣0️⃣ Com
