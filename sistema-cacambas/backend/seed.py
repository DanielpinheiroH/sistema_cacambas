from datetime import date
from app.models import UsuarioSistema
from app.database import SessionLocal

# Lista de clientes para inserir
clientes = [
    {
        "nome_empresa": "EcoCaçambas",
        "email": "contato@ecocacambas.com.br",
        "token_acesso": "ECO123",
        "ativo": True,
        "validade_licenca": date(2025, 12, 31)
    },
    {
        "nome_empresa": "Caçambas Rápidas",
        "email": "suporte@cacambasrapidas.com",
        "token_acesso": "RAP456",
        "ativo": True,
        "validade_licenca": date(2025, 11, 30)
    },
    {
        "nome_empresa": "MasterCaçamba",
        "email": "admin@mastercacamba.com",
        "token_acesso": "MST789",
        "ativo": True,
        "validade_licenca": date(2025, 10, 15)
    },
    {
        "nome_empresa": "Brasília Caçambas",
        "email": "bras@cacambas.com",
        "token_acesso": "DF001",
        "ativo": True,
        "validade_licenca": date(2026, 1, 31)
    },
    {
        "nome_empresa": "SuperLimpeza",
        "email": "limpeza@super.com",
        "token_acesso": "SUP555",
        "ativo": True,
        "validade_licenca": date(2025, 9, 1)
    },
]

# Executa o cadastro no banco
def popular_usuarios():
    with SessionLocal() as db:
        for cliente in clientes:
            existe = db.query(UsuarioSistema).filter_by(token_acesso=cliente["token_acesso"]).first()
            if not existe:
                novo = UsuarioSistema(**cliente)
                db.add(novo)
        db.commit()
    print("🌱 Seed executado com sucesso!")

if __name__ == "__main__":
    popular_usuarios()