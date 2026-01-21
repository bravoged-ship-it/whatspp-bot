const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

// --- CONFIGURACIÓN ---
const VERIFY_TOKEN = "47d2812e-a3ae-4697-871a-10a5fa363347"; 
const ACCESS_TOKEN = "EAAKwmTV97XABQru3n3zyZABYSkEr2QSSNSmefMtoEdZCjbn3w3kVmM3QpMex2YS0T4hpriBRFyGrk2j6ekMZBbmnjlkSuVRFQ7xY3hZAjTXVM9Y3EggEhbng6I3B1ngzZB67plyecbep9atckqtdSyQCPeOXaJTgVBdDRMh2UZCwQkFrvw71FZCztwZCLS29RUpzWpnQXt47DQiWuyus6UC8PwVFrOfEQxtR7ICyk5dZCPJnUrGIQBDS42gdd7Bbquk0YcNU3plZBZBs0bZAAeidPZCWgOhXmlopZA1YsgcpQZD"; 
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

// Recepción y Respuesta
app.post('/webhook', async (req, res) => {
    const body = req.body;

    if (body.object === 'whatsapp_business_account') {
        if (body.entry && body.entry[0].changes[0].value.messages) {
            const msg = body.entry[0].changes[0].value.messages[0];
            const from = msg.from; 
            const text = msg.text ? msg.text.body : "Mensaje no es texto";

            console.log(`Mensaje recibido de ${from}: ${text}`);

            let numeroDestino = from;
            if (from.startsWith("521")) {
                numeroDestino = "52" + from.substring(3);
            }

            try {
                await axios({
                    method: "POST",
                    url: `https://graph.facebook.com/v21.0/${PHONE_NUMBER_ID}/messages`,
                    data: {
                        messaging_product: "whatsapp",
                        to: numeroDestino,
                        type: "text",
                        text: { body: "¡Bot activo! Recibí: " + text },
                    },
                    headers: { 
                        "Authorization": `Bearer ${ACCESS_TOKEN}`,
                        "Content-Type": "application/json" 
                    },
                });
                console.log(`Respuesta enviada a: ${numeroDestino}`);
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
