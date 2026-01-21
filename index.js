const express = require('express');
const app = express();
app.use(express.json());

// --- 1. CONFIGURACIÓN DE SEGURIDAD ---
// Este es el token que tú inventas. 
// Debes poner el MISMO en el panel de Meta cuando configures el Webhook.
const VERIFY_TOKEN = "47d2812e-a3ae-4697-871a-10a5fa363347"; 

// --- 2. VERIFICACIÓN DEL WEBHOOK (MÉTODO GET) ---
// Meta llama a esta ruta para asegurarse de que tu servidor existe y es seguro.
app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    if (mode && token) {
        if (mode === 'subscribe' && token === VERIFY_TOKEN) {
            console.log('WEBHOOK_VERIFIED');
            res.status(200).send(challenge);
        } else {
            res.sendStatus(403); // Token incorrecto
        }
    }
});

// --- 3. RECEPCIÓN DE MENSAJES (MÉTODO POST) ---
// Aquí es donde Meta te enviará los mensajes que tus clientes escriban.
app.post('/webhook', (req, res) => {
    const body = req.body;

    // Verificamos que sea un evento de WhatsApp
    if (body.object === 'whatsapp_business_account') {
        if (body.entry && body.entry[0].changes && body.entry[0].changes[0].value.messages) {
            
            const mensajeOriginal = body.entry[0].changes[0].value.messages[0];
            const textoUsuario = mensajeOriginal.text ? mensajeOriginal.text.body : "No es texto";
            const numeroUsuario = mensajeOriginal.from;

            console.log(`Mensaje de ${numeroUsuario}: ${textoUsuario}`);
            
            // Aquí podrías agregar la lógica para responder (usando un fetch/axios a la API de Meta)
        }
        res.sendStatus(200); // Siempre responder 200 a Meta para que no reintente
    } else {
        res.sendStatus(404);
    }
});

// --- 4. INICIO DEL SERVIDOR ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Servidor activo en puerto ${PORT}`);
});
