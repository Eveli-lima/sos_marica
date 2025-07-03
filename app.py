from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

estados_do_usuario = {}

vermelhinhos = {
    "E03": {
        "nome": "UBATIBA",
        "saida_rodoviaria": ["04:50", "05:50", "06:20", "06:55", "07:30", "08:05"],
        "saida_bairro": ["05:10", "06:10", "06:40", "07:15", "07:50", "08:25"]
    },
    "E04": {
        "nome": "SILVADO",
        "saida_rodoviaria": ["04:40", "05:55", "07:05", "08:15", "09:25"],
        "saida_bairro": ["05:05", "06:20", "07:30", "08:40", "09:50"]
    }
}

# Menus
def menu_principal():
    return """
===============================
Bem-vindo ao SOS Maricá 👋

Como posso te ajudar?

[1] Saúde
[2] Telefones 
[3] Transporte

Digite o número ou palavra da opção.
Digite [F] para encerrar o atendimento.
===============================
"""

def menu_saude():
    return """
===============================
🩺 Saúde - Escolha uma opção:

[1] Marcar consulta
[2] Consultar marcação

Digite [V] para voltar ou [0] para o menu principal.
===============================
"""

def menu_transporte():
    return """
===============================
🚌 Transporte - Escolha uma opção:

[1] Vermelhinho
[2] Viação Nossa Senhora do Amparo
[3] Vans

Digite [V] para voltar ou [0] para o menu principal.
===============================
"""

def menu_vermelhinhos():
    texto = "🚌 Escolha o Vermelhinho:\n"
    for codigo, info in vermelhinhos.items():
        texto += f"[{codigo}] {info['nome']}\n"
    texto += "\nDigite o código, [V] para voltar ou [0] para o menu principal."
    return texto

def horarios_vermelhinho(codigo):
    info = vermelhinhos.get(codigo.upper())
    if not info:
        return "❌ Código inválido. Tente novamente."
    texto = f"Horários do Vermelhinho {info['nome']}:\n\n"
    texto += "Saída Rodoviária:\n" + ", ".join(info["saida_rodoviaria"]) + "\n\n"
    texto += "Saída Bairro:\n" + ", ".join(info["saida_bairro"]) + "\n\n"
    texto += "Digite outro código, [V] para voltar ou [0] para o menu principal."
    return texto

# Rota principal
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    remetente = request.form.get("From")
    msg = request.form.get('Body').strip().lower()
    resp = MessagingResponse()
    response_msg = ""

    if remetente not in estados_do_usuario:
        estados_do_usuario[remetente] = "menu_principal"
        response_msg = menu_principal()
        resp.message(response_msg)
        print(f"Usuário: {remetente}, Estado: menu_principal, Mensagem: {msg}, Resposta: {response_msg}")
        return str(resp)

    estado_atual = estados_do_usuario[remetente]

    # Encerrar atendimento
    if msg == "f":
        estados_do_usuario.pop(remetente, None)
        response_msg = "✅ Atendimento encerrado. Digite qualquer coisa para começar novamente."
        resp.message(response_msg)
        print(f"Usuário: {remetente}, Estado: ENCERRADO, Mensagem: {msg}, Resposta: {response_msg}")
        return str(resp)

    # Voltar para o menu principal
    if msg == "0":
        estados_do_usuario[remetente] = "menu_principal"
        response_msg = menu_principal()
        resp.message(response_msg)
        print(f"Usuário: {remetente}, Estado: menu_principal, Mensagem: {msg}, Resposta: {response_msg}")
        return str(resp)

    # Voltar para o menu anterior
    if msg in ["v", "voltar"]:
        if estado_atual.startswith("vermelhinho_") or estado_atual == "vermelhinho_selecao":
            estados_do_usuario[remetente] = "menu_transporte"
            response_msg = menu_transporte()
        elif estado_atual == "menu_transporte":
            estados_do_usuario[remetente] = "menu_principal"
            response_msg = menu_principal()
        elif estado_atual == "menu_saude":
            estados_do_usuario[remetente] = "menu_principal"
            response_msg = menu_principal()
        else:
            estados_do_usuario[remetente] = "menu_principal"
            response_msg = menu_principal()
        resp.message(response_msg)
        print(f"Usuário: {remetente}, Estado: {estado_atual}, Mensagem: {msg}, Resposta: {response_msg}")
        return str(resp)

    # Lógica dos menus
    if estado_atual == "menu_principal":
        if msg == "1":
            estados_do_usuario[remetente] = "menu_saude"
            response_msg = menu_saude()
        elif msg == "2":
            response_msg = "🚨 Emergência:\n- SAMU: 192\n- Bombeiros: 193\n- Polícia: 190\n\nDigite [V] para voltar ou [0] para o menu principal."
        elif msg == "3":
            estados_do_usuario[remetente] = "menu_transporte"
            response_msg = menu_transporte()
        else:
            response_msg = menu_principal()

    elif estado_atual == "menu_saude":
        if msg == "1":
            response_msg = "📆 Para marcar uma consulta, acesse: https://www.marica.rj.gov.br/saude/"
        elif msg == "2":
            response_msg = "🔎 Para consultar marcação, entre com seu CPF no portal da saúde."
        else:
            response_msg = menu_saude()

    elif estado_atual == "menu_transporte":
        if msg == "1":
            estados_do_usuario[remetente] = "vermelhinho_selecao"
            response_msg = menu_vermelhinhos()
        elif msg == "2":
            response_msg = "🚧 Em breve: Viação Nossa Senhora do Amparo."
        elif msg == "3":
            response_msg = "🚧 Em breve: Informações sobre vans."
        else:
            response_msg = menu_transporte()

    elif estado_atual == "vermelhinho_selecao":
        codigo = msg.upper()
        if codigo in vermelhinhos:
            estados_do_usuario[remetente] = f"vermelhinho_{codigo}"
            response_msg = horarios_vermelhinho(codigo)
        else:
            response_msg = "❌ Código inválido.\n" + menu_vermelhinhos()

    elif estado_atual.startswith("vermelhinho_"):
        codigo = msg.upper()
        if codigo in vermelhinhos:
            response_msg = horarios_vermelhinho(codigo)
        else:
            response_msg = "❌ Código inválido.\n" + menu_vermelhinhos()

    else:
        response_msg = "❌ Não entendi. Digite uma opção válida, [V] para voltar ou [0] para o menu principal."

    resp.message(response_msg)

    print(f"Usuário: {remetente}, Estado: {estado_atual}, Mensagem: {msg}, Resposta: {response_msg}")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
