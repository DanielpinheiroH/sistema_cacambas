from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base
import datetime

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
    data_inicio = Column(DateTime, default=datetime.datetime.utcnow)
    data_fim = Column(DateTime)
    encerrado = Column(Boolean, default=False) 
    
    valor = Column(Float)  

    cliente = relationship("Cliente", back_populates="alugueis")
    cacamba = relationship("Cacamba", back_populates="alugueis")