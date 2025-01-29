import json
import os
from dotenv import load_dotenv, find_dotenv  # type: ignore
import chainlit as cl  # type: ignore
from openai import OpenAI  # type: ignore
from model.query_generator import query_generator
from database.query_handler import query_handler
from model.query_interpreter import query_interpreter
from utils.log import log

load_dotenv(find_dotenv())

# Armazenando o histórico das mensagens
conversation_history = []  # Pode ser um banco de dados ou variável global

def load_db_schema(schema_path="src/utils/db_schema.json"):
    with open(schema_path, "r") as f:
        return json.load(f)


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
db_schema = load_db_schema()


@cl.on_message
async def main(message: cl.Message):
    if not message:
        log("[app]", "Mensagem recebida é None.", "warn")
        return

    try:
        log("[app]", f"Mensagem recebida: {message.content}", "info")
        user_input = message.content

        # Adiciona a nova mensagem ao histórico
        conversation_history.append(f"Usuário: {user_input}")
        
        # Adiciona o histórico de conversas ao prompt de entrada
        history_str = "\n".join(conversation_history)
        
        # Passa o histórico junto com a nova entrada
        query = await query_generator(
            client=client, 
            user_input=user_input, 
            db_schema=db_schema,
            history=history_str  # Passa o histórico
        )

        log("[app]", f"Query gerada: {query}", "info")
        query_result = await query_handler(query)
        result_formatted = await query_interpreter(client, query, query_result, db_schema)

        # Adiciona a resposta do bot ao histórico
        conversation_history.append(f"Bot: {result_formatted}")
        
        await cl.Message(content=f"Resultado da consulta:\n\n{result_formatted}").send()

    except Exception as e:
        log("[app]", f"Erro no App: {e}", "error")
        await cl.Message(
            content="Desculpe, ocorreu um erro ao processar sua solicitação."
        ).send()
