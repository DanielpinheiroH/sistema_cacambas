from app.database import SessionLocal
from app.models import Cacamba

def registrar_cacamba(identificacao, localizacao=None):  # localizacao é opcional, mas ignorada
    session = SessionLocal()
    try:
        nova_cacamba = Cacamba(identificacao=identificacao)  # <- Removido localizacao
        session.add(nova_cacamba)
        session.commit()
        return True
    except Exception as e:
        print(f"Erro ao registrar caçamba: {e}")
        session.rollback()
        return False
    finally:
        session.close()
