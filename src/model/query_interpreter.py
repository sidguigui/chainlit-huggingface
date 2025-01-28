import asyncio


async def query_interpreter(client, user_input: str, query_made: str, query_result: list):
    try:
        # Verificação de nulidade para garantir que o 'client' tenha um valor válido
        if not client or not hasattr(client, "chat") or not hasattr(client.chat, "completions"):
            return "Erro: Cliente inválido ou não configurado corretamente."
        
        # Formatação do prompt dependendo do tipo de dados retornado pela consulta
        if query_result and isinstance(query_result[0], tuple):
            if len(query_result) == 1 and len(query_result[0]) == 1:
                prompt = f"""
                O usuário fez a seguinte pergunta: "{user_input}"
                A consulta gerada foi: {query_made}
                O resultado da consulta foi o valor {query_result[0][0]}.
                Sua tarefa é gerar uma resposta clara e objetiva.
                Exemplo de resposta: 'X pedidos foram feitos', onde X é o valor.
                """
            else:
                prompt = f"""
                O usuário fez a seguinte pergunta: "{user_input}"
                A consulta gerada foi: {query_made}
                O resultado da consulta retornou os seguintes dados: {query_result}.
                Sua tarefa é gerar uma resposta adequada para exibir esses dados.
                Caso seja uma tabela, formate os dados com cabeçalhos e linhas.
                """
        else:
            prompt = f"""
            O usuário fez a seguinte pergunta: "{user_input}"
            A consulta gerada foi: {query_made}
            O resultado da consulta não retornou dados esperados ou é indefinido.
            Sua tarefa é responder adequadamente sobre a situação.
            """
        
        # Chama a API de forma assíncrona usando asyncio.to_thread para evitar bloqueio
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
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
            print(f"Erro ao chamar a API: {e}")
            return "Erro ao comunicar com a API."

        # Verifica a validade da resposta da API
        if not response or "choices" not in response or not response["choices"]:
            return "Erro: Resposta inválida da IA."

        # Extrai a resposta da IA
        response_text = response["choices"][0]["message"]["content"].strip()

        return response_text

    except Exception as e:
        # Erro de captura geral, para assegurar que qualquer falha seja tratada
        print(f"Erro ao gerar a resposta: {e}")
        return "Desculpe, houve um erro ao processar sua solicitação."
