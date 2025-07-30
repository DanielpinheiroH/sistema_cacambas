from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import requests
import sys
import os

# Adiciona o caminho da pasta Controle_sistema_cacambas ao sys.path
CAMINHO_USUARIOS = os.path.join(os.path.expanduser("~"), "Desktop", "Controle_sistema_cacambas")
if CAMINHO_USUARIOS not in sys.path:
    sys.path.append(CAMINHO_USUARIOS)

from usuarios_database import UsuarioSessionLocal
from usuarios_models import UsuarioSistema  # Usaremos apenas este modelo

# Caminho para o banco de dados dos usuários
CAMINHO_BANCO = os.path.join(CAMINHO_USUARIOS, "usuarios.db")

# 🔹 Inicializa a aplicação
app = FastAPI()

# 🔹 Middleware CORS para permitir integração com o app desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔹 Modelo da requisição de token
class TokenRequest(BaseModel):
    token: str

# 🔹 Rota para validar o token
@app.post("/validar_token")
def validar_token(data: TokenRequest):
    with UsuarioSessionLocal() as db:
        usuario = db.query(UsuarioSistema).filter(
            UsuarioSistema.token == data.token
        ).first()

    if not usuario:
        print("❌ Token não encontrado:", data.token)
        raise HTTPException(status_code=401, detail="Token inválido.")

    if not usuario.ativo:
        print(f"🔒 Usuário inativo: {usuario.empresa}")
        raise HTTPException(status_code=403, detail="Acesso bloqueado.")

    validade = usuario.validade
    hoje = date.today()

    if not validade:
        print(f"⚠️ Usuário sem validade definida: {usuario.empresa}")
        raise HTTPException(status_code=403, detail="Licença expirada ou não cadastrada.")

    if validade < hoje:
        print(f"⛔ Licença expirada em {validade} para {usuario.empresa}")
        raise HTTPException(status_code=403, detail="Licença expirada.")

    print(f"✅ Token validado para {usuario.empresa}")
    return {
        "id": usuario.id,
        "empresa": usuario.empresa,
        "token": usuario.token,
        "validade": validade
    }

print("🔥 Servidor rodando nessa porra com banco em:", CAMINHO_BANCO)
