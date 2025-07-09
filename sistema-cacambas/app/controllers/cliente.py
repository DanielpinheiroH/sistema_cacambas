from app.models.database import SessionLocal
from app.models.cliente import Cliente

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
        return False
    finally:
        db.close()

def listar_clientes():
    db = SessionLocal()
    try:
        return db.query(Cliente).all()
    finally:
        db.close()