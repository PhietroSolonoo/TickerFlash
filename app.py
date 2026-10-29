import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import redis

app = Flask(__name__)

mongo_client = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
db = mongo_client["ticketflash"]

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True,
)

# Helper para validar e converter o ID do MongoDB
def converter_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        return None

@app.route("/health", methods=["GET"])
def health():
    try:
        mongo_ok = mongo_client.admin.command("ping")["ok"] == 1
    except Exception:
        mongo_ok = False
    try:
        redis_ok = redis_client.ping()
    except Exception:
        redis_ok = False
    status = "ok" if (mongo_ok and redis_ok) else "degradado"
    return jsonify({"status": status, "mongo": mongo_ok, "redis": redis_ok}), 200


# --- CRUD DE EVENTOS (Req 2) ---

@app.route("/eventos", methods=["POST"])
def criar_evento():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400
    
    # Garante que os setores novos começam com 0 vendidos
    if "setores" in dados:
        for setor in dados["setores"]:
            setor["vendidos"] = 0

    resultado = db.eventos.insert_one(dados)
    dados["_id"] = str(resultado.inserted_id)
    return jsonify(dados), 201


@app.route("/eventos", methods=["GET"])
def listar_eventos():
    categoria = request.args.get("categoria")
    cidade = request.args.get("cidade")
    
    query = {}
    if categoria:
        query["categoria"] = categoria
    if cidade:
        query["local.cidade"] = cidade  # Filtra pelo subdocumento

    eventos = list(db.eventos.find(query))
    for ev in eventos:
        ev["_id"] = str(ev["_id"])
    
    return jsonify(eventos), 200


@app.route("/eventos/<id>", methods=["GET"])
def buscar_evento(id):
    obj_id = converter_id(id)
    if not obj_id:
        return jsonify({"erro": "ID inválido"}), 404
        
    evento = db.eventos.find_one({"_id": obj_id})
    if not evento:
        return jsonify({"erro": "Evento não encontrado"}), 404
        
    evento["_id"] = str(evento["_id"])
    return jsonify(evento), 200


@app.route("/eventos/<id>", methods=["PUT"])
def atualizar_evento(id):
    obj_id = converter_id(id)
    if not obj_id:
        return jsonify({"erro": "ID inválido"}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    resultado = db.eventos.update_one({"_id": obj_id}, {"$set": dados})
    if resultado.matched_count == 0:
        return jsonify({"erro": "Evento não encontrado"}), 404

    return jsonify({"mensagem": "Evento atualizado"}), 200


@app.route("/eventos/<id>", methods=["DELETE"])
def deletar_evento(id):
    obj_id = converter_id(id)
    if not obj_id:
        return jsonify({"erro": "ID inválido"}), 404

    resultado = db.eventos.delete_one({"_id": obj_id})
    if resultado.deleted_count == 0:
        return jsonify({"erro": "Evento não encontrado"}), 404

    return jsonify({"mensagem": "Evento removido"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)