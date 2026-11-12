from datetime import datetime
from pathlib import Path
import os

from dotenv import load_dotenv
from pymongo import MongoClient


# Carrega o .env que fica ao lado deste arquivo.
load_dotenv(Path(__file__).resolve().parent / ".env")
uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI não encontrada no arquivo .env")

cliente = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    cliente.admin.command("ping")
    banco = cliente["caderno_erros"]

    if "materias" not in banco.list_collection_names():
        banco.create_collection("materias")

    materias = banco["materias"]
    usuarios = banco["usuarios"]
    agora = datetime.now()

    exemplos = [
        {
            "codigoExemplo": True,
            "usuarioEmail": "ana@email.com",
            "nomeMateria": "Banco de Dados NoSQL",
            "dataCriacao": agora,
            "status": "ativa",
            "cadernos": [
                {
                    "nome": "Caderno de MongoDB",
                    "descricao": "Anotações e exercícios sobre MongoDB e PyMongo.",
                    "dataCriacao": agora,
                }
            ],
        },
        {
            "codigoExemplo": True,
            "usuarioEmail": "bruno@email.com",
            "nomeMateria": "Programação Python",
            "dataCriacao": agora,
            "status": "ativa",
            "cadernos": [
                {
                    "nome": "Caderno de Python",
                    "descricao": "Anotações e exercícios de programação Python.",
                    "dataCriacao": agora,
                }
            ],
        },
        {
            "codigoExemplo": True,
            "usuarioEmail": "carla@email.com",
            "nomeMateria": "Estatística",
            "dataCriacao": agora,
            "status": "ativa",
            "cadernos": [
                {
                    "nome": "Caderno de Estatística",
                    "descricao": "Anotações e exercícios de estatística.",
                    "dataCriacao": agora,
                }
            ],
        },
    ]

    emails = [exemplo["usuarioEmail"] for exemplo in exemplos]
    emails_encontrados = set(usuarios.distinct("email", {"email": {"$in": emails}}))
    emails_ausentes = set(emails) - emails_encontrados

    if emails_ausentes:
        raise ValueError(
            "Cadastre primeiro estes usuários na coleção usuarios: "
            + ", ".join(sorted(emails_ausentes))
        )

    inseridas = 0
    ja_existiam = 0

    for exemplo in exemplos:
        filtro = {
            "codigoExemplo": True,
            "usuarioEmail": exemplo["usuarioEmail"],
            "nomeMateria": exemplo["nomeMateria"],
        }
        resultado = materias.update_one(
            filtro,
            {"$setOnInsert": exemplo},
            upsert=True,
        )
        if resultado.upserted_id is not None:
            inseridas += 1
        else:
            ja_existiam += 1

    print("Conexão com MongoDB realizada com sucesso!")
    print(f"Coleção: caderno_erros.materias")
    print(f"{inseridas} matéria(s) inserida(s); {ja_existiam} já existia(m).")

finally:
    cliente.close()
