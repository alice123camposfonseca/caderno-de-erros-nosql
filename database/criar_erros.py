from datetime import datetime
from pathlib import Path
import os

from dotenv import load_dotenv
from pymongo import MongoClient


# Carrega o .env que fica na mesma pasta deste script.
load_dotenv(Path(__file__).resolve().parent / ".env")
uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI não encontrada no arquivo .env")

cliente = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    cliente.admin.command("ping")
    banco = cliente["caderno_erros"]
    erros = banco["erros"]

    # Exemplos associados ao usuário Ana criado em criar_usuarios.py.
    exemplos = [
        {
            "codigoExemplo": True,
            "usuarioEmail": "ana@email.com",
            "materia": "Banco de Dados NoSQL",
            "assunto": "Diferença entre documentos e coleções",
            "tipo": "conceito",
            "descricao": "Confundi um documento com uma coleção no MongoDB.",
            "dificuldade": 3,
            "quantidadeErros": 1,
            "tags": ["MongoDB", "documentos", "coleções"],
            "status": "ativo",
            "dataCriacao": datetime.now(),
            "revisoes": [],
        },
        {
            "codigoExemplo": True,
            "usuarioEmail": "ana@email.com",
            "materia": "Programação Python",
            "assunto": "Laço while",
            "tipo": "procedimento",
            "descricao": "Esqueci de atualizar a variável de controle do while.",
            "dificuldade": 4,
            "quantidadeErros": 2,
            "tags": ["Python", "while", "repetição"],
            "status": "ativo",
            "dataCriacao": datetime.now(),
            "revisoes": [],
        },
        {
            "codigoExemplo": True,
            "usuarioEmail": "ana@email.com",
            "materia": "Banco de Dados NoSQL",
            "assunto": "Inserção de documentos com PyMongo",
            "tipo": "procedimento",
            "descricao": "Tentei inserir novamente um e-mail que já tinha índice único.",
            "dificuldade": 2,
            "quantidadeErros": 1,
            "tags": ["PyMongo", "insert_many", "índice único"],
            "status": "ativo",
            "dataCriacao": datetime.now(),
            "revisoes": [],
        },
    ]

    inseridos = 0
    ja_existiam = 0

    for exemplo in exemplos:
        filtro = {
            "codigoExemplo": True,
            "usuarioEmail": exemplo["usuarioEmail"],
            "assunto": exemplo["assunto"],
        }
        resultado = erros.update_one(filtro, {"$setOnInsert": exemplo}, upsert=True)
        if resultado.upserted_id is not None:
            inseridos += 1
        else:
            ja_existiam += 1

    print("Conexão com MongoDB realizada com sucesso!")
    print(f"{inseridos} exemplo(s) inserido(s); {ja_existiam} já existia(m).")
    print("Coleção: caderno_erros.erros")

finally:
    cliente.close()
