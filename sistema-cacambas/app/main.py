# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA DE CAÇAMBAS - TELA PRINCIPAL
# Desenvolvido com CustomTkinter + SQLAlchemy
# Código refatorado e estilizado com boas práticas profissionais
# ═══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from datetime import datetime, timedelta

from .database import init_db, SessionLocal
from .models import Cacamba, Aluguel

from .views.cliente_view import construir_tela_cliente
from .views.cacamba_view import construir_tela_cacamba
from .views.aluguel_view import construir_tela_aluguel, construir_tela_devolucao
from .views.locacao_view import construir_tela_locacao
from .views.historico_view import construir_tela_historico
from app.views.consulta_cliente_view import construir_tela_consulta_clientes


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO INICIAL E TELA
# ═══════════════════════════════════════════════════════════════════════════════

telas = {}  # Dicionário que armazena todas as views


def mostrar_tela(nome: str) -> None:
    """Eleva a tela desejada para o topo."""
    if nome in telas:
        telas[nome].tkraise()


def mostrar_dashboard(frame: ctk.CTkFrame) -> None:
    """Atualiza e exibe os dados do dashboard principal."""
    for widget in frame.winfo_children():
        widget.destroy()

    with SessionLocal() as db:
        total_disponiveis = db.query(Cacamba).filter_by(disponivel=True).count()
        total_alugadas = db.query(Cacamba).filter_by(disponivel=False).count()

        hoje = datetime.today()
        vencendo = db.query(Aluguel).filter(
            Aluguel.encerrado.is_(False),
            Aluguel.data_fim <= hoje + timedelta(days=2)
        ).count()

    # UI
    ctk.CTkLabel(frame, text="📊 Dashboard", font=("Segoe UI", 20, "bold")).pack(pady=10)
    ctk.CTkLabel(frame, text=f"🚛 Caçambas Alugadas: {total_alugadas}", font=("Segoe UI", 14)).pack(pady=5)
    ctk.CTkLabel(frame, text=f"✅ Caçambas Disponíveis: {total_disponiveis}", font=("Segoe UI", 14)).pack(pady=5)
    ctk.CTkLabel(
        frame,
        text=f"⚠️ Vencendo em até 2 dias: {vencendo}",
        font=("Segoe UI", 14),
        text_color="red"
    ).pack(pady=5)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """Ponto de entrada do sistema."""
    init_db()

    # Configuração visual
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Sistema de Caçambas - Menu Principal")
    root.geometry("440x650")

    # Container principal
    container = ctk.CTkFrame(root)
    container.pack(expand=True, fill="both")

    # Construção e registro das telas
    telas.update({
        "dashboard":           ctk.CTkFrame(container),
        "cliente":             construir_tela_cliente(container),
        "cacamba":             construir_tela_cacamba(container),
        "aluguel":             construir_tela_aluguel(container),
        "devolucao":           construir_tela_devolucao(container),
        "locacao":             construir_tela_locacao(container),
        "historico":           construir_tela_historico(container),
        "consulta_clientes":   construir_tela_consulta_clientes(container),
    })

    mostrar_dashboard(telas["dashboard"])

    for tela in telas.values():
        tela.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Frame de botões
    botoes_frame = ctk.CTkFrame(root, corner_radius=12)
    botoes_frame.pack(pady=10, padx=20, fill="x")

    botoes = [
        ("🔄 Atualizar Dashboard",    lambda: mostrar_dashboard(telas["dashboard"])),
        ("📊 Ir para Dashboard",      lambda: mostrar_tela("dashboard")),
        ("📝 Nova Locação",           lambda: mostrar_tela("locacao")),
        ("📋 Novo Cliente",           lambda: mostrar_tela("cliente")),
        ("🚛 Caçambas",               lambda: mostrar_tela("cacamba")),
        ("📆 Aluguéis",               lambda: mostrar_tela("aluguel")),
        ("↩️ Devoluções",             lambda: mostrar_tela("devolucao")),
        ("📄 Histórico",              lambda: mostrar_tela("historico")),
        ("📋 Clientes (Consulta)",    lambda: mostrar_tela("consulta_clientes")),
    ]

    for texto, comando in botoes:
        ctk.CTkButton(botoes_frame, text=texto, command=comando, width=250).pack(pady=5)

    # Exibir primeira tela
    mostrar_tela("dashboard")
    root.mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO DIRETA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
