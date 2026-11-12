from pathlib import Path
import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv(Path(__file__).resolve().parent / ".env")
uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI não encontrada no arquivo .env")


def consultar_cadernos_e_erros(colecao_materias, colecao_erros, email_usuario=None):
    """Retorna matérias, cadernos e erros do mesmo usuário e matéria."""
    filtro = {}
    if email_usuario:
        filtro["usuarioEmail"] = email_usuario

    resultado = []
    for materia in colecao_materias.find(filtro).sort(
        [("usuarioEmail", 1), ("nomeMateria", 1)]
    ):
        filtro_erros = {
            "usuarioEmail": materia["usuarioEmail"],
            "materia": materia["nomeMateria"],
        }
        erros_da_materia = list(colecao_erros.find(filtro_erros).sort("dataCriacao", -1))

        cadernos = []
        for caderno in materia.get("cadernos", []):
            cadernos.append(
                {
                    "nome": caderno.get("nome", "Caderno sem nome"),
                    "descricao": caderno.get("descricao", ""),
                    # No modelo atual, os erros se relacionam à matéria e ao usuário.
                    "erros": erros_da_materia,
                }
            )

        resultado.append(
            {
                "usuarioEmail": materia["usuarioEmail"],
                "materia": materia["nomeMateria"],
                "cadernos": cadernos,
            }
        )

    return resultado


def main():
    cliente = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        cliente.admin.command("ping")
        banco = cliente["caderno_erros"]
        dados = consultar_cadernos_e_erros(banco["materias"], banco["erros"])

        if not dados:
            print("Nenhuma matéria ou caderno encontrado.")
            return

        for item in dados:
            print(f"\nUsuário: {item['usuarioEmail']}")
            print(f"Matéria: {item['materia']}")

            if not item["cadernos"]:
                print("  Esta matéria ainda não possui cadernos.")
                continue

            for caderno in item["cadernos"]:
                print(f"  Caderno: {caderno['nome']}")
                if caderno["descricao"]:
                    print(f"    Descrição: {caderno['descricao']}")
                if not caderno["erros"]:
                    print("    Nenhum erro cadastrado para esta matéria.")
                    continue

                for erro in caderno["erros"]:
                    print(f"    - {erro.get('assunto', 'Erro sem assunto')}")
                    print(f"      Tipo: {erro.get('tipo', 'não informado')}")
                    print(f"      Descrição: {erro.get('descricao', 'sem descrição')}")

    finally:
        cliente.close()


if __name__ == "__main__":
    main()
