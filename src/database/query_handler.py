import os
from sqlalchemy import create_engine, text  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

# Configuração da conexão com o banco de dados
DB_URL = (
    f"postgresql://{os.environ.get('DATABASEUSER')}:{os.environ.get('DATABASEPSSW')}@"
    f"{os.environ.get('DATABASEHOST')}:{os.environ.get('DATABASEPORT')}/{os.environ.get('DATABASENAME')}"
)

# Criando o engine e a sessão do SQLAlchemy
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)


async def query_handler(query: str):
    """
    Executa a query SQL no banco de dados utilizando SQLAlchemy.

    Args:
        query (str): A query SQL a ser executada.

    Returns:
        O resultado da consulta no banco de dados.
    """
    session = Session()  # Inicia a sessão com o banco de dados

    try:
        # Executa a consulta
        result = session.execute(text(query))

        # Para uma consulta SELECT, recupera os resultados
        if query.strip().upper().startswith("SELECT"):
            result = result.fetchall()
        else:
            # Para outras consultas, faz o commit para persistir as alterações
            session.commit()
            result = f"{result.rowcount} linhas afetadas."

        return result

    except Exception as e:
        print(f"Erro ao executar a query: {e}")
        return "Não foi possível executar a consulta no banco de dados."

    finally:
        session.close()  # Fecha a sessão
