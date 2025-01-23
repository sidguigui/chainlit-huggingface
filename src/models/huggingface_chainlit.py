import chainlit as cl  # type: ignore
import torch  # type: ignore
from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

# Inicializa o modelo fora da função para carregar apenas uma vez
model_name = "gpt2"
local_dir = "./models_cache/distilgpt2"

# Definindo o dispositivo (somente CPU, sem uso de GPU)
device = torch.device("cpu")  # Garantindo que o modelo será carregado na CPU

print("Carregando o modelo...")

# Carrega o tokenizador e o modelo
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=local_dir)
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=local_dir)

# Mover o modelo para o dispositivo (CPU)
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
    try:
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

        # Decodifica a resposta
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return "Ocorreu um erro ao gerar a resposta. Tente novamente mais tarde."


@cl.on_message
async def main(message: cl.Message):
    """
    Esta função será chamada sempre que o usuário enviar uma mensagem pela interface do Chainlit.

    Args:
        message: Mensagem do usuário enviada pela interface Chainlit.

    Returns:
        None.
    """
    try:
        # Processar a mensagem do usuário com o modelo
        user_input = message.content
        await cl.Message(content="Gerando resposta...").send()

        # Chama a função de geração de resposta
        model_response = await generate_response(user_input)

        # Envia a resposta gerada para o usuário
        await cl.Message(content=model_response).send()

    except Exception as e:
        print(f"Erro no processamento da mensagem: {e}")
        await cl.Message(
            content="Ocorreu um erro ao processar a mensagem. Tente novamente."
        ).send()
