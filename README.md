# 🤖 SOS Maricá - Telegram Bot

Bem-vindo ao SOS Maricá! Este é um bot para o Telegram criado para fornecer informações úteis sobre a cidade de Maricá, RJ.

## ✨ Funcionalidades

* Responde a perguntas sobre horários dos "vermelhinhos".
* Mantém o histórico da conversa para um diálogo mais natural.
* (Em breve mais funcionalidades...)

## ⚙️ Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/Eveli-lima/sos_marica.git
    cd sos_marica
    ```
2.  **Crie um ambiente virtual e instale as dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Configure as suas chaves secretas:**
    * Crie um ficheiro chamado `.env` na pasta principal.
    * Adicione as seguintes linhas, substituindo pelas suas chaves:
        ```
        GEMINI_API_KEY="SUA_CHAVE_DO_GEMINI"
        TELEGRAM_BOT_TOKEN="SEU_TOKEN_DO_TELEGRAM"
        ```
4.  **Execute o bot:**
    ```bash
    python app_telegram.py
    ```