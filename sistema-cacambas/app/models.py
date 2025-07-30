from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class UsuarioSistema(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome_empresa = Column(String, nullable=False)
    email = Column(String, unique=True)
    token_acesso = Column(String, unique=True, nullable=False)
    ativo = Column(Boolean, default=True)
    validade = Column(Date)
class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    cpf_cnpj = Column(String, unique=True)  # ✅ novo campo
    telefone = Column(String)
    endereco = Column(String)
    email = Column(String, unique=True)  # ✅ novo campo
    alugueis = relationship("Aluguel", back_populates="cliente")

class Cacamba(Base):
    __tablename__ = 'cacambas'
    id = Column(Integer, primary_key=True)
    identificacao = Column(String, unique=True)
    localizacao_atual = Column(String)
    disponivel = Column(Boolean, default=True)
    alugueis = relationship("Aluguel", back_populates="cacamba")

class Aluguel(Base):
    __tablename__ = 'aluguéis'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    cacamba_id = Column(Integer, ForeignKey('cacambas.id'))
    
    cliente = relationship("Cliente", back_populates="alugueis")  # ← ok
    cacamba = relationship("Cacamba", back_populates="alugueis")  # ← ok
    
    data_inicio = Column(DateTime, default=datetime.datetime.utcnow)
    data_fim = Column(DateTime)
    encerrado = Column(Boolean, default=False)
    valor = Column(Float)
    pago = Column(Boolean, default=False)
 # NOVO CAMPO:
    endereco_obra = Column(String, nullable=False)