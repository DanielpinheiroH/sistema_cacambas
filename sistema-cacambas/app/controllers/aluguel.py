from app.models.database import SessionLocal
from app.models.aluguel import Aluguel
from app.models.cacamba import Cacamba
from datetime import datetime

def registrar_aluguel(cliente_id, cacamba_id, data_entrega, dias_aluguel):
    db = SessionLocal()
    try:
        # Atualiza disponibilidade da caçamba
        cacamba = db.query(Cacamba).filter_by(id=cacamba_id).first()
        if not cacamba or not cacamba.disponivel:
            print("Caçamba indisponível.")
            return False

        cacamba.disponivel = False

        aluguel = Aluguel(
            cliente_id=cliente_id,
            cacamba_id=cacamba_id,
            data_entrega=data_entrega,
            dias_aluguel=dias_aluguel,
            ativo=True
        )
        db.add(aluguel)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print("Erro ao registrar aluguel:", e)
        return False
    finally:
        db.close()

def finalizar_aluguel(aluguel_id):
    db = SessionLocal()
    try:
        aluguel = db.query(Aluguel).filter_by(id=aluguel_id).first()
        if not aluguel or not aluguel.ativo:
            print("Aluguel já finalizado ou não encontrado.")
            return False

        aluguel.ativo = False

        # Liberar a caçamba
        cacamba = db.query(Cacamba).filter_by(id=aluguel.cacamba_id).first()
        if cacamba:
            cacamba.disponivel = True

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print("Erro ao finalizar aluguel:", e)
        return False
    finally:
        db.close()
