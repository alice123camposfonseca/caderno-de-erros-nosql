import os
from pymongo import MongoClient
from dotenv import load_dotenv

# CONEXÃO COM O MONGODB

load_dotenv()

uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI não encontrada no arquivo .env")

cliente = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    cliente.admin.command("ping")
    print("Conexão com MongoDB Atlas realizada com sucesso!")

    db = cliente["caderno_erros"]
    collection = db["erros"]
  
    # AGREGAÇÃO 1: ERROS POR USUÁRIO E MATÉRIA

    pipeline_usuarios = [
        {
            "$match": {
                "usuarioEmail": {
                    "$exists": True
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "usuario": "$usuarioEmail",
                    "materia": "$materia"
                },
                "totalErros": {
                    "$sum": 1
                },
                "dificuldadeMedia": {
                    "$avg": "$dificuldade"
                }
            }
        },
        {
            "$sort": {
                "totalErros": -1
            }
        }
    ]

    resultado_usuarios = collection.aggregate(pipeline_usuarios)

    print("\n===== AGREGAÇÃO 1: ERROS POR USUÁRIO E MATÉRIA =====")

    for documento in resultado_usuarios:
        print(documento)

    
    # AGREGAÇÃO 2: TAXA DE ACERTO POR MATÉRIA
   

    pipeline_taxa_acerto = [
        {
            "$match": {
                "revisoes.0": {
                    "$exists": True
                }
            }
        },
        {
            "$unwind": "$revisoes"
        },
        {
            "$group": {
                "_id": "$materia",
                "totalRevisoes": {
                    "$sum": 1
                },
                "acertos": {
                    "$sum": {
                        "$cond": [
                            {
                                "$eq": [
                                    "$revisoes.resultado", "acertou"
                                ]
                            },
                            1,
                            0
                        ]
                    }
                },
                "erros": {
                    "$sum": {
                        "$cond": [
                            {
                                "$eq": [
                                    "$revisoes.resultado", "errou"
                                ]
                            },
                            1,
                            0
                        ]
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "materia": "$_id",
                "totalRevisoes": 1,
                "acertos": 1,
                "erros": 1,
                "taxaAcertoPercentual": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        "$acertos", "$totalRevisoes"
                                    ]
                                },
                                100
                            ]
                        },
                        1
                    ]
                }
            }
        },
        {
            "$sort": {
                "taxaAcertoPercentual": 1
            }
        }
    ]

    resultado_taxa = collection.aggregate(pipeline_taxa_acerto)

    print("\n===== AGREGAÇÃO 2: TAXA DE ACERTO POR MATÉRIA =====")

    for documento in resultado_taxa:
        print(documento)

except Exception as erro:
    print("\nErro ao executar as agregações:")
    print(erro)

finally:
    cliente.close()
    print("\nConexão com MongoDB encerrada.")