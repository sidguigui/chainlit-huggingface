from datetime import datetime


async def query_generator(client, user_input: str, db_schema: dict):
    try:
        # Obter o mês e ano atuais dinamicamente
        current_month = datetime.now().month
        current_year = datetime.now().year

        # Converte o esquema JSON em uma representação textual mais detalhada para o prompt
        db_schema_str = ""
        for table_name, table_info in db_schema.items():
            # Adiciona informações sobre a tabela
            db_schema_str += f"Tabela: {table_name}\n"
            db_schema_str += f"Descrição: {table_info['description']}\n"
            db_schema_str += "Colunas:\n"

            # Adiciona informações sobre as colunas da tabela
            for column in table_info["columns"]:
                col_name = column["name"]
                col_type = column["data_type"]
                col_desc = column["description"]
                example_value = column.get("example", "N/A")

                db_schema_str += f"- {col_name} ({col_type}): {col_desc} (Exemplo: {example_value})\n"

            db_schema_str += "\n"

        # Log do esquema para verificar se está correto
        print(f"Esquema do banco de dados:\n{db_schema_str}")

        # Atualizar o prompt com contexto dinâmico de data
        prompt = f"""
        Você é um assistente SQL. Sua tarefa é gerar uma query SQL válida com base na descrição fornecida pelo usuário e no esquema do banco de dados.

        Esquema do banco de dados:
        {db_schema_str}

        Contexto adicional:
        - O mês atual é {current_month} (numérico).
        - O ano atual é {current_year}.
        - Sempre que possível, use funções SQL para lidar com datas de forma dinâmica, como MONTH(CURRENT_DATE) e YEAR(CURRENT_DATE).

        Descrição do usuário: {user_input}

        Dicas:
        - Certifique-se de que a query esteja correta e funcional.
        - Inclua apenas tabelas e colunas válidas do esquema fornecido.
        - Sempre que possível, use funções SQL para lidar com datas dinamicamente.
        - Responda apenas com a query SQL final, sem explicações adicionais.

        Query SQL:
        """

        # Log do prompt
        print(f"Prompt gerado para a API:\n{prompt}")

        # Chamada para a API GPT-4
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em SQL."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.5,
        )

        # Extrai a query da resposta
        query = response.choices[0].message.content.strip()

        # Log da query gerada
        print(f"Query gerada pela API:\n{query}")

        # Verifica se a query gerada contém um SELECT válido
        if "SELECT" not in query.upper():
            raise ValueError("Query gerada não parece válida.")

        return query

    except Exception as e:
        print(f"Erro ao gerar a query SQL: {e}")
        return "Não foi possível gerar uma query SQL válida. Verifique os dados fornecidos ou tente novamente."
