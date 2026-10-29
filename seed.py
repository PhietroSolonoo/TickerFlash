import os
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

# Conexão
mongo_client = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
db = mongo_client["ticketflash"]

# Limpa os dados antigos (delete_many para não apagar os índices)
db.eventos.delete_many({})
db.usuarios.delete_many({})
db.pedidos.delete_many({})

# Semente para os dados serem sempre iguais
random.seed(42)

cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre"]

# 1. USUÁRIOS (20)
usuarios = []
for i in range(20):
    usuarios.append({
        "_id": ObjectId(f"{i + 1:024x}"),
        "nome": f"Usuario {i + 1}",
        "email": f"usuario{i + 1}@email.com",
        "cidade": random.choice(cidades),
        "dataCadastro": datetime.now() - timedelta(days=random.randint(1, 365))
    })
db.usuarios.insert_many(usuarios)

# 2. EVENTOS (10)
categorias = ["Show", "Teatro", "Stand-up", "Festival", "Esporte"]
eventos = []
for i in range(10):
    setores = [
        {"nome": "Pista", "preco": 100.0, "capacidade": 500, "vendidos": 0},
        {"nome": "Camarote", "preco": 250.0, "capacidade": 100, "vendidos": 0}
    ]
    eventos.append({
        "_id": ObjectId(f"{i + 1:024x}"),
        "nome": f"Evento {i + 1}",
        "categoria": random.choice(categorias),
        "data": datetime.now() + timedelta(days=random.randint(10, 100)),
        "local": {"cidade": random.choice(cidades), "endereco": f"Rua {i + 1}, 100"},
        "atracoes": [f"Atracao A{i}", f"Atracao B{i}"],
        "setores": setores
    })
db.eventos.insert_many(eventos)

# 3. PEDIDOS (50)
status_opcoes = ["confirmado", "pendente", "cancelado"]
pedidos = []
for i in range(50):
    ev = eventos[random.randint(0, 9)]
    setor = random.choice(ev["setores"])
    qtd = random.randint(1, 4)
    status = random.choice(status_opcoes)
    
    pedidos.append({
        "_id": ObjectId(f"{i + 1:024x}"),
        "usuarioId": usuarios[random.randint(0, 19)]["_id"],
        "eventoId": ev["_id"],
        "setor": setor["nome"],
        "quantidade": qtd,
        "valorTotal": setor["preco"] * qtd,
        "status": status,
        "criadoEm": datetime.now() - timedelta(days=random.randint(0, 30))
    })

    # Se o pedido for confirmado, já atualiza o campo 'vendidos' no evento
    if status == "confirmado":
        db.eventos.update_one(
            {"_id": ev["_id"], "setores.nome": setor["nome"]},
            {"$inc": {"setores.$.vendidos": qtd}}
        )

db.pedidos.insert_many(pedidos)

print("Seed concluído: 10 eventos, 20 usuários e 50 pedidos inseridos!")