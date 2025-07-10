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


from sqlalchemy.orm import joinedload  # assegure que isso esteja no topo



def mostrar_dashboard(frame: ctk.CTkFrame) -> None:
    frame.configure(fg_color="#F9FAFB")
    for widget in frame.winfo_children():
        widget.destroy()

    with SessionLocal() as db:
        total_disponiveis = db.query(Cacamba).filter_by(disponivel=True).count()
    total_alugadas = db.query(Cacamba).filter_by(disponivel=False).count()

    hoje = datetime.today()
    vencendo = db.query(Aluguel).filter(
        Aluguel.encerrado == False,
        Aluguel.data_fim <= hoje + timedelta(days=2)
    ).count()

    alugueis_ativos = (
        db.query(Aluguel)
        .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))
        .filter(Aluguel.encerrado == False)
        .order_by(Aluguel.data_inicio.desc())
        .all()
    )
    # ─── Título ───────────────────────────────────────────────
    ctk.CTkLabel(
        frame,
        text="📊 Painel de Controle",
        font=("Segoe UI", 28, "bold"),
        text_color="#1E293B"
    ).pack(pady=(30, 5))

    ctk.CTkLabel(
        frame,
        text="Acompanhe o status geral das operações abaixo",
        font=("Segoe UI", 15),
        text_color="#6B7280"
    ).pack(pady=(0, 20))

    # ─── Cards Verticais ──────────────────────────────────────
    def criar_card_vertical(texto, valor, cor):
        card = ctk.CTkFrame(
            frame,
            corner_radius=16,
            fg_color=cor,
            height=50,
            width=320
        )
        card.pack(pady=10)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=texto,
            font=("Segoe UI", 15, "bold"),
            text_color="white"
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            card,
            text=str(valor),
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        ).pack(side="right", padx=12)


    criar_card_vertical("🚛 Caçambas Alugadas:", total_alugadas, "#3B82F6")   # Azul
    criar_card_vertical("✅ Caçambas Disponíveis:", total_disponiveis, "#10B981")  # Verde
    criar_card_vertical("⚠️ Vencendo em 2 dias:", vencendo, "#EF4444")        # Vermelho


    # Separador visual
    ctk.CTkLabel(frame, text="─" * 50, text_color="#D1D5DB").pack(pady=20)

    

    # Tabela: Caçambas Alugadas
    ctk.CTkLabel(frame, text="📋 Caçambas Alugadas Ativas", font=("Segoe UI", 16, "bold")).pack(pady=6)

    cabecalho = ctk.CTkFrame(frame, fg_color="#dddddd")
    cabecalho.pack(fill="x", padx=10)

    colunas = ["ID", "Cliente", "Caçamba", "Início", "Fim"]
    larguras = [40, 160, 80, 90, 90]

    for i, (titulo, largura) in enumerate(zip(colunas, larguras)):
        ctk.CTkLabel(cabecalho, text=titulo, width=largura, anchor="center", font=("Segoe UI", 12, "bold")).grid(row=0, column=i, padx=2, pady=4)

    corpo = ctk.CTkScrollableFrame(frame, height=280)
    corpo.pack(fill="both", expand=True, padx=10, pady=5)

    if not alugueis_ativos:
        ctk.CTkLabel(corpo, text="⚠️ Nenhuma caçamba está alugada no momento.", font=("Segoe UI", 13)).pack(pady=20)
    else:
        for idx, aluguel in enumerate(alugueis_ativos):
            nome_cliente = aluguel.cliente.nome if aluguel.cliente else "?"
            identificacao = aluguel.cacamba.identificacao if aluguel.cacamba else "?"
            inicio = aluguel.data_inicio.strftime("%d/%m/%Y")
            fim = aluguel.data_fim.strftime("%d/%m/%Y")
            dados = [str(aluguel.id), nome_cliente, identificacao, inicio, fim]

            linha = ctk.CTkFrame(corpo, fg_color="#f6f6f6" if idx % 2 == 0 else "#e2e2e2")
            linha.pack(fill="x")

            for i, (valor, largura) in enumerate(zip(dados, larguras)):
                ctk.CTkLabel(linha, text=valor, width=largura, anchor="center", font=("Segoe UI", 12)).grid(row=0, column=i, padx=2, pady=4)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
from sqlalchemy.orm import joinedload  # no topo do arquivo

def mostrar_apenas_cacambas_alugadas(frame: ctk.CTkFrame):
    """Exibe caçambas alugadas em formato de tabela dentro do dashboard."""
    for widget in frame.winfo_children():
        widget.destroy()

    with SessionLocal() as db:
        alugueis_ativos = (
            db.query(Aluguel)
            .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))
            .filter(Aluguel.encerrado == False)
            .order_by(Aluguel.data_inicio.desc())
            .all()
        )

    # Título
    ctk.CTkLabel(frame, text="🚛 Caçambas Alugadas (Ativas)", font=("Segoe UI", 22, "bold")).pack(pady=10)

    # Cabeçalhos
    cabecalho = ctk.CTkFrame(frame, fg_color="#dddddd")
    cabecalho.pack(fill="x", padx=10)

    colunas = ["ID", "Cliente", "Caçamba", "Início", "Fim"]
    larguras = [40, 160, 80, 90, 90]

    for i, (titulo, largura) in enumerate(zip(colunas, larguras)):
        label = ctk.CTkLabel(cabecalho, text=titulo, width=largura, anchor="center", font=("Segoe UI", 12, "bold"))
        label.grid(row=0, column=i, padx=2, pady=4)

    # Corpo da tabela
    corpo = ctk.CTkScrollableFrame(frame, height=320)
    corpo.pack(fill="both", expand=True, padx=10, pady=5)

    if not alugueis_ativos:
        ctk.CTkLabel(corpo, text="⚠️ Nenhuma caçamba está alugada no momento.", font=("Segoe UI", 13)).pack(pady=20)
        return

    for idx, aluguel in enumerate(alugueis_ativos):
        nome_cliente = aluguel.cliente.nome if aluguel.cliente else "?"
        identificacao = aluguel.cacamba.identificacao if aluguel.cacamba else "?"
        inicio = aluguel.data_inicio.strftime("%d/%m/%Y")
        fim = aluguel.data_fim.strftime("%d/%m/%Y")

        dados = [str(aluguel.id), nome_cliente, identificacao, inicio, fim]

        linha = ctk.CTkFrame(corpo, fg_color="#f6f6f6" if idx % 2 == 0 else "#e2e2e2")
        linha.pack(fill="x")

        for i, (valor, largura) in enumerate(zip(dados, larguras)):
            ctk.CTkLabel(linha, text=valor, width=largura, anchor="center", font=("Segoe UI", 12)).grid(row=0, column=i, padx=2, pady=4)

def ir_para_cacambas_alugadas():
    mostrar_tela("dashboard")
    mostrar_apenas_cacambas_alugadas(telas["dashboard"])



def ir_para_dashboard():
    mostrar_dashboard(telas["dashboard"])
    mostrar_tela("dashboard")


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
        ("📊 Ir para Dashboard", lambda: ir_para_dashboard()),
       ("📊 Ver Caçambas Alugadas", lambda: ir_para_cacambas_alugadas()),
        ("📋 Novo Cliente",           lambda: mostrar_tela("cliente")),
        ("📆 Novo Aluguel",               lambda: mostrar_tela("aluguel")),
        ("↩️ Devoluções",             lambda: mostrar_tela("devolucao")),
        ("📄 Histórico",              lambda: mostrar_tela("historico")),
        ("📋 Clientes (Consulta)",    lambda: mostrar_tela("consulta_clientes")),
        ("🚛 Caçambas",               lambda: mostrar_tela("cacamba")),
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
