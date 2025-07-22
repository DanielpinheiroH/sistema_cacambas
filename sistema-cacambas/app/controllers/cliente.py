from app.models.database import SessionLocal
from app.models.cliente import Cliente
import traceback

# ════════════════════════════════════════════════════════
# SALVAR NOVO CLIENTE
# ════════════════════════════════════════════════════════
def salvar_cliente(nome, cpf_cnpj, telefone, endereco, email):
    db = SessionLocal()
    try:
        cliente = Cliente(
            nome=nome,
            cpf_cnpj=cpf_cnpj,
            telefone=telefone,
            endereco=endereco,
            email=email
        )
        db.add(cliente)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print("Erro ao salvar cliente:", e)
        traceback.print_exc()
        return False
    finally:
        db.close()

# ════════════════════════════════════════════════════════
# LISTAR TODOS OS CLIENTES
# ════════════════════════════════════════════════════════
def listar_clientes():
    db = SessionLocal()
    try:
        return db.query(Cliente).all()
    finally:
        db.close()

# ════════════════════════════════════════════════════════
# ATUALIZAR CLIENTE POR ID
# ════════════════════════════════════════════════════════
def atualizar_cliente(id_cliente, nome=None, cpf_cnpj=None, telefone=None, endereco=None, email=None):
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter(Cliente.id == id_cliente).first()
        if not cliente:
            return False  # Cliente não encontrado

        # Atualiza somente os campos fornecidos
        if nome is not None:
            cliente.nome = nome
        if cpf_cnpj is not None:
            cliente.cpf_cnpj = cpf_cnpj
        if telefone is not None:
            cliente.telefone = telefone
        if endereco is not None:
            cliente.endereco = endereco
        if email is not None:
            cliente.email = email

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print("Erro ao atualizar cliente:", e)
        traceback.print_exc()
        return False
    finally:
        db.close()

# ════════════════════════════════════════════════════════
# DELETAR CLIENTE POR ID
# ════════════════════════════════════════════════════════
def deletar_cliente(id_cliente):
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter(Cliente.id == id_cliente).first()
        if not cliente:
            return False  # Cliente não encontrado
        db.delete(cliente)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print("Erro ao deletar cliente:", e)
        traceback.print_exc()
        return False
    finally:
        db.close()
