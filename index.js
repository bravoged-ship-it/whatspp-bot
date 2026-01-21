const express = require('express');
const axios = require('axios'); // Necesitaremos esta librería para enviar datos a Meta
const app = express();
app.use(express.json());

// --- CONFIGURACIÓN ---
const VERIFY_TOKEN = "47d2812e-a3ae-4697-871a-10a5fa363347"; // El que ya usaste en el Webhook
const ACCESS_TOKEN = "EAAKwmTV97XABQnO9jK4IoTaSXDGWMBuzWia1rEcnRcQkZAzPZAAx2IW55IK1SIH1ZBvqccBnoMOj8jKvVTRgeLo5eqxupmL6eXdQAj0cVx9B4LbvlQRTZBCHjZCwwoGuajD4Vv1ZCgSJZC4tcuEt4szqw0JYB4id0czqzz0w3jQvM3TJco8vSH4i9Dg03FmWkbOvUPZC8HwNduqlmU7qbNtysM8axfbrX0SzWiLR1rJzLUlSev6DwF3mZCgZAmxm6UMZBGlZBWPKlHxroZCZAPiAV9eu0rv9adF4LMPuFZA5wZDZD"; 
const PHONE_NUMBER_ID = "916360421552548";

// Verificación del Webhook
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

// Recepción y Respuesta de mensajes
app.post('/webhook', async (req, res) => {
    const body = req.body;

    if (body.object === 'whatsapp_business_account') {
        if (body.entry && body.entry[0].changes[0].value.messages) {
            const msg = body.entry[0].changes[0].value.messages[0];
            const from = msg.from; // Número del usuario
            const text = msg.text.body; // Texto que envió

            console.log(`Mensaje recibido de ${from}: ${text}`);

            // LÓGICA DE RESPUESTA
            try {
                await axios({
                    method: "POST",
                    url: `https://graph.facebook.com/v21.0/${PHONE_NUMBER_ID}/messages`,
                    data: {
                        messaging_product: "whatsapp",
                        to: from,
                        text: { body: "¡Hola! Soy tu bot de ventas. Recibí tu mensaje: " + text },
                    },
                    headers: { "Authorization": `Bearer ${ACCESS_TOKEN}` },
                });
                console.log("Respuesta enviada con éxito");
            } catch (error) {
                console.error("Error al enviar:", error.response ? error.response.data : error.message);
            }
        }
        res.sendStatus(200);
    } else {
        res.sendStatus(404);
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor activo en puerto ${PORT}`));
