import chainlit as cl  # type: ignore
import torch  # type: ignore
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # type: ignore
import traceback

# Modelo e tokenizador
model_name = "google/flan-t5-small"  # Um modelo leve, mas bom para tarefas de NLP
local_dir = "./models_cache/flan-t5-small"

# Configuração do dispositivo
device = torch.device("cpu")

print("Carregando o modelo...")

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=local_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=local_dir)
    model = model.to(device)  # Mover o modelo para CPU
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    raise


@cl.on_message
async def main(message: cl.Message):
    """
    Callback que processa a mensagem do usuário e gera uma query SQL.
    """
    try:
        user_input = message.content

        # Construir o prompt para o modelo
        prompt = f"""
        Você é um assistente especializado em SQL. Sua tarefa é criar queries SQL válidas e corretas com base na descrição fornecida pelo usuário.

        Descrição do usuário: {user_input}

        Exemplo 1:
        Descrição: Liste todos os usuários na tabela "users".
        Query SQL: SELECT * FROM users;

        Exemplo 2:
        Descrição: Conte quantas linhas existem na tabela "orders".
        Query SQL: SELECT COUNT(*) FROM orders;

        Agora, com base na descrição do usuário, gere a query SQL correspondente:
        """

        # Tokenizar a entrada
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        # Gerar a resposta do modelo
        outputs = model.generate(
            inputs.input_ids,
            max_length=150,
            num_beams=5,
            no_repeat_ngram_size=2,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )

        # Decodificar a resposta gerada
        query = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        # Enviar a query gerada para o usuário
        await cl.Message(content=f"Query gerada:\n\n```sql\n{query}\n```").send()

    except Exception as e:
        print(f"Erro: {e}")
        await cl.Message(
            content="Desculpe, ocorreu um erro ao processar sua solicitação."
        ).send()


@cl.step(type="tool")
async def generate_query(user_input: str, db_schema: str = ""):
    """
    Gera uma query SQL com base na entrada do usuário e no esquema do banco.

    Args:
        user_input: Descrição em linguagem natural do que a query deve fazer.
        db_schema: Estrutura básica do banco de dados (opcional).

    Returns:
        Uma query SQL gerada.
    """
    try:
        # Construa o prompt para o modelo
        prompt = f"""
Você é um assistente especializado em SQL. Baseado na descrição abaixo e no esquema do banco de dados, crie uma query SQL válida. Certifique-se de que a query esteja correta e inclua apenas a SQL final.

Descrição do usuário: {user_input}

Esquema do banco de dados:
{db_schema}

Query SQL:
"""
        # Tokenize a entrada
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(device)

        # Gera a query
        outputs = model.generate(
            inputs.input_ids,
            max_length=150,  # Garantir espaço para queries mais longas
            num_beams=5,  # Melhor precisão na saída
            no_repeat_ngram_size=2,
            temperature=0.2,  # Respostas mais objetivas
            pad_token_id=tokenizer.eos_token_id,
        )

        # Decodifica a query gerada
        query = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        # Valida a query gerada (verifica se é plausível)
        if "SELECT" not in query.upper():
            raise ValueError("Query gerada não parece válida.")

        return query

    except Exception:
        print(f"Erro ao gerar a query SQL: {traceback.format_exc()}")
        return "Não foi possível gerar uma query SQL válida. Verifique os dados fornecidos ou tente novamente."
