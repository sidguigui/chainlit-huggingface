import json
import os
from dotenv import load_dotenv, find_dotenv
import chainlit as cl  # type: ignore
from openai import OpenAI  # type: ignore
from model.query_generator import query_generator  # Importa a função de geração de query
from database.query_handler import query_handler  # Importa a função para execução da consulta no banco

load_dotenv(find_dotenv())

def load_db_schema(schema_path="src/utils/db_schema.json"):
    with open(schema_path, 'r') as f:
        return json.load(f)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
db_schema = load_db_schema()
 
@cl.on_message
async def main(message: cl.Message):
    try:
        print(f"Mensagem recebida: {message.content}")  # Log da mensagem
        user_input = message.content
        query = await query_generator(client=client, user_input=user_input, db_schema=db_schema)

        print(f"Query gerada: {query}")  # Log da query gerada

        result = await query_handler(query)
        print(f"Resultado da consulta: {result}")  # Log do resultado

        await cl.Message(content=f"Resultado da consulta:\n\n{result}").send()

    except Exception as e:
        print(f"Erro: {e}")
        await cl.Message(
            content="Desculpe, ocorreu um erro ao processar sua solicitação."
        ).send()