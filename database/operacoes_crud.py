from datetime import datetime
from pathlib import Path
import os

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv(Path(__file__).resolve().parent / ".env")


class OperacoesCRUD:
    """Operações CRUD para erros e cadernos do banco caderno_erros.

    Os cadernos ficam embutidos nos documentos da coleção materias.
    Os erros ficam na coleção erros e são associados pelo e-mail do usuário
    e pelo nome da matéria.
    """

    CAMPOS_ERRO_EDITAVEIS = {
        "materia",
        "assunto",
        "tipo",
        "descricao",
        "dificuldade",
        "quantidadeErros",
        "tags",
        "status",
        "revisoes",
    }
    CAMPOS_CADERNO_EDITAVEIS = {"nome", "descricao"}

    def __init__(self, uri=None, nome_banco="caderno_erros"):
        uri = uri or os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI não encontrada no arquivo .env")

        self.cliente = MongoClient(uri, serverSelectionTimeoutMS=10000)
        self.cliente.admin.command("ping")
        self.banco = self.cliente[nome_banco]
        self.erros = self.banco["erros"]
        self.materias = self.banco["materias"]

    def fechar(self):
        self.cliente.close()

    @staticmethod
    def _id_objectid(id_documento):
        try:
            return ObjectId(id_documento)
        except Exception as erro:
            raise ValueError("O ID informado não é um ObjectId válido.") from erro

    @staticmethod
    def _validar_alteracoes(alteracoes, campos_permitidos):
        if not isinstance(alteracoes, dict) or not alteracoes:
            raise ValueError("Informe um dicionário com os campos a atualizar.")
        campos_invalidos = set(alteracoes) - campos_permitidos
        if campos_invalidos:
            raise ValueError(
                "Campos não permitidos: " + ", ".join(sorted(campos_invalidos))
            )

    # CRUD de erros
    def criar_erro(self, usuario_email, nome_materia, dados):
        if not self.materias.find_one(
            {"usuarioEmail": usuario_email, "nomeMateria": nome_materia}
        ):
            raise ValueError("Não encontrei essa matéria associada ao usuário.")
        if not isinstance(dados, dict) or not dados:
            raise ValueError("Informe os dados do erro em um dicionário.")

        documento = dict(dados)
        documento["usuarioEmail"] = usuario_email
        documento["materia"] = nome_materia
        documento.setdefault("dataCriacao", datetime.now())
        documento.setdefault("revisoes", [])
        resultado = self.erros.insert_one(documento)
        return str(resultado.inserted_id)

    def consultar_erros(self, usuario_email, nome_materia=None):
        filtro = {"usuarioEmail": usuario_email}
        if nome_materia:
            filtro["materia"] = nome_materia
        return list(self.erros.find(filtro).sort("dataCriacao", -1))

    def atualizar_erro(self, id_erro, usuario_email, alteracoes):
        self._validar_alteracoes(alteracoes, self.CAMPOS_ERRO_EDITAVEIS)
        resultado = self.erros.update_one(
            {"_id": self._id_objectid(id_erro), "usuarioEmail": usuario_email},
            {"$set": alteracoes},
        )
        return resultado.modified_count == 1

    def excluir_erro(self, id_erro, usuario_email):
        resultado = self.erros.delete_one(
            {"_id": self._id_objectid(id_erro), "usuarioEmail": usuario_email}
        )
        return resultado.deleted_count == 1

    # CRUD de cadernos embutidos em documentos da coleção materias
    def criar_caderno(self, usuario_email, nome_materia, nome, descricao=""):
        materia = self.materias.find_one(
            {"usuarioEmail": usuario_email, "nomeMateria": nome_materia}
        )
        if not materia:
            raise ValueError("Não encontrei essa matéria associada ao usuário.")
        if any(c.get("nome") == nome for c in materia.get("cadernos", [])):
            raise ValueError("Esse caderno já existe nessa matéria.")

        resultado = self.materias.update_one(
            {"_id": materia["_id"]},
            {
                "$push": {
                    "cadernos": {
                        "nome": nome,
                        "descricao": descricao,
                        "dataCriacao": datetime.now(),
                    }
                }
            },
        )
        return resultado.modified_count == 1

    def consultar_cadernos(self, usuario_email, nome_materia=None):
        filtro = {"usuarioEmail": usuario_email}
        if nome_materia:
            filtro["nomeMateria"] = nome_materia

        resultado = []
        for materia in self.materias.find(filtro).sort("nomeMateria", 1):
            resultado.append(
                {
                    "usuarioEmail": materia["usuarioEmail"],
                    "materia": materia["nomeMateria"],
                    "cadernos": materia.get("cadernos", []),
                }
            )
        return resultado

    def atualizar_caderno(
        self, usuario_email, nome_materia, nome_atual, alteracoes
    ):
        self._validar_alteracoes(alteracoes, self.CAMPOS_CADERNO_EDITAVEIS)
        materia = self.materias.find_one(
            {"usuarioEmail": usuario_email, "nomeMateria": nome_materia}
        )
        if not materia:
            return False

        cadernos = materia.get("cadernos", [])
        if not any(c.get("nome") == nome_atual for c in cadernos):
            return False

        novo_nome = alteracoes.get("nome", nome_atual)
        if novo_nome != nome_atual and any(
            c.get("nome") == novo_nome for c in cadernos
        ):
            raise ValueError("Já existe um caderno com esse nome nessa matéria.")

        campos_set = {f"cadernos.$[caderno].{campo}": valor
                      for campo, valor in alteracoes.items()}
        resultado = self.materias.update_one(
            {"_id": materia["_id"]},
            {"$set": campos_set},
            array_filters=[{"caderno.nome": nome_atual}],
        )
        return resultado.modified_count == 1

    def excluir_caderno(self, usuario_email, nome_materia, nome_caderno):
        resultado = self.materias.update_one(
            {
                "usuarioEmail": usuario_email,
                "nomeMateria": nome_materia,
                "cadernos.nome": nome_caderno,
            },
            {"$pull": {"cadernos": {"nome": nome_caderno}}},
        )
        return resultado.modified_count == 1


if __name__ == "__main__":
    print(
        "Módulo CRUD pronto. Importe OperacoesCRUD em outro arquivo para usar as funções."
    )
