import os
from google import genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv

# Importa as ferramentas que criamos no outro arquivo
from src.tools import get_horarios_onibus

# Carrega as variáveis de ambiente.
load_dotenv()

# Variáveis globais para armazenar o CLIENTE e as CONFIGURAÇÕES
_client_gemini = None
_configuracoes_gemini = None

def _configure_gemini():
    """
    Função interna para configurar e retornar o CLIENTE e as CONFIGURAÇÕES.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A chave GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env")
    
    # MUDANÇA 1: Criamos o Cliente, como na documentação
    client = genai.Client(api_key=api_key)
    
    system_prompt = (
        "Você é o 'SOS Maricá', um assistente virtual amigável e prestativo para os cidadãos de Maricá, RJ. "
        "Sua principal função é fornecer informações úteis sobre a cidade. "
        "Seja sempre educado e direto em suas respostas. "
        "Responda exclusivamente em português do Brasil. "
        "Se você não souber a resposta para uma pergunta ou não tiver uma ferramenta para isso, "
        "informe educadamente que não possui essa informação no momento."
    )
    
    # MUDANÇA 2: Guardamos as configs, mas não criamos um 'modelo'
    configuracoes = {
        "system_instruction": system_prompt,
        "tools": [get_horarios_onibus]
    }
    
    # Retornamos o cliente e as configs
    return client, configuracoes

def _get_client_e_config():
    """
    Retorna a instância do cliente e das configs, inicializando-os se necessário.
    """
    global _client_gemini, _configuracoes_gemini
    if _client_gemini is None:
        _client_gemini, _configuracoes_gemini = _configure_gemini()
    return _client_gemini, _configuracoes_gemini

def get_gemini_response(historico_chat, nova_mensagem_usuario: str) -> str:
    """
    Gera uma resposta do Gemini usando a nova lógica 'stateless'.
    """
    try:
        # MUDANÇA 3: Pegamos o cliente e as configs
        client, config = _get_client_e_config()

        # MUDANÇA 4: Preparamos o 'contents' para a API
        # A API nova quer o histórico + a nova mensagem juntos
        
        # 1. Copia o histórico
        contents_para_api = list(historico_chat)
        
        # 2. Adiciona a nova mensagem do usuário
        contents_para_api.append({'role': 'user', 'parts': [nova_mensagem_usuario]})
        
        # MUDANÇA 5: Chamamos 'generate_content'
        # Esta é a sintaxe correta da biblioteca 'google-genai'
        # Não usamos mais 'start_chat'
        response = client.generate_content(
            model='models/gemini-1.5-flash-latest',
            contents=contents_para_api,
            system_instruction=config["system_instruction"],
            tools=config["tools"]
        )
        
        return response.text
        
    except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated) as e:
        print(f"ERRO DE PERMISSÃO/AUTENTICAÇÃO: {e}")
        mensagem_erro = (
            "🚨 **Erro de Autenticação com a API do Google.**\n\n"
            "Verifique sua chave de API e se a 'Generative Language' API está ativa no seu projeto Google Cloud."
        )
        return mensagem_erro
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao se comunicar com a API do Gemini: {e}")
        return "Desculpe, estou com dificuldades técnicas para me conectar. Por favor, tente novamente em alguns instantes."

# Bloco de teste
if __name__ == '__main__':
    historico_teste = []
    
    pergunta = "quais os horarios do onibus e03?"
    print(f"Usuário: {pergunta}")
    resposta = get_gemini_response(historico_teste, pergunta)
    print(f"Assistente: {resposta}")
    
    # Simula um histórico
    historico_teste.append({'role': 'user', 'parts': [pergunta]})
    historico_teste.append({'role': 'model', 'parts': [resposta]})
    
    pergunta2 = "e do e05?"
    print(f"Usuário: {pergunta2}")
    resposta2 = get_gemini_response(historico_teste, pergunta2)
    print(f"Assistente: {resposta2}")