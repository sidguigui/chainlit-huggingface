import chainlit as cl
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Inicialize o modelo fora da função para carregar apenas uma vez
model_name = "gpt2"
local_dir = "./models_cache/distilgpt2"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Carregando o modelo...")
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=local_dir)
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=local_dir)
model = model.to(device)

@cl.step(type="tool")
async def generate_response(user_input: str):
    """
    Gera uma resposta do modelo para a entrada do usuário.

    Args:
        user_input: Mensagem do usuário.

    Returns:
        Resposta gerada pelo modelo.
    """
    # Tokenize a entrada
    inputs = tokenizer.encode(user_input, return_tensors="pt").to(device)
    
    # Gera uma resposta
    outputs = model.generate(
        inputs,
        max_length=50,
        num_return_sequences=1,
        num_beams=5,
        no_repeat_ngram_size=2,
        top_p=0.95,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response


@cl.on_message
async def main(message: cl.Message):
    """
    Esta função será chamada sempre que o usuário enviar uma mensagem pela interface do Chainlit.

    Args:
        message: Mensagem do usuário enviada pela interface Chainlit.

    Returns:
        None.
    """
    # Processar a mensagem do usuário com o modelo
    user_input = message.content
    await cl.Message(content="Gerando resposta...").send()

    # Chama a função de geração de resposta
    model_response = await generate_response(user_input)

    # Envia a resposta gerada para o usuário
    await cl.Message(content=model_response).send()
