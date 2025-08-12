# app/controllers/cacamba.py
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models import Cacamba


def registrar_cacamba(identificacao: str, localizacao_atual: str | None = None) -> bool:
    """
    Cadastra uma nova caçamba. Se o modelo tiver o campo `localizacao`, salva-o.
    Retorna True em caso de sucesso, False em caso de erro/duplicidade.
    """
    session = SessionLocal()
    try:
        # Verifica se já existe
        existente = session.query(Cacamba).filter(Cacamba.identificacao == identificacao).first()
        if existente:
            # Já existe -> mantemos o comportamento simples (não atualizar) e retornamos False
            return False

        nova = Cacamba(identificacao=identificacao)
        # Só seta localizacao se a coluna existir no modelo
        if hasattr(Cacamba, "localizacao") and localizacao_atual is not None:
            setattr(nova, "localizacao", localizacao_atual)

        session.add(nova)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    except Exception as e:
        session.rollback()
        print(f"Erro ao registrar caçamba: {e}")
        return False
    finally:
        session.close()


def buscar_cacamba_por_identificacao(ident: str) -> dict | None:
    """
    Busca a caçamba pela identificação.
    Retorna {"identificacao": ..., "localizacao": ...} se encontrar; caso contrário, None.
    Se o modelo não tiver `localizacao`, retorna com valor "" nesse campo.
    """
    session = SessionLocal()
    try:
        obj = session.query(Cacamba).filter(Cacamba.identificacao == ident).first()
        if not obj:
            return None

        registro = {
            "identificacao": getattr(obj, "identificacao", ""),
            "localizacao_atual": getattr(obj, "localizacao_atual", "") if hasattr(obj, "localizacao_atual") else ""
        }
        return registro
    except Exception as e:
        print(f"Erro ao buscar caçamba: {e}")
        return None
    finally:
        session.close()


def excluir_cacamba(ident: str) -> bool:
    """
    Exclui a caçamba pela identificação.
    Retorna True se excluiu; False se não encontrou ou em caso de erro.
    """
    session = SessionLocal()
    try:
        obj = session.query(Cacamba).filter(Cacamba.identificacao == ident).first()
        if not obj:
            return False

        session.delete(obj)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao excluir caçamba: {e}")
        return False
    finally:
        session.close()
