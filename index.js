const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

// --- CONFIGURACIÓN (Asegúrate de que estos datos sean los correctos) ---
const VERIFY_TOKEN = "TU_TOKEN_SECRETO_123"; 
const ACCESS_TOKEN = "PEGA_AQUI_TU_TOKEN_DE_ACCESO_TEMPORAL"; 
const PHONE_NUMBER_ID = "916360421552548"; // Ya lo tomé de tu imagen anterior

// Verificación del Webhook para Meta
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
            const from = msg.from; // Viene como 5215550679358
            const text = msg.text.body;

            console.log(`Mensaje recibido de ${from}: ${text}`);

            // --- LÓGICA DE CORRECCIÓN PARA MÉXICO ---
            // Si el número tiene el '1' después del '52', se lo quitamos para que coincida con Meta
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
                        to: numeroDestino, // Enviamos al número corregido
                        type: "text",
                        text: { body: "¡Logrado! El bot ya puede responderte. Recibí: " + text },
                    },
                    headers: {
