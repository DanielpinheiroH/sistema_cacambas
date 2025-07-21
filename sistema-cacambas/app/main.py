# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA DE CAÇAMBAS - TELA PRINCIPAL
# Desenvolvido com CustomTkinter + SQLAlchemy
# Layout totalmente responsivo (100% grid)
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
from sqlalchemy.orm import joinedload

telas = {}

def mostrar_tela(nome: str) -> None:
    if nome in telas and telas[nome].winfo_exists():
        telas[nome].tkraise()
    else:
        print(f"⚠️ Tela '{nome}' não encontrada ou foi destruída.")

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

    ctk.CTkLabel(frame, text="📊 Painel de Controle", font=("Segoe UI", 28, "bold"), text_color="#1E293B").pack(pady=(30, 5))
    ctk.CTkLabel(frame, text="Acompanhe o status geral das operações abaixo", font=("Segoe UI", 15), text_color="#6B7280").pack(pady=(0, 20))

    def criar_card_vertical(texto, valor, cor):
        card = ctk.CTkFrame(frame, corner_radius=16, fg_color=cor, height=50, width=320)
        card.pack(pady=10)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=texto, font=("Segoe UI", 15, "bold"), text_color="white").pack(side="left", padx=10)
        ctk.CTkLabel(card, text=str(valor), font=("Segoe UI", 18, "bold"), text_color="white").pack(side="right", padx=12)

    criar_card_vertical("🚛 Caçambas Alugadas:", total_alugadas, "#3B82F6")
    criar_card_vertical("✅ Caçambas Disponíveis:", total_disponiveis, "#10B981")
    criar_card_vertical("⚠️ Vencendo em 2 dias:", vencendo, "#EF4444")

    ctk.CTkLabel(frame, text="─" * 50, text_color="#D1D5DB").pack(pady=20)
    ctk.CTkLabel(frame, text="📋 Caçambas Alugadas Ativas", font=("Segoe UI", 16, "bold")).pack(pady=6)

    cabecalho = ctk.CTkFrame(frame, fg_color="#dddddd")
    cabecalho.pack(fill="x", padx=10)
    colunas = ["ID", "Cliente", "Caçamba", "Início", "Fim", "Endereço da Obra", "Pago?", "Ação"]
    larguras = [40, 160, 80, 90, 90, 240, 80, 80]

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
            endereco_obra = aluguel.endereco_obra or "—"
            pago = "✅" if aluguel.pago else "❌"
            btn_texto = "💰 Marcar" if not aluguel.pago else "↩️ Estornar"
            btn_cor = "#10B981" if not aluguel.pago else "#F59E0B"
            btn_hover = "#059669" if not aluguel.pago else "#D97706"

            dados = [str(aluguel.id), nome_cliente, identificacao, inicio, fim, endereco_obra, pago]
            linha = ctk.CTkFrame(corpo, fg_color="#f6f6f6" if idx % 2 == 0 else "#e2e2e2")
            linha.pack(fill="x")

            for i, (valor, largura) in enumerate(zip(dados, larguras)):
                ctk.CTkLabel(linha, text=valor, width=largura, anchor="center", font=("Segoe UI", 12)).grid(row=0, column=i, padx=2, pady=4)

            ctk.CTkButton(linha, text=btn_texto, width=90, height=30, font=("Segoe UI", 12), fg_color=btn_cor,
                          hover_color=btn_hover, command=lambda a_id=aluguel.id, f=frame: alternar_status_pagamento(a_id, f)).grid(row=0, column=len(dados), padx=4)

def alternar_status_pagamento(aluguel_id: int, frame: ctk.CTkFrame):
    with SessionLocal() as db:
        aluguel = db.query(Aluguel).get(aluguel_id)
        if aluguel:
            aluguel.pago = not aluguel.pago
            db.commit()
    mostrar_dashboard(frame)

def mostrar_apenas_cacambas_alugadas(frame: ctk.CTkFrame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.grid_rowconfigure(2, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    with SessionLocal() as db:
        alugueis_ativos = (
            db.query(Aluguel)
            .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))
            .filter(Aluguel.encerrado == False)
            .order_by(Aluguel.data_inicio.desc())
            .all()
        )

    ctk.CTkLabel(
        frame,
        text="🚛 Caçambas Alugadas (Ativas)",
        font=("Segoe UI", 22, "bold")
    ).grid(row=0, column=0, pady=(20, 10), sticky="n")

    # Cabeçalho
    cabecalho = ctk.CTkFrame(frame, fg_color="#dddddd")
    cabecalho.grid(row=1, column=0, sticky="ew", padx=10)
    cabecalho.grid_columnconfigure(tuple(range(8)), weight=1)

    colunas = ["ID", "Cliente", "Caçamba", "Início", "Fim", "Endereço da Obra", "Pago?", "Ação"]

    for i, titulo in enumerate(colunas):
        ctk.CTkLabel(
            cabecalho,
            text=titulo,
            anchor="center",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=i, padx=2, pady=4, sticky="nsew")

    # Corpo com scroll
    corpo = ctk.CTkScrollableFrame(frame, height=400)
    corpo.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 20))
    corpo.grid_columnconfigure(0, weight=1)

    if not alugueis_ativos:
        ctk.CTkLabel(
            corpo,
            text="⚠️ Nenhuma caçamba está alugada no momento.",
            font=("Segoe UI", 13)
        ).grid(row=0, column=0, pady=20)
        return

    for idx, aluguel in enumerate(alugueis_ativos):
        nome_cliente = aluguel.cliente.nome if aluguel.cliente else "?"
        identificacao = aluguel.cacamba.identificacao if aluguel.cacamba else "?"
        inicio = aluguel.data_inicio.strftime("%d/%m/%Y")
        fim = aluguel.data_fim.strftime("%d/%m/%Y")
        endereco_obra = aluguel.endereco_obra or "—"
        pago = "✅" if aluguel.pago else "❌"
        btn_texto = "💰 Marcar" if not aluguel.pago else "↩️ Estornar"
        btn_cor = "#10B981" if not aluguel.pago else "#F59E0B"
        btn_hover = "#059669" if not aluguel.pago else "#D97706"

        dados = [str(aluguel.id), nome_cliente, identificacao, inicio, fim, endereco_obra, pago]

        linha = ctk.CTkFrame(corpo, fg_color="#f6f6f6" if idx % 2 == 0 else "#e2e2e2")
        linha.grid(row=idx, column=0, sticky="ew", pady=1)
        linha.grid_columnconfigure(tuple(range(len(dados) + 1)), weight=1)

        for i, valor in enumerate(dados):
            ctk.CTkLabel(
                linha,
                text=valor,
                anchor="center",
                font=("Segoe UI", 12)
            ).grid(row=0, column=i, padx=2, pady=4, sticky="nsew")

        ctk.CTkButton(
            linha,
            text=btn_texto,
            font=("Segoe UI", 12),
            fg_color=btn_cor,
            hover_color=btn_hover,
            command=lambda a_id=aluguel.id, f=frame: alternar_status_pagamento(a_id, f)
        ).grid(row=0, column=len(dados), padx=4, sticky="nsew")


def ir_para_cacambas_alugadas():
    mostrar_apenas_cacambas_alugadas(telas["ver_cacambas"])
    mostrar_tela("ver_cacambas")

def ir_para_dashboard():
    mostrar_dashboard(telas["dashboard"])
    mostrar_tela("dashboard")

def main() -> None:
    init_db()
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Sistema de Caçambas - Menu Principal")
    root.geometry("1000x720")
    root.minsize(800, 600)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    container = ctk.CTkFrame(root)
    container.grid(row=0, column=0, sticky="nsew")
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)

    telas.update({
        "dashboard": ctk.CTkFrame(container),
        "cliente": construir_tela_cliente(container),
        "cacamba": construir_tela_cacamba(container),
        "aluguel": construir_tela_aluguel(container),
        "devolucao": construir_tela_devolucao(container),
        "locacao": construir_tela_locacao(container),
        "historico": construir_tela_historico(container),
        "consulta_clientes": construir_tela_consulta_clientes(container),
        "ver_cacambas": ctk.CTkFrame(container)
    })

    for tela in telas.values():
        tela.grid(row=0, column=0, sticky="nsew")

    mostrar_dashboard(telas["dashboard"])
    mostrar_tela("dashboard")

    botoes = [
        ("📊 Dashboard", lambda: ir_para_dashboard()),
        ("🚛 Caçambas Alugadas", lambda: ir_para_cacambas_alugadas()),
        ("👤 Cliente", lambda: mostrar_tela("cliente")),
        ("➕ Aluguel", lambda: mostrar_tela("aluguel")),
        ("↩️ Devolução", lambda: mostrar_tela("devolucao")),
        ("📄 Histórico", lambda: mostrar_tela("historico")),
        ("🔍 Clientes", lambda: mostrar_tela("consulta_clientes")),
        ("⚙️ Caçambas", lambda: mostrar_tela("cacamba")),
    ]

    botoes_frame = ctk.CTkFrame(root)
    botoes_frame.grid(row=1, column=0, pady=10)
    botoes_frame.columnconfigure(tuple(range(len(botoes))), weight=1)

    for idx, (texto, comando) in enumerate(botoes):
        ctk.CTkButton(
            botoes_frame,
            text=texto,
            command=comando,
            width=130,
            height=38,
            font=("Segoe UI", 12),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white",
            corner_radius=8
        ).grid(row=0, column=idx, padx=6, pady=5, sticky="ew")

    root.mainloop()

if __name__ == "__main__":
    main()
