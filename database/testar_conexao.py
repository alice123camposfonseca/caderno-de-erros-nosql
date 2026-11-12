import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Obtém a string de conexão
uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI não encontrada no arquivo .env")

# Conecta ao MongoDB Atlas
cliente = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    cliente.admin.command("ping")
    print("Conexão com MongoDB Atlas realizada com sucesso!")
except Exception as erro:
    print("Não foi possível conectar ao MongoDB:")
    print(erro)
finally:
    cliente.close()