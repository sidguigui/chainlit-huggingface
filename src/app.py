import json
import os
from dotenv import load_dotenv, find_dotenv
import chainlit as cl  # type: ignore
from openai import OpenAI  # type: ignore
from model.query_generator import query_generator
from database.query_handler import query_handler
from model.query_interpreter import query_interpreter

load_dotenv(find_dotenv())


def load_db_schema(schema_path="src/utils/db_schema.json"):
    with open(schema_path, "r") as f:
        return json.load(f)


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
db_schema = load_db_schema()


@cl.on_message
async def main(message: cl.Message):
    if not message:
        print("Mensagem recebida é None.")
        return  # Retorna imediatamente se a mensagem for None

    try:
        print(f"Mensagem recebida: {message.content}")  # Log da mensagem
        user_input = message.content

        # Geração da query com a função query_generator
        query = await query_generator(client=client, user_input=user_input, db_schema=db_schema)

        print(f"Query gerada: {query}")  # Log da query gerada

        # Execução da consulta no banco de dados
        query_result = await query_handler(query)

        result_formatted = await query_interpreter(client, query ,query_result, db_schema)
        print(f"Resultado da consulta: {result_formatted}")  # Log do resultado

        # Envio da resposta formatada para o usuário
        await cl.Message(content=f"Resultado da consulta:\n\n{query_result}").send()

    except Exception as e:
        print(f"Erro: {e}")
        await cl.Message(content="Desculpe, ocorreu um erro ao processar sua solicitação.").send()
