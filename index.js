const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

// --- CONFIGURACIÓN ---
const VERIFY_TOKEN = process.env.VERIFY_TOKEN || "47d2812e-a3ae-4697-871a-10a5fa363347"; 
const ACCESS_TOKEN = process.env.ACCESS_TOKEN || "EAAKwmTV97XABQop3XPaybUZARzXjiyC01oZATwiy3ZA7ZABHpTR3I6GZA8pDi45t6Dfulqb8XHLpZCaUhCsETtB3YxqZC1XLQbSNhrBG0EgIZA3qKNZBB98fdyyemrvTKbPt3hTOWRPFECcrzb2HtnaQko5DroJXndTswh85T0fch8rQxowxPfra0lkpf1EV6KdZBjIu1dWpKCt0UgV8ctasM20VZAdMQymDxLMKR64S5N7HZBicABd1giKhfW8Ea7kUDZB1SPHIsROOOJhoPZBDjcnyVn2kA2WllpZCgtixwZDZD"; 
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
            
            // Si el mensaje no tiene texto (es una imagen o audio), evitamos que truene el código
            const text = msg.text ? msg.text.body.trim().toLowerCase() : "";

            // Lógica para limpiar el número de México (521 -> 52)
            let numeroDestino = from;
            if (from.startsWith("521")) {
                numeroDestino = "52" + from.substring(3);
            }

            let respuestaBot = "";

            // --- LÓGICA DE VALIDACIÓN ---
            const tieneCorreo = text.includes("@") && text.includes(".");
            const tieneTelefono = /\d{8,}/.test(text);
            
            // Definimos palabras que activan el saludo
            const saludos = ["hola", "buen", "dia", "tarde", "noche", "menu", "inicio", "empezar"];
            const esSaludo = saludos.some(s => text.includes(s));

            // --- FLUJO DE DECISIÓN CORREGIDO ---
            if (esSaludo) {
                // Si el usuario saluda o pide el menú, siempre mostramos el inicio
                respuestaBot = "🙌 ¡Hola! Gracias por comunicarte a *ULMA Packaging México*.\n\n¿Cómo te podemos ayudar? Elige una opción indicando el número:\n\n1️⃣ Venta de maquinaria \n2️⃣ Servicio técnico y repuestos\n3️⃣ Administración y Finanzas \n4️⃣ Atención personalizada";
            } 
            else if (text === "1") {
                respuestaBot = "🏭 *Ayúdenos a ofrecerle la mejor solución, por favor indíque los datos necesarios:* \n\n¿De qué parte de la república se comunica? \n¿Qué tecnología de envasado es de su interés? \n¿Qué productos desea empacar?"; // Tu texto completo aquí
            } 
            else if (text === "2") {
                respuestaBot = "🔩 *Que podemos hacer por usted en Servicio técnico?:* \n\nVenta de repuestos. \nVenta de servicios de mantenimiento. \n\nPara ofrecerle la mejor atención indíque el modelo de su equipo, no. de serie y/o código de repuesto."; // Tu texto completo aquí
            } 
            else if (text === "3") {
                respuestaBot = "🏢 *¿A qué área te gustaría contactar?:* \n\n• Facturación de equipos \n• Facturación de servicios/refacciones \n• Cuentas por cobrar/pagar \n• Recursos Humanos"; // Tu texto completo aquí
            } 
            else if (text === "4") {
                respuestaBot = "👤 *Agente Humano:*\nEn un momento un asesor se pondrá en contacto con usted.";
            } 
            else if (tieneCorreo || tieneTelefono) {
                respuestaBot = "✅ *Datos registrados con éxito.* Hemos recibido su contacto. Un asesor de ULMA Packaging se comunicará con usted a la brevedad. ¡Que tenga un excelente día! 👋";
            }
            else if (text.length > 5) {
                // Solo llega aquí si NO saludó y NO mandó correo/teléfono
                respuestaBot = "✅ *Información recibida.* Por favor comparta un **correo electrónico** y **número telefónico** para que un asesor pueda contactarlo formalmente. ¡Gracias!";
            } 
            else {
                // Para textos muy cortos que no sean números ni saludos
                respuestaBot = "🙌 ¡Hola! Gracias por comunicarte a *ULMA Packaging México*. Por favor elige una opción del 1 al 4.";
            }

            // --- ENVÍO DEL MENSAJE ---
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
