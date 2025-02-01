import json
import os
import chainlit as cl  # type: ignore
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # type: ignore
from langchain.chains import create_sql_query_chain  # type: ignore
from langchain_community.utilities import SQLDatabase  # type: ignore
from sqlalchemy import create_engine, text  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from langchain_core.output_parsers import StrOutputParser  # type: ignore
from langchain_core.prompts import PromptTemplate  # type: ignore
from utils.log import log

load_dotenv()


def load_db_schema(schema_path="src/utils/db_schema.json"):
    with open(schema_path, "r") as f:
        return json.load(f)


schema_info = load_db_schema()

openai_key = os.getenv("OPENAI_API_KEY")

db_uri = (
    f"postgresql://{os.environ.get('DATABASEUSER')}:{os.environ.get('DATABASEPSSW')}@"
    f"{os.environ.get('DATABASEHOST')}:{os.environ.get('DATABASEPORT')}/{os.environ.get('DATABASENAME')}"
)

db = SQLDatabase.from_uri(db_uri)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
chain = create_sql_query_chain(llm, db)

engine = create_engine(db_uri, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

answer = answer_prompt | llm | StrOutputParser()


# Lista para armazenar o histórico de mensagens
chat_history = []

@cl.on_message
async def main(message: cl.Message):
    log("[main]", f"Mensagem recebida: {message.content}", "info")

    # Adicionar a mensagem do usuário ao histórico
    chat_history.append({"role": "user", "content": message.content})

    # Criar o histórico de mensagens para o prompt, incluindo a estrutura do banco de dados e as mensagens anteriores
    prompt_context = f"""
    Você é um assistente SQL. Aqui está a estrutura do banco de dados para referência:
    {json.dumps(schema_info, indent=4)}

    Histórico de conversa:
    {json.dumps(chat_history, indent=4)}

    Baseado nisso, gere uma consulta SQL precisa para a seguinte pergunta:
    {message.content}
    """
    
    log("[main]", "Gerando a consulta SQL a partir do contexto", "info")

    response = chain.invoke({"question": prompt_context})
    sql_query = response.strip()

    log("[main]", f"Consulta SQL gerada: {sql_query}", "info")

    if "COUNT(" in sql_query:
        sql_query = sql_query.replace("LIMIT 10", "")
        log("[main]", "Removido 'LIMIT 10' da consulta devido a uso de 'COUNT'", "info")

    try:
        result = session.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()

        if not rows:
            result_text = "Nenhum resultado encontrado."
            table_text = ""
        else:
            table = "| " + " | ".join(columns) + " |\n"
            table += "|" + "|".join(["---"] * len(columns)) + "|\n"
            for row in rows:
                table += "| " + " | ".join(map(str, row)) + " |\n"

            table_text = f"**Tabela de Resultados:**\n\n{table}"
            result_text = table if len(rows) > 1 else " | ".join(map(str, rows[0]))

        log("[main]", f"Resultado da consulta: {result_text}", "info")

    except Exception as e:
        result_text = f"Erro ao executar a consulta: {str(e)}"
        table_text = ""
        log("[main]", f"Erro ao executar a consulta SQL: {str(e)}", "error")


    final_answer = answer.invoke(
        {"question": message.content, "query": sql_query, "result": result_text}
    )
    
    chat_history.append({"role": "system", "content": final_answer})


    log("[main]", f"Resposta final gerada: {final_answer}", "info")

    await cl.Message(
        content=f"**Consulta SQL Gerada:**\n\n{sql_query}\n\n{table_text}\n\n**Resposta:**\n{final_answer}"
    ).send()
