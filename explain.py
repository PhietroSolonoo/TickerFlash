import os
import json
from datetime import datetime
from pymongo import MongoClient

mongo_client = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
db = mongo_client["ticketflash"]

# Consulta que usa o índice composto (categoria + data)
query = {"categoria": "Show", "data": {"$gte": datetime.now()}}

# Roda o explain
explicacao = db.eventos.find(query).explain()

# Pega o plano vencedor
winning_plan = explicacao["queryPlanner"]["winningPlan"]

# Imprime de forma bonita
print("--- WINNING PLAN ---")
print(json.dumps(winning_plan, indent=4, default=str))