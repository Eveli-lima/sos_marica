from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

estados_do_usuario = {}  # Estado da conversa por número de telefone


# === Funções de menus ===

def menu_principal():
    return """
===============================
Bem-vindo ao SOS Maricá 👋

Como posso te ajudar?

[1] Saúde
[2] Telefones 
[3] Transporte

Digite o número ou palavra da opção.
==============================="""


def menu_saude():
    return """
🩺 Saúde - Escolha uma opção:

[1] Marcar consulta
[2] Consultar marcação

Digite 'voltar' ou '0' para retornar.
"""


# === Rota principal ===
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    remetente = request.form.get("From")
    msg = request.form.get('Body').strip().lower()
    resp = MessagingResponse()

    if remetente not in estados_do_usuario:
        estados_do_usuario[remetente] = "menu_principal"

    estado_atual = estados_do_usuario[remetente]
    response_msg = ""

    # Comando universal para voltar
    if msg in ["voltar", "0"]:
        estados_do_usuario[remetente] = "menu_principal"
        estado_atual = "menu_principal"

    # === Menus ===
    if estado_atual == "menu_principal":

        if msg == "1":
            estados_do_usuario[remetente] = "menu_saude"
            response_msg = menu_saude()

        elif msg == "2":
            response_msg = "🚨 Emergência:\n- SAMU: 192\n- Bombeiros: 193\n- Polícia: 190"

        elif msg == "3":
            response_msg = "🚌 Transporte:\n- Viação Nossa Senhora do Amparo\n- Consulte os itinerários no site da prefeitura"
            
        else:
            response_msg = menu_principal()

    elif estado_atual == "menu_saude":
        
        if msg == "1":
            response_msg = "📆 Para marcar uma consulta, acesse: https://www.marica.rj.gov.br/saude/"

        elif msg == "2":
            response_msg = "🔎 Para consultar marcação, entre com seu CPF no portal da saúde."

        else:
            response_msg = menu_saude()

     # === Fallback para garantir resposta ===
    #if not response_msg.strip():
        #response_msg = "❌ Ops, não entendi. Digite um número válido ou 'voltar' para retornar ao menu."

    # DEBUG
    #print(f"Usuário: {remetente}, Estado: {estado_atual}, Mensagem: '{msg}', Resposta: '{response_msg}'")

    # Enviar resposta
    resp.message(response_msg)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
