from utils.log import log
import asyncio


async def query_interpreter(client, user_input: str, query_made: str, query_result: list):
    # Converter o resultado da query em uma tabela mais legível
    log("[query_interpreter]", f"Interpretando a query: {query_result}", "info")
    formatted_result = "\n".join(
        [f"{' | '.join(map(str, row))}" for row in query_result]
    )
    log("[query_interpreter]", f"Resultado formatado: {formatted_result}", "info")
    prompt = f"""
    Você é um assistente especializado em interpretar e apresentar resultados de consultas SQL de forma clara e concisa. 

    A consulta feita pelo usuário foi: "{user_input}"
    A query executada foi: "{query_made}"

    O resultado da query é o seguinte, organizado em forma de tabela:

    {formatted_result}

    A tabela acima contém os dados retornados pela consulta SQL. Seu objetivo é apresentar esses dados de maneira amigável, com as colunas claramente identificadas e as informações apresentadas de forma concisa. 

    Use o formato de tabela Markdown para exibir as informações. Exemplo de resposta:

    | Variável        | Valor       | Descrição                                |
    |-----------------|-------------|------------------------------------------|
    | ordernumber     | 10107       | Número único atribuído ao pedido         |
    | quantityordered | 30          | Quantidade de unidades solicitadas      |
    | priceeach       | 95.7        | Preço unitário do produto                |

    Se houver várias linhas, cada linha de dados deve ser apresentada como uma linha de tabela. Caso não haja dados para uma coluna, deixe em branco, mas sempre forneça uma tabela organizada com cabeçalhos.

    Responda apenas com a tabela em Markdown, sem explicações adicionais. 
    """

    
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create, model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Você é um assistente especializado em interpretação de dados."},
                      {"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        log("[query_interpreter]", f"Erro na IA: {str(e)}", "error")
        return "Houve um erro ao processar sua solicitação. Tente novamente."
