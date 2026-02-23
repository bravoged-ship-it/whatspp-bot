import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Cargamos el archivo .env
load_dotenv()

def inicializar_bot():
    # Obtenemos la llave dentro de la función para que no haya errores de definición
    llave = os.getenv("GOOGLE_API_KEY")
    
    if not llave:
        print("❌ ERROR: No se encontró la GOOGLE_API_KEY en el archivo .env")
        return None

    try:
        # 2. Configuración con Gemini 2.5 Flash
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=llave,
            temperature=0.7
        )

        # 3. Lógica del asistente
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en Mac M1 y despliegues en Render.com."),
            ("user", "{input}")
        ])

        # 4. Cadena de ejecución
        chain = prompt | llm | StrOutputParser()
        return chain

    except Exception as e:
        print(f"❌ Error al configurar el modelo: {e}")
        return None

if __name__ == "__main__":
    bot = inicializar_bot()
    
    if bot:
        print("\n✅ --- Bot de Gemini 2.5 Listo en tu Mac M1 ---")
        try:
            # Prueba de fuego
            pregunta = "Confirma que estás funcionando con Gemini 2.5"
            respuesta = bot.invoke({"input": pregunta})
            print(f"\nRespuesta de Gemini:\n{respuesta}\n")
        except Exception as e:
            print(f"❌ Error al ejecutar la consulta: {e}")
