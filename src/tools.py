import json
from pathlib import Path

# Constrói o caminho para o arquivo de dados de forma segura
# Isso garante que o código funcionará em qualquer computador, independente do sistema operacional
caminho_dados = Path(__file__).parent.parent / "data" / "vermelhinhos.json"

def get_horarios_onibus(codigo_linha: str) -> str:
    """
    Busca e retorna os horários de uma linha de ônibus específica.

    Args:
        codigo_linha (str): O código da linha de ônibus (ex: "E03").

    Returns:
        str: Uma string formatada com os horários ou uma mensagem de erro.
    """
    try:
        # Abre e carrega o arquivo JSON com os dados dos ônibus
        with open(caminho_dados, 'r', encoding='utf-8') as f:
            dados_onibus = json.load(f)

        codigo = codigo_linha.strip().upper()
        info_linha = dados_onibus.get(codigo)

        if not info_linha:
            return f"Não encontrei informações para a linha {codigo}. Por favor, verifique o código."

        nome = info_linha.get('nome', 'Nome não disponível')
        saida_rodoviaria = ", ".join(info_linha.get('saida_rodoviaria', []))
        saida_bairro = ", ".join(info_linha.get('saida_bairro', []))

        # Formata a resposta de forma clara para o usuário
        resposta = (
            f"🚌 Horários para a linha {codigo} - {nome}:\n\n"
            f"➡️ Saídas da Rodoviária: {saida_rodoviaria}\n"
            f"⬅️ Saídas do Bairro: {saida_bairro}"
        )
        return resposta

    except FileNotFoundError:
        return "Desculpe, não consegui encontrar o arquivo com os horários dos ônibus no momento."
    except json.JSONDecodeError:
        return "Desculpe, parece que há um problema com o formato do arquivo de horários."
    except Exception as e:
        # Captura qualquer outro erro inesperado
        print(f"Ocorreu um erro inesperado em get_horarios_onibus: {e}")
        return "Ocorreu um erro inesperado ao buscar os horários. A equipe técnica já foi notificada."

# Exemplo de como usar a função (para testes)
if __name__ == '__main__':
    print(get_horarios_onibus("E01"))
    print("\n---\n")
    print(get_horarios_onibus("E99")) # Testando uma linha que não existe
