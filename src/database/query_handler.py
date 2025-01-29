import os
from sqlalchemy import create_engine, text  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from utils.log import log

DB_URL = (
    f"postgresql://{os.environ.get('DATABASEUSER')}:{os.environ.get('DATABASEPSSW')}@"
    f"{os.environ.get('DATABASEHOST')}:{os.environ.get('DATABASEPORT')}/{os.environ.get('DATABASENAME')}"
)

engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)

async def query_handler(query: str):
    session = Session()  
    try:
        result = session.execute(text(query))
        if query.strip().upper().startswith("SELECT"):
            result = result.fetchall()
        else:
            session.commit()
            result = f"{result.rowcount} linhas afetadas."
        return result
    except Exception as e:
        log("[query_handler]",f"Erro ao executar a query: {e}","error")
        return "Não foi possível executar a consulta no banco de dados."
    finally:
        session.close()  
