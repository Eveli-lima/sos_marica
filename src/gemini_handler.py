import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv

# Importa as ferramentas que criamos no outro arquivo
from src.tools import get_horarios_onibus

# Carrega as variáveis de ambiente. É uma boa prática ter aqui também,
# para o caso de testar este arquivo de forma isolada.
load_dotenv()

# Variável global para armazenar o modelo (padrão de inicialização preguiçosa)
_modelo_gemini = None

def _configure_gemini():
    """
    Função interna para configurar e retornar o modelo Generative AI.
    Só é chamada na primeira vez que o modelo é necessário.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A chave GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env")
    
    genai.configure(api_key=api_key)
    
    system_prompt = (
        "Você é o 'SOS Maricá', um assistente virtual amigável e prestativo para os cidadãos de Maricá, RJ. "
        "Sua principal função é fornecer informações úteis sobre a cidade. "
        "Seja sempre educado e direto em suas respostas. "
        "Responda exclusivamente em português do Brasil. "
        "Se você não souber a resposta para uma pergunta ou não tiver uma ferramenta para isso, "
        "informe educadamente que não possui essa informação no momento."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-1.0-pro',
        system_instruction=system_prompt,
        tools=[get_horarios_onibus]
    )
    return model

def _get_model():
    """
    Retorna a instância do modelo, inicializando-a se ainda não tiver sido criada.
    """
    global _modelo_gemini
    if _modelo_gemini is None:
        _modelo_gemini = _configure_gemini()
    return _modelo_gemini

def get_gemini_response(historico_chat, nova_mensagem_usuario: str) -> str:
    """
    Inicia uma sessão de chat com o Gemini, envia uma nova mensagem e retorna a resposta.
    """
    try:
        # Pega a instância do modelo usando a função auxiliar
        modelo = _get_model()
        
        # O resto da função permanece igual
        chat = modelo.start_chat(history=historico_chat)
        response = chat.send_message(nova_mensagem_usuario)
        return response.text
        
    except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated) as e:
        print(f"ERRO DE PERMISSÃO/AUTENTICAÇÃO: {e}")
        mensagem_erro = (
            "🚨 **Erro de Autenticação com a API do Google.**\n\n"
            "Parece que há um problema com a sua chave de API. Por favor, verifique os seguintes pontos:\n\n"
            "1.  **Chave de API:** A `GEMINI_API_KEY` no seu ficheiro `.env` está correta e completa?\n"
            "2.  **API Ativada:** A API 'Generative Language' está ativada no seu projeto Google Cloud?\n"
            "3.  **Faturação:** O seu projeto no Google Cloud tem uma conta de faturação associada? (Isto é, por vezes, necessário, mesmo para o nível gratuito)."
        )
        return mensagem_erro
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao se comunicar com a API do Gemini: {e}")
        return "Desculpe, estou com dificuldades técnicas para me conectar. Por favor, tente novamente em alguns instantes."

# Bloco de teste para executar este arquivo diretamente
if __name__ == '__main__':
    historico_teste = []
    
    pergunta = "quais os horarios do onibus e03?"
    print(f"Usuário: {pergunta}")
    resposta = get_gemini_response(historico_teste, pergunta)
    print(f"Assistente: {resposta}")

