import psycopg2
import os

# Configuração da conexão com o banco de dados
DB_CONFIG = {
    'dbname': os.environ.get("DATABASENAME"),
    'user': os.environ.get("DATABASEUSER"),
    'password': os.environ.get("DATABASEPSSW"),
    'host': os.environ.get("DATABASEHOST"),
    'port': os.environ.get("DATABASEPORT")
}

async def query_handler(query: str):
    """
    Executa a query SQL no banco de dados.

    Args:
        query (str): A query SQL a ser executada.
    
    Returns:
        O resultado da consulta no banco de dados.
    """
    try:
        # Conectando ao banco de dados
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Executa a consulta
        cursor.execute(query)
        
        # Para uma consulta SELECT, recupera os resultados
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            # Para outras consultas, retorna a quantidade de linhas afetadas
            conn.commit()
            result = f"{cursor.rowcount} linhas afetadas."

        cursor.close()
        conn.close()

        return result

    except Exception as e:
        print(f"Erro ao executar a query: {e}")
        return "Não foi possível executar a consulta no banco de dados."
