from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.models import UsuarioSistema
from app.database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware CORS para integração com o app desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criação das tabelas
Base.metadata.create_all(bind=engine)

# Modelo da requisição de token
class TokenRequest(BaseModel):
    token: str

# Rota para validar o token
@app.post("/validar_token")
def validar_token(data: TokenRequest):
    with SessionLocal() as db:
        usuario = db.query(UsuarioSistema).filter(
            UsuarioSistema.token_acesso == data.token
        ).first()

    if usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido.")

    if usuario.ativo is False:
        raise HTTPException(status_code=403, detail="Acesso bloqueado.")

    # ✅ Solução definitiva com getattr
    validade = getattr(usuario, "validade_licenca", None)

    if isinstance(validade, date) and validade < date.today():
        raise HTTPException(status_code=403, detail="Licença expirada.")

    return {
        "id": usuario.id,
        "empresa": usuario.nome_empresa,
        "token": usuario.token_acesso
    }

print("rodou essa porra!")