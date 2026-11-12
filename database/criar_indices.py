from pathlib import Path
import os

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient


load_dotenv(Path(__file__).resolve().parent / ".env")
uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI não encontrada no arquivo .env")

cliente = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    cliente.admin.command("ping")
    banco = cliente["caderno_erros"]

    # Um e-mail identifica cada usuário.
    idx_usuarios = banco["usuarios"].create_index(
        [("email", ASCENDING)],
        unique=True,
        name="email_1",
    )

    # Evita cadastrar a mesma matéria duas vezes para o mesmo usuário.
    idx_materias = banco["materias"].create_index(
        [("usuarioEmail", ASCENDING), ("nomeMateria", ASCENDING)],
        unique=True,
        name="usuario_materia_unicos",
    )

    # Apoia a consulta CRUD de erros por usuário/matéria ordenados por data.
    idx_erros = banco["erros"].create_index(
        [
            ("usuarioEmail", ASCENDING),
            ("materia", ASCENDING),
            ("dataCriacao", DESCENDING),
        ],
        name="erros_por_usuario_materia_data",
    )

    print("Índices criados ou já existentes:")
    print(f"usuarios: {idx_usuarios}")
    print(f"materias: {idx_materias}")
    print(f"erros: {idx_erros}")
finally:
    cliente.close()

