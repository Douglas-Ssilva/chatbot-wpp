# Biblioteca padrão do Python para acessar variáveis de ambiente
import os

# Biblioteca para carregar variáveis do arquivo .env
from dotenv import load_dotenv


# Importações do SQLAlchemy (ORM para trabalhar com banco de dados)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# Busca a variável DATABASE_URL do .env
database_url = os.getenv('DATABASE_URL')

# Cria a conexão com o banco de dados usando a URL
engine = create_engine(database_url, 
                       echo=False, #echo exibição de query no console
                       pool_size=10, #apenas 10 connections abertas simultaneamente
                       max_overflow=20, #quantidade de pessoas em espera na nossa fila p usar o banco
                       pool_timeout=120, #query mto demorada
                       pool_recycle=1800) #pool aberta mto tempo, vai demorar esse tempo p ser reciclada p proximo uso

# Cria a fábrica de sessões para acessar o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(): 
    return SessionLocal()