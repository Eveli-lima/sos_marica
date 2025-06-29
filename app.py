from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    msg = request.form.get('Body').strip().lower()
    resp = MessagingResponse()
    response_msg = ""

    if msg == "saúde":
        response_msg = "🏥 Serviços de saúde em Maricá:\n- Hospital Municipal\n- UPA Inoã\n- Tel: (21) XXXX-XXXX"
    elif msg == "educação":
        response_msg = "📚 Educação em Maricá:\n- Escola Municipal Zilda Arns\n- Escola Técnica Maricá"
    elif msg == "emergência":
        response_msg = "🚨 Emergências:\n- SAMU: 192\n- Bombeiros: 193\n- Polícia: 190"
    elif msg == "transporte":
        response_msg = "🚌 Transporte:\n- Viação Nossa Senhora do Amparo\n- Itinerários no site da Prefeitura"
    else:
        response_msg = ("🤖 SOS Maricá Bot\n"
                        "Digite uma das opções abaixo:\n"
                        "- saúde\n"
                        "- educação\n"
                        "- emergência\n"
                        "- transporte")

    resp.message(response_msg)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
