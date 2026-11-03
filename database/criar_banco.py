import os
from datetime import datetime

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI não encontrada no arquivo .env")


cliente = MongoClient(uri)

cliente.admin.command("ping")

print("Conexão com MongoDB realizada com sucesso!")
banco = cliente["caderno_erros"]

if "erros" not in banco.list_collection_names():
    banco.create_collection("erros")
    print("Coleção erros criada!")

colecao = banco["erros"]
exemplos = [

    # Documento 1
    {
        "codigoExemplo": True,
        "materia": "Banco de Dados NoSQL",
        "assunto": "MongoDB",
        "tipo": "conceito",
        "tags": ["MongoDB", "documentos", "colecoes"],
        "descricao": "Confundi documentos com coleções no MongoDB.",
        "dificuldade": 3,
        "quantidadeErros": 2,
        "status": "ativo",
        "dataCriacao": datetime(2026, 10, 20),
        "revisoes": [
            {
                "data": datetime(2026, 10, 22),
                "resultado": "errou",
                "observacao": "Ainda confundo os conceitos."
            },
            {
                "data": datetime(2026, 10, 25),
                "resultado": "acertou",
                "observacao": "Consegui compreender a diferença."
            }
        ]
    },

    # Documento 2
    {
        "codigoExemplo": True,
        "materia": "Programação Python",
        "assunto": "Estruturas de repetição",
        "tipo": "procedimento",
        "tags": ["Python", "while", "loops"],
        "descricao": "Esqueci de atualizar a variável de controle do while.",
        "dificuldade": 4,
        "quantidadeErros": 3,
        "status": "ativo",
        "dataCriacao": datetime(2026, 10, 21),
        "revisoes": [
            {
                "data": datetime(2026, 10, 23),
                "resultado": "errou",
                "observacao": "Esqueci novamente de atualizar a condição."
            }
        ]
    },

    # Documento 3
    {
        "codigoExemplo": True,
        "materia": "Estatística",
        "assunto": "Medidas de tendência central",
        "tipo": "calculo",
        "tags": ["Estatística", "media", "mediana"],
        "descricao": "Confundi o cálculo da média aritmética com o da mediana.",
        "dificuldade": 5,
        "quantidadeErros": 4,
        "status": "ativo",
        "dataCriacao": datetime(2026, 10, 22),
        "revisoes": [
            {
                "data": datetime(2026, 10, 24),
                "resultado": "errou",
                "observacao": "Ainda tenho dificuldade nos cálculos."
            },
            {
                "data": datetime(2026, 10, 27),
                "resultado": "errou",
                "observacao": "Preciso revisar o conteúdo."
            }
        ]
    },

    # Documento 4
    {
        "codigoExemplo": True,
        "materia": "Banco de Dados NoSQL",
        "assunto": "Documentos embutidos",
        "tipo": "interpretacao",
        "tags": ["MongoDB", "modelagem", "documentos"],
        "descricao": "Não identifiquei quando utilizar documentos embutidos.",
        "dificuldade": 2,
        "quantidadeErros": 1,
        "status": "superado",
        "dataCriacao": datetime(2026, 10, 24),
        "revisoes": [
            {
                "data": datetime(2026, 10, 26),
                "resultado": "acertou",
                "observacao": "Consegui compreender a modelagem."
            }
        ]
    },

    # Documento 5
    {
        "codigoExemplo": True,
        "materia": "Matemática",
        "assunto": "Equações do segundo grau",
        "tipo": "calculo",
        "tags": ["Matemática", "equacoes", "bhaskara"],
        "descricao": "Errei a aplicação da fórmula de Bhaskara.",
        "dificuldade": 4,
        "quantidadeErros": 2,
        "status": "ativo",
        "dataCriacao": datetime(2026, 10, 28),
        "revisoes": []
    }

]
colecao.delete_many({"codigoExemplo": True})

resultado = colecao.insert_many(exemplos)
print(f"{len(resultado.inserted_ids)} documentos inseridos com sucesso!")

print("\nDocumentos existentes na coleção:")

for documento in colecao.find():
    print(documento)

cliente.close()
print("\nProcesso finalizado!")
