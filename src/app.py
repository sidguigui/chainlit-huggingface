import chainlit as cl  # type: ignore
from models.huggingface_chainlit import get_model_response


@cl.on_message
async def main(message: str):
    response = get_model_response(message)
    await cl.Message(content=response).send()
