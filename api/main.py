from pathlib import Path
import os
import secrets
from contextlib import asynccontextmanager

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from datetime import datetime
from api.redis_service import RedisService


# =========================
# CONEXÃO COM O MONGODB
# =========================

project_root = Path(__file__).resolve().parent.parent
root_env_path = project_root / ".env"
database_env_path = project_root / "database" / ".env"
env_path = root_env_path if root_env_path.exists() else database_env_path

load_dotenv(env_path)

MONGODB_URI = os.getenv("MONGODB_URI")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))

if not MONGODB_URI:
    raise ValueError("MONGODB_URI não encontrada no database/.env")

cliente = MongoClient(MONGODB_URI)

banco = cliente["caderno_erros"]

erros = banco["erros"]
usuarios = banco["usuarios"]
redis_service = RedisService(REDIS_URL)
bearer_scheme = HTTPBearer()


# =========================
# CRIAÇÃO DA API
# =========================

@asynccontextmanager
async def lifespan(_: FastAPI):
    # O filtro recebe todos os e-mails reais antes de ser usado para rejeitar
    # logins. Assim, uma resposta negativa do Bloom Filter é confiável aqui.
    redis_service.ping()
    redis_service.prepare_structures()
    for user in usuarios.find({}, {"email": 1}):
        if user.get("email"):
            redis_service.remember_email(user["email"].lower())
    yield
    redis_service.close()


app = FastAPI(
    title="Caderno de Erros API",
    description="API do sistema Caderno de Erros",
    version="2.0.0",
    lifespan=lifespan,
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


class Credenciais(BaseModel):
    email: str
    senha: str


def sessao_atual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    session = redis_service.get_session(credentials.credentials)
    if not session:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")
    return session


# =========================
# ROTA INICIAL
# =========================

@app.get("/")
def inicio():
    return {
        "mensagem": "API do Caderno de Erros funcionando!"
    }


# =========================
# LOGIN COM CACHE REDIS
# =========================

@app.post("/auth/login")
def login(credenciais: Credenciais):
    email = credenciais.email.strip().lower()

    # Bloom Filter: se não está no filtro, certamente não está entre os
    # usuários carregados do MongoDB. Se está, pode haver falso positivo.
    if not redis_service.email_is_known(email):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    user = redis_service.get_cached_user(email)
    if user is None:
        document = usuarios.find_one({"email": email})
        if not document:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        user = {
            "_id": str(document["_id"]),
            "nome": document["nome"],
            "email": document["email"],
            "senhaHash": document.get("senhaHash", ""),
        }
        redis_service.cache_user(user)

    password_hash = user.get("senhaHash", "").encode("utf-8")
    if not password_hash or not bcrypt.checkpw(credenciais.senha.encode("utf-8"), password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = secrets.token_urlsafe(32)
    redis_service.create_session(token, user, SESSION_TTL_SECONDS)
    redis_service.track_login(user["_id"])
    redis_service.track_event("login")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": SESSION_TTL_SECONDS,
    }


@app.get("/auth/me")
def perfil(session: dict = Depends(sessao_atual)):
    """Consulta o usuário a partir da sessão cacheada e renova seu TTL."""
    return session


@app.post("/auth/logout", status_code=204)
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    redis_service.delete_session(credentials.credentials)


# =========================
# MÉTRICAS PROBABILÍSTICAS
# =========================

@app.get("/stats/usage")
def estatisticas_uso():
    """Métricas aproximadas: HyperLogLog e Count-Min Sketch."""
    login_estimates = []
    for user in usuarios.find({}, {"nome": 1, "email": 1}):
        login_estimates.append({
            "nome": user.get("nome"),
            "email": user.get("email"),
            "estimativa_logins": redis_service.login_frequency(str(user["_id"])),
        })

    return {
        "data": datetime.now().date().isoformat(),
        "usuarios_unicos_estimados": redis_service.unique_users_today(),
        "logins_estimados_por_usuario": login_estimates,
        "eventos_estimados": {
            "logins": redis_service.event_frequency("login"),
            "erros_cadastrados": redis_service.event_frequency("erro_cadastrado"),
            "revisoes_registradas": redis_service.event_frequency("revisao_registrada"),
        },
        "observacao": "HyperLogLog e Count-Min Sketch fornecem estimativas probabilísticas.",
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
    redis_service.track_event("erro_cadastrado")

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

    redis_service.track_event("revisao_registrada")

    return {
        "mensagem": "Revisão registrada com sucesso!"
    }
