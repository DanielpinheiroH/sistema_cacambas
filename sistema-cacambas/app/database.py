import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Caminho absoluto para a pasta raiz do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "sistema.db")  # <-- banco na raiz do projeto

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()

def init_db():
    from .models import Cliente, Cacamba, Aluguel
    Base.metadata.create_all(engine)