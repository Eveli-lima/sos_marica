import os
import asyncio
import pathlib # Módulo para lidar com caminhos de arquivos
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv, find_dotenv # Adicionamos find_dotenv
import google.generativeai as genai

# --- NOVO BLOCO DE DIAGNÓSTICO DE ARQUIVO ---
print("--- Verificando a presença do arquivo .env ---")
# Procura pelo arquivo .env no diretório atual
env_path = pathlib.Path('.').resolve() / '.env'
if env_path.is_file():
    print(f"✅ Arquivo .env FISICAMENTE ENCONTRADO em: {env_path}")
else:
    # Mostra o caminho completo onde o arquivo era esperado
    diretorio_atual = pathlib.Path('.').resolve()
    print(f"❌ ATENÇÃO: Nenhum arquivo .env foi encontrado no diretório: {diretorio_atual}")
    print("   Por favor, verifique se o arquivo .env está nesta pasta e se o nome está exatamente '.env'.")
print("-------------------------------------------\n")
# --- FIM DO NOVO BLOCO ---

# Carrega as variáveis de ambiente (nossas chaves secretas)
# Esta nova versão procura o arquivo .env de forma mais inteligente
load_dotenv(find_dotenv())

# --- BLOCO DE DIAGNÓSTICO (Temporário) ---
print("--- Iniciando diagnóstico ---")
gemini_key_lida = os.getenv("GEMINI_API_KEY")
telegram_token_lido = os.getenv("TELEGRAM_BOT_TOKEN")

if gemini_key_lida:
    print("✅ Chave GEMINI_API_KEY foi lida com sucesso!")
    # Vamos configurar o genai aqui para um teste completo
    try:
        genai.configure(api_key=gemini_key_lida)
        print("✅ A biblioteca Gemini foi configurada com sucesso.")
    except Exception as e:
        print(f"❌ ERRO ao configurar a biblioteca Gemini: {e}")
else:
    print("❌ FALHA: A chave GEMINI_API_KEY não foi encontrada no ambiente.")

if telegram_token_lido:
    print("✅ Token TELEGRAM_BOT_TOKEN foi lido com sucesso!")
else:
    print("❌ FALHA: O token TELEGRAM_BOT_TOKEN não foi encontrado no ambiente.")
print("--- Fim do diagnóstico ---\n")
# --- FIM DO BLOCO ---


# Importa a função que se comunica com o Gemini
# O 'src.' é necessário por causa da estrutura de pastas que criamos
from src.gemini_handler import get_gemini_response


# Dicionário para armazenar o histórico de conversas de cada usuário
historicos_usuarios = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de boas-vindas quando o comando /start é emitido."""
    user_id = update.effective_user.id
    # Limpa o histórico do usuário para começar uma nova conversa
    historicos_usuarios[user_id] = [] 
    
    mensagem_boas_vindas = (
        "👋 Olá! Eu sou o SOS Maricá, seu assistente virtual para informações da cidade.\n\n"
        "Como posso te ajudar hoje? Você pode me perguntar sobre os horários dos 'vermelhinhos', por exemplo."
    )
    await update.message.reply_text(mensagem_boas_vindas)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa as mensagens de texto recebidas dos usuários."""
    user_id = update.effective_user.id
    mensagem_usuario = update.message.text

    # Garante que o usuário tenha um histórico, mesmo que comece sem o /start
    if user_id not in historicos_usuarios:
        historicos_usuarios[user_id] = []
    
    # Recupera o histórico da conversa atual
    historico_atual = historicos_usuarios[user_id]

    # Mostra um feedback "digitando..." para o usuário
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # Obtém a resposta do Gemini
    resposta_assistente = get_gemini_response(historico_atual, mensagem_usuario)

    # Atualiza o histórico com a nova interação
    historicos_usuarios[user_id].append({'role': 'user', 'parts': [mensagem_usuario]})
    historicos_usuarios[user_id].append({'role': 'model', 'parts': [resposta_assistente]})

    # Envia a resposta para o usuário no Telegram
    await update.message.reply_text(resposta_assistente)

def main() -> None:
    """Inicia o bot do Telegram."""
    # A variável `telegram_token_lido` do nosso diagnóstico já contém o token
    if not telegram_token_lido:
        raise ValueError("O token TELEGRAM_BOT_TOKEN não foi encontrado. Verifique seu arquivo .env")

    # Cria a aplicação do bot
    application = Application.builder().token(telegram_token_lido).build()

    # Adiciona os handlers para os comandos e mensagens
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot SOS Maricá no ar! Pressione Ctrl+C para encerrar.")

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()

