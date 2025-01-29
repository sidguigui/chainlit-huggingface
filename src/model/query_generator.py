from datetime import datetime
import asyncio
from utils.log import log


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

        prompt = f"""
        Você é um assistente especializado em SQL, treinado para gerar queries SQL válidas e funcionais com base na descrição do usuário e no esquema do banco de dados fornecido. Siga estas instruções cuidadosamente:

        ### Esquema do Banco de Dados:
        {db_schema_str}

        ### Contexto Dinâmico:
        - O mês atual é {current_month} (em formato numérico).
        - O ano atual é {current_year}.
        - Sempre use funções SQL compatíveis com PostgreSQL para lidar com datas dinamicamente, como `CURRENT_DATE`, `EXTRACT(MONTH FROM CURRENT_DATE)` e `EXTRACT(YEAR FROM CURRENT_DATE)`.

        ### Suas Tarefas:
        1. Analise a descrição fornecida pelo usuário.
        2. Considere apenas tabelas e colunas existentes no esquema fornecido.
        3. Use boas práticas para gerar uma query otimizada e funcional:
        - Utilize nomes de colunas e tabelas exatamente como aparecem no esquema.
        - Sempre que possível traga a tabela inteira, exemplificando os exemplos.
        - Inclua ordenação e limites, caso seja relevante para a solicitação do usuário.
        4. Responda exclusivamente com a query SQL finalizada, sem explicações ou comentários adicionais.

        ### Descrição do Usuário:
        {user_input}

        ### Dicas Adicionais:
        - Certifique-se de que a query seja válida e funcional no PostgreSQL.
        - Use funções nativas para lidar com manipulações de datas.
        - Sempre respeite o contexto atual de mês e ano ao trabalhar com dados temporais.

        ### Query SQL:
        """
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em SQL."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.5,
        )

        # Extrai a query da resposta
        query = (
            response.choices[0]
            .message.content.strip()
            .strip("```")
            .replace("sql\n", "")
            .strip()
        )

        # Log da query gerada
        log("[query_generator]", f"Query gerada pela API:\n{query}", "info")

        # Verifica se a query gerada contém um SELECT válido
        if "SELECT" not in query.upper():
            raise ValueError("Query gerada não parece válida.")

        return query

    except Exception as e:
        log("[query_generator]", f"Erro ao gerar a query SQL: {e}", "error")
        return "Não foi possível gerar uma query SQL válida. Verifique os dados fornecidos ou tente novamente."
