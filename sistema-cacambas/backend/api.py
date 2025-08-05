from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# 🔹 Inicializa Firebase a partir de arquivo local ou variável de ambiente
firebase_json = os.getenv("FIREBASE_CONFIG")

if not firebase_admin._apps:
    try:
        if firebase_json:
            # Modo produção (ex: Render.com)
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
        else:
            # Modo local (ex: teste na sua máquina)
            caminho_cred_local = os.path.join(
                os.path.dirname(__file__),
                "../app/firebase/firebase_config.json"
            )
            cred = credentials.Certificate(caminho_cred_local)

        firebase_admin.initialize_app(cred)
        db_firestore = firestore.client()
        print("✅ Firebase inicializado com sucesso!")
    except Exception as e:
        print("❌ Erro ao inicializar Firebase:", e)
        raise Exception("Erro ao inicializar Firebase.")

# 🔹 Inicializa FastAPI
app = FastAPI()

# 🔹 Middleware CORS para integração com o app desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Modelo para requisição de token
class TokenRequest(BaseModel):
    token: str

# 🔹 Rota para validar token via Firestore
@app.post("/validar_token")
def validar_token(data: TokenRequest):
    try:
        docs = db_firestore.collection("usuarios").where("token", "==", data.token).stream()
        usuario = None
        for doc in docs:
            usuario = doc.to_dict()
            break

        if not usuario:
            print("❌ Token não encontrado:", data.token)
            raise HTTPException(status_code=401, detail="Token inválido.")

        if not usuario.get("ativo", False):
            print(f"🔒 Usuário inativo: {usuario.get('empresa')}")
            raise HTTPException(status_code=403, detail="Usuário inativo.")

        validade = usuario.get("validade")
        if not validade:
            print(f"⚠️ Usuário sem validade: {usuario.get('empresa')}")
            raise HTTPException(status_code=403, detail="Licença não cadastrada.")

        hoje = date.today()
        if validade.date() < hoje:
            print(f"⛔ Licença expirada para {usuario.get('empresa')} em {validade}")
            raise HTTPException(status_code=403, detail="Licença expirada.")

        print(f"✅ Token validado com sucesso para {usuario.get('empresa')}")

        return {
            "empresa": usuario.get("empresa"),
            "email": usuario.get("email", ""),
            "telefone": usuario.get("telefone", ""),
            "token": usuario.get("token"),
            "validade": validade.isoformat()
        }

    except Exception as e:
        print("❌ Erro ao validar token:", e)
        raise HTTPException(status_code=500, detail="Erro interno na validação.")
