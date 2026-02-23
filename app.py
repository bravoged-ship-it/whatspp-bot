import google.generativeai as genai
import requests

# Configurar Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/webhook")
async def handle_whatsapp_message(request: Request):
    data = await request.json()
    
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            # 1. Extraer el mensaje y el número del usuario
            message_obj = data["entry"][0]["changes"][0]["value"]["messages"][0]
            user_number = message_obj["from"]
            user_text = message_obj["text"]["body"]

            # 2. Pedirle respuesta a Gemini
            response = model.generate_content(user_text)
            bot_answer = response.text

            # 3. Enviar la respuesta a WhatsApp
            url = f"https://graph.facebook.com/v21.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
            headers = {"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"}
            json_data = {
                "messaging_product": "whatsapp",
                "to": user_number,
                "text": {"body": bot_answer}
            }
            requests.post(url, json=headers, json=json_data)
            
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        
    return {"status": "ok"}
