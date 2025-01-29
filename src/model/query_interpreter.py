from utils.log import log


async def query_interpreter(
    client, user_input: str, query_made: str, query_result: list
):
    try:
        log("[query_interpreter]", f"Query executada: {query_made}", "info")

        # Verificação de client válido
        if not client or not hasattr(client, "chat"):
            return "Erro: Cliente inválido ou não configurado corretamente."

        # Tratamento do resultado da query
        if not query_result:
            prompt = f"""
            O usuário perguntou: "{user_input}"
            A consulta gerada foi: {query_made}
            O resultado da consulta não retornou dados.
            Responda de forma clara informando que não há dados disponíveis para essa consulta.
            """
        elif isinstance(query_result, list) and all(
            isinstance(row, tuple) for row in query_result
        ):
            if len(query_result) == 1 and len(query_result[0]) == 1:
                resultado = query_result[0][0]
                prompt = f"""
                O usuário perguntou: "{user_input}"
                A consulta gerada foi: {query_made}
                O resultado foi: {resultado}.
                Responda de forma amigável, por exemplo: 'Foram feitos {resultado} pedidos'.
                """
            else:
                headers = ", ".join(
                    [f"Coluna {i + 1}" for i in range(len(query_result[0]))]
                )
                linhas = "\n".join([", ".join(map(str, row)) for row in query_result])
                prompt = f"""
                O usuário perguntou: "{user_input}"
                A consulta gerada foi: {query_made}
                O resultado foi uma tabela com as seguintes colunas: {headers}
                E os seguintes valores:
                {linhas}

                Formate a resposta de forma clara e organizada para exibição ao usuário.
                """
        else:
            prompt = f"""
            O usuário perguntou: "{user_input}"
            A consulta gerada foi: {query_made}
            O formato do resultado da consulta não foi reconhecido.
            Responda de forma adequada informando sobre o erro.
            """

        # Chamada assíncrona da API
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente que responde com base em resultados de banco de dados.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.5,
            )
        except Exception as e:
            log("[query_interpreter]", f"Erro ao chamar a API: {e}", "error")
            return "Erro ao comunicar com a API."

        # Extração correta da resposta
        if not response or not response.choices:
            return "Erro: Resposta inválida da IA."

        response_text = response.choices[0].message.content.strip()

        return response_text

    except Exception as e:
        log("[query_interpreter]", f"Erro inesperado: {e}", "error")
        return "Desculpe, houve um erro ao processar sua solicitação."
