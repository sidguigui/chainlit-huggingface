import pandas as pd  # type: ignore
import os
from sqlalchemy import create_engine  # type: ignore

def csv_to_postgres(csv_path, table_name, postgres_uri):
    """
    Lê um arquivo CSV e insere os dados no PostgreSQL.

    Args:
        csv_path (str): Caminho do arquivo CSV.
        table_name (str): Nome da tabela no PostgreSQL.
        postgres_uri (str): URI de conexão com o PostgreSQL (exemplo: postgresql://user:password@host:port/database).
    """
    try:
        # Lê o arquivo CSV em um DataFrame
        print(f"Lendo o arquivo CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()

        # Mostra uma prévia dos dados
        print("Prévia do DataFrame:")
        print(df.head())

        # Cria uma conexão com o banco de dados PostgreSQL
        print(f"Conectando ao banco de dados PostgreSQL: {postgres_uri}")
        engine = create_engine(postgres_uri)

        # Insere o DataFrame no banco de dados
        print(f"Inserindo os dados na tabela '{table_name}'...")
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Dados inseridos com sucesso na tabela '{table_name}'!")

    except Exception as e:
        print(f"Erro ao processar o arquivo CSV: {e}")

# Configurações
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'sales_data_sample.csv')
table_name = "orders"  # Substitua pelo nome da tabela no PostgreSQL

# Pega as variáveis de ambiente para a conexão
DB_URL = (
    f"postgresql://{os.environ.get('DATABASEUSER')}:{os.environ.get('DATABASEPSSW')}@"
    f"{os.environ.get('DATABASEHOST')}:{os.environ.get('DATABASEPORT')}/{os.environ.get('DATABASENAME')}"
)

# Chama a função
csv_to_postgres(csv_path, table_name, DB_URL)