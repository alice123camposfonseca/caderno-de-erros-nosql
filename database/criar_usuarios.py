
import os
from datetime import datetime
import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

# Carregar as variáveis do arquivo .env
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

# Obter a string de conexão do MongoDB Atlas
MONGODB_URI = os.getenv("MONGODB_URI")

# Conectar ao MongoDB
client = MongoClient(MONGODB_URI)

# Acessar o banco de dados
db = client["caderno_erros"]

# Acessar ou criar a coleção usuarios
usuarios = db["usuarios"]

# Criar usuários de exemplo
usuarios_exemplo = [
    {
        "nome": "Ana",
        "email": "ana@email.com",
        "senhaHash": bcrypt.hashpw(b"senha123", bcrypt.gensalt()).decode("utf-8"),
        "dataCadastro": datetime(2026, 11, 10),
        "status": "ativo"
    },
    {
        "nome": "Bruno",
        "email": "bruno@email.com",
        "senhaHash": bcrypt.hashpw(b"senha123", bcrypt.gensalt()).decode("utf-8"),
        "dataCadastro": datetime(2026, 11, 10),
        "status": "ativo"
    },
    {
        "nome": "Carla",
        "email": "carla@email.com",
        "senhaHash": bcrypt.hashpw(b"senha123", bcrypt.gensalt()).decode("utf-8"),
        "dataCadastro": datetime(2026, 11, 10),
        "status": "ativo"
    }
]

# Criar índice único para o email
usuarios.create_index("email", unique=True)

# Inserir os usuários de exemplo
for usuario in usuarios_exemplo:
    usuarios.update_one({"email": usuario["email"]}, {"$set": usuario}, upsert=True)

print(f"{len(usuarios_exemplo)} usuários criados ou atualizados!")

# Consultar e exibir os usuários
print("\nUsuários cadastrados:")

for usuario in usuarios.find():
    print(usuario)

# Encerrar a conexão
client.close()

print("\nProcesso finalizado!")
