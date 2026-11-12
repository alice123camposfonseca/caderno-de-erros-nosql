from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from datetime import datetime


# =========================
# CONEXÃO COM O MONGODB
# =========================

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path)

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI não encontrada no database/.env")

cliente = MongoClient(MONGODB_URI)

banco = cliente["caderno_erros"]

erros = banco["erros"]


# =========================
# CRIAÇÃO DA API
# =========================

app = FastAPI(
    title="Caderno de Erros API",
    description="API do sistema Caderno de Erros",
    version="1.0.0"
)


# =========================
# CONFIGURAÇÃO DE CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# MODELO DE DADOS
# =========================

class Erro(BaseModel):
    usuarioEmail: str
    materia: str
    assunto: str
    tipo: str
    descricao: str
    dificuldade: int
    tags: list[str] = []

class Revisao(BaseModel):
    resultado: str
    observacao: str = ""


# =========================
# ROTA INICIAL
# =========================

@app.get("/")
def inicio():
    return {
        "mensagem": "API do Caderno de Erros funcionando!"
    }


# =========================
# CONSULTAR ERROS
# =========================

@app.get("/erros")
def consultar_erros():

    documentos = list(erros.find())

    for documento in documentos:
        documento["_id"] = str(documento["_id"])

    return documentos


# =========================
# CADASTRAR ERRO
# =========================

@app.post("/erros")
def cadastrar_erro(erro: Erro):

    novo_erro = erro.model_dump()

    novo_erro["quantidadeErros"] = 1
    novo_erro["status"] = "ativo"
    novo_erro["revisoes"] = []

    from datetime import datetime

    novo_erro["dataCriacao"] = datetime.now()

    resultado = erros.insert_one(novo_erro)

    return {
        "mensagem": "Erro cadastrado com sucesso!",
        "id": str(resultado.inserted_id)
    }

# =========================
# REGISTRAR REVISÃO
# =========================

@app.patch("/erros/{erro_id}/revisoes")
def registrar_revisao(erro_id: str, revisao: Revisao):

    if not ObjectId.is_valid(erro_id):
        raise HTTPException(
            status_code=400,
            detail="ID do erro inválido"
        )

    if revisao.resultado not in ["acertou", "errou"]:
        raise HTTPException(
            status_code=400,
            detail="Resultado deve ser acertou ou errou"
        )

    nova_revisao = {
        "data": datetime.now(),
        "resultado": revisao.resultado,
        "observacao": revisao.observacao
    }

    atualizacao = {
        "$push": {
            "revisoes": nova_revisao
        }
    }

    if revisao.resultado == "errou":
        atualizacao["$inc"] = {
            "quantidadeErros": 1
        }

    resultado = erros.update_one(
        {"_id": ObjectId(erro_id)},
        atualizacao
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Erro não encontrado"
        )

    return {
        "mensagem": "Revisão registrada com sucesso!"
    }
