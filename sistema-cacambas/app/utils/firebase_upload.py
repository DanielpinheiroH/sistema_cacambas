import firebase_admin
from firebase_admin import credentials, storage
import threading
import time
import socket
from datetime import datetime
import os
from app.utils.cliente_info import cliente
import unicodedata
import re


# Caminho para o banco principal (dados dos clientes)
CAMINHO_BANCO = os.path.join(os.path.dirname(__file__), '../..', 'sistema.db')
CAMINHO_BANCO = os.path.abspath(CAMINHO_BANCO)

# Caminho da credencial do Firebase
CAMINHO_CREDENCIAL = os.path.join(os.path.dirname(__file__), '..', 'firebase', 'firebase_config.json')
CAMINHO_CREDENCIAL = os.path.abspath(CAMINHO_CREDENCIAL)

# Inicializa o Firebase apenas uma vez
if not firebase_admin._apps:
    cred = credentials.Certificate(CAMINHO_CREDENCIAL)
    firebase_admin.initialize_app(cred, {
    "storageBucket": "sistema-cacambas-backup-ea2ac.firebasestorage.app"
})
    storage.bucket().name  # Verifica se o bucket foi inicializado corretamente
else:
    print("Firebase já inicializado, reutilizando a instância existente.")

def conexao_ativa():
    """Verifica se há conexão com a internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def slugify(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = re.sub(r'[^\w\s-]', '', texto).strip().lower()
    texto = re.sub(r'[-\s]+', '_', texto)
    return texto

def baixar_backup_do_cliente():
    if not cliente or "empresa" not in cliente:
        print("⚠️ Cliente não está logado. Não é possível baixar backup.")
        return

    nome_empresa = slugify(cliente["empresa"])
    nome_arquivo = f"backup_banco/{nome_empresa}_sistema.db"
    bucket = storage.bucket()
    blob = bucket.blob(nome_arquivo)

    if not blob.exists():
        print("⚠️ Nenhum backup encontrado para este cliente.")
        return

    try:
        blob.download_to_filename(CAMINHO_BANCO)
        print(f"✅ Backup restaurado para {CAMINHO_BANCO}")
    except Exception as e:
        print("❌ Erro ao baixar backup:", e)

def upload_automatico():
    print("📦 CLIENTE NO BACKUP:", cliente)

    if not conexao_ativa():
        print("⚠️ Sem conexão. Upload não realizado.")
        return

    if not cliente or "empresa" not in cliente:
        print("⚠️ Cliente ainda não fez login. Backup ignorado.")
        return  # ✅ AGORA ESTÁ DENTRO DO IF CORRETO

    nome_empresa = slugify(cliente["empresa"])
    nome_arquivo = f"backup_banco/{nome_empresa}_sistema.db" 

    bucket = storage.bucket()
    blob = bucket.blob(nome_arquivo)

    try:
        print("🚀 Iniciando upload para Firebase...")
        blob.upload_from_filename(CAMINHO_BANCO)
        print("✅ Backup enviado com sucesso:", blob.name)
    except Exception as e:
        print("❌ Erro ao fazer upload:", e)

    print("✅ DEBUG FINAL CLIENTE:", cliente)

def iniciar_agendamento(intervalo_em_minutos=30):
    """Inicia uma thread em segundo plano para fazer uploads em intervalos regulares."""
    def loop_upload():
        while True:
            time.sleep(intervalo_em_minutos * 60)
            upload_automatico()

    threading.Thread(target=loop_upload, daemon=True).start()
    print(f"🔄 Agendamento de upload iniciado a cada {intervalo_em_minutos} minutos.")