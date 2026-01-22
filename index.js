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
                respuestaBot = "🏭 *Ayúdenos a ofrecerle la mejor solución, por favor indíque los datos necesarios:* \n¿De qué parte de la república se comunica? \n¿Qué tecnología de envasado es de su interés? \n¿Qué productos desea empacar";
            } else if (text === "2") {
                respuestaBot = "🔩 *Que podemos hacer por usted en Servicio técnico?:* \nVenta de repuestos. \nVenta de servicios de mantenimiento. \nPara ofrecerle la mejor atención indíque el modelo de su equipo, no. de serie y/o código de repuesto";
            } else if (text === "3") {
                respuestaBot = "🏢 *¿A qué área te gustaría contactar?:* \nFacturación de equipos \nFacturación de servicios/ refacciones \nCuentas por cobrar, \nCuentas por pagar \nRecursos Humanos";
            } else if (text === "4") {
                respuestaBot = "👤 *Agente Humano:*\nEn un momento un asesor se pondrá en contacto con usted.";
            }
            else if (text.length > 5) {
                respuestaBot = "✅ *Información recibida.* Por favor comparta un correo electrónico y número telefónico y en breve un asesor se pondrá en contacto con usted. ¡Gracias!";
            }
            else {
                respuestaBot = "🙌 ¡Hola! Gracias por comunicarte a ULMA Packaging México, Soluciones en envasado. \n¿Cómo te podemos ayudar?, elige la opción que más se acomode a tus necesidades indicando el número:\n1️⃣ Venta de maquinaria \n2️⃣ Servicio técnico y repuestos\n3️⃣ Administración y Finanzas \n4️⃣ Atención personalizada";
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
