const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

// --- CONFIGURACIÓN (Usa tus datos que ya funcionan) ---
const VERIFY_TOKEN = "47d2812e-a3ae-4697-871a-10a5fa363347"; 
const ACCESS_TOKEN = "EAAKwmTV97XABQohfBxyY5Kbr6OHmJOU9iglZCCwPh28m4Xq6cZCft2CeyRWKDgyYLPilOaFZAPsmLYTyPUd9vcMK6IrazqnCjmXyApClvcFv3XbATxwjSksrKrrZCP6ZBC6ZCx2gXPUEsEGxzRT26T3ldQ0GxA7d5Va1VxqNquCDPqnYJI0IOwe69vmpN1U9epUNrMyvsxDKXMfuqZCKhD3C7FbyJJhVudNOUO1yd2tSAFhzonVL5xldf3r2IzGLEHIkeNyKnvZCpNKHdqy53VoaKZBviUKsu4jFhvg04"; 
const PHONE_NUMBER_ID = "916360421552548"; 

app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];
    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
        res.status(200).send(challenge);
    } else {
        res.sendStatus(403);
    }
});

app.post('/webhook', async (req, res) => {
    const body = req.body;
    if (body.object === 'whatsapp_business_account') {
        if (body.entry && body.entry[0].changes[0].value.messages) {
            const msg = body.entry[0].changes[0].value.messages[0];
            const from = msg.from; 
            const text = msg.text ? msg.text.body.trim().toLowerCase() : "";

            // Lógica para limpiar el número de México
            let numeroDestino = from;
            if (from.startsWith("521")) {
                numeroDestino = "52" + from.substring(3);
            }

            // --- LÓGICA DEL MENÚ ---
            let respuestaBot = "";

            if (text === "1") {
                respuestaBot = "🛍️ *Nuestros Productos:*\nContamos con calzado deportivo y casual. ¿Deseas ver el catálogo digital?";
            } else if (text === "2") {
                respuestaBot = "📍 *Ubicación:*\nEstamos en Av. Juárez #123, CDMX. Abrimos de 9:00 AM a 6:00 PM.";
            } else if (text === "3") {
                respuestaBot = "👤 *Agente Humano:*\nEn un momento un asesor se pondrá en contacto contigo.";
            } else {
                respuestaBot = "🙌 ¡Hola! Bienvenido a nuestra tienda.\n\nPor favor, elige una opción enviando el número:\n1️⃣ Ver Productos\n2️⃣ Horarios y Ubicación\n3️⃣ Hablar con un asesor";
            }

            try {
                await axios({
                    method: "POST",
                    url: `https://graph.facebook.com/v21.0/${PHONE_NUMBER_ID}/messages`,
                    data: {
                        messaging_product: "whatsapp",
                        to: numeroDestino,
                        type: "text",
                        text: { body: respuestaBot },
                    },
                    headers: { "Authorization": `Bearer ${ACCESS_TOKEN}` },
                });
            } catch (error) {
                console.error("Error al enviar:", error.response ? error.response.data : error.message);
            }
        }
        res.status(200).send("EVENT_RECEIVED");
    } else {
        res.sendStatus(404);
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor activo en puerto ${PORT}`));
