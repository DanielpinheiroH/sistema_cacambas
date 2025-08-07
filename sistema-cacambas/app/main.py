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
from .views.token_view import TokenView
from app.utils import cliente_info
from app.utils.firebase_upload import upload_automatico, iniciar_agendamento
from app.utils.firebase_upload import baixar_backup_do_cliente
import atexit

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

            ctk.CTkButton(linha, text=btn_texto, width=60, height=30, font=("Segoe UI", 12), fg_color=btn_cor,
                          hover_color=btn_hover, command=lambda a_id=aluguel.id, f=frame: alternar_status_pagamento(a_id, f)).grid(row=0, column=len(dados), padx=4)

def alternar_status_pagamento(aluguel_id: int, frame: ctk.CTkFrame):
    with SessionLocal() as db:
        aluguel = db.query(Aluguel).get(aluguel_id)
        if aluguel:
            aluguel.pago = not aluguel.pago
            db.commit()
    mostrar_dashboard(frame)

def buscar_historico_por_cacamba(identificacao: str, frame: ctk.CTkFrame):
    if hasattr(frame, "frame_resultado") and frame.frame_resultado:
        frame.frame_resultado.destroy()

    if not identificacao:
        resultado = ctk.CTkLabel(frame, text="⚠️ Informe a identificação da caçamba.", font=("Segoe UI", 12))
        resultado.grid(row=4, column=0, pady=5)
        frame.frame_resultado = resultado
        return

    with SessionLocal() as db:
        cacamba = db.query(Cacamba).filter(Cacamba.identificacao == identificacao).first()

        if not cacamba:
            resultado = ctk.CTkLabel(frame, text="⚠️ Caçamba não encontrada.", font=("Segoe UI", 12))
            resultado.grid(row=4, column=0, pady=5)
            frame.frame_resultado = resultado
            return

        alugueis = (
            db.query(Aluguel)
            .options(joinedload(Aluguel.cliente))
            .filter(Aluguel.id_cacamba == cacamba.id)
            .order_by(Aluguel.data_inicio.desc())
            .all()
        )

    frame.frame_resultado = ctk.CTkScrollableFrame(frame, height=200)
    frame.frame_resultado.grid(row=4, column=0, columnspan=1, sticky="nsew", padx=10, pady=(5, 20))

    if not alugueis:
        ctk.CTkLabel(frame.frame_resultado, text="⚠️ Nenhum histórico encontrado.", font=("Segoe UI", 12)).pack(pady=5)
        return

    # Cabeçalho da tabela
    cabecalho = ctk.CTkFrame(frame.frame_resultado, fg_color="#ddd")
    cabecalho.pack(fill="x")
    colunas = ["ID", "Cliente", "Início", "Fim", "Pago", "Status", "Endereço"]
    larguras = [50, 150, 100, 100, 60, 80, 300]

    for i, (titulo, largura) in enumerate(zip(colunas, larguras)):
        ctk.CTkLabel(cabecalho, text=titulo, width=largura, anchor="center", font=("Segoe UI", 12, "bold")).grid(row=0, column=i, padx=2, pady=4)

    for idx, aluguel in enumerate(alugueis):
        cliente = aluguel.cliente.nome if aluguel.cliente else "—"
        inicio = aluguel.data_inicio.strftime("%d/%m/%Y")
        fim = aluguel.data_fim.strftime("%d/%m/%Y")
        pago = "✅" if aluguel.pago else "❌"
        status = "🔴 Ativa" if not aluguel.encerrado else "✅ Finalizado"
        endereco = aluguel.endereco_obra or "—"

        valores = [str(aluguel.id), cliente, inicio, fim, pago, status, endereco]

        linha = ctk.CTkFrame(frame.frame_resultado, fg_color="#f9f9f9" if idx % 2 == 0 else "#e2e2e2")
        linha.pack(fill="x")

        for i, (valor, largura) in enumerate(zip(valores, larguras)):
            ctk.CTkLabel(linha, text=valor, width=largura, anchor="center", font=("Segoe UI", 11)).grid(row=0, column=i, padx=2, pady=3)




def mostrar_apenas_cacambas_alugadas(frame: ctk.CTkFrame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.grid_rowconfigure(3, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.frame_resultado = None

    # Título
    ctk.CTkLabel(
        frame,
        text="🚛 Caçambas Alugadas (Ativas)",
        font=("Segoe UI", 22, "bold")
    ).grid(row=0, column=0, pady=(20, 10), sticky="n")

    # 🔍 Campo de busca
    busca_frame = ctk.CTkFrame(frame, fg_color="transparent")
    busca_frame.grid(row=1, column=0, pady=(0, 5), sticky="ew")

    entry_identificacao = ctk.CTkEntry(
        busca_frame,
        placeholder_text="🔍 Digite a identificação da caçamba",
        width=280
    )
    entry_identificacao.grid(row=0, column=0, padx=(0, 10))

    def filtrar_por_cacamba():
        identificacao = entry_identificacao.get()
        for linha in corpo.winfo_children():
            linha.destroy()

        with SessionLocal() as db:
            alugueis_filtrados = (
                db.query(Aluguel)
                .join(Cacamba)  # ✅ Resolve o problema
                .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))
                .filter(Aluguel.encerrado == False)
                .filter(Cacamba.identificacao.like(f"%{identificacao}%"))
                .order_by(Aluguel.data_inicio.desc())
                .all()
            )

        if not alugueis_filtrados:
            ctk.CTkLabel(
                corpo,
                text="⚠️ Nenhuma caçamba encontrada com essa identificação.",
                font=("Segoe UI", 13)
            ).grid(row=0, column=0, pady=10)
            return

        for idx, aluguel in enumerate(alugueis_filtrados):
            nome = aluguel.cliente.nome if aluguel.cliente else "—"
            id_cacamba = aluguel.cacamba.identificacao if aluguel.cacamba else "—"
            inicio = aluguel.data_inicio.strftime("%d/%m/%Y")
            fim = aluguel.data_fim.strftime("%d/%m/%Y")
            endereco = aluguel.endereco_obra or "—"
            pago = "✅" if aluguel.pago else "❌"
            btn_texto = "💰" if not aluguel.pago else "↩️"
            btn_cor = "#10B981" if not aluguel.pago else "#F59E0B"
            btn_hover = "#059669" if not aluguel.pago else "#D97706"

            dados = [str(aluguel.id), nome, id_cacamba, inicio, fim, endereco, pago]

            linha = ctk.CTkFrame(corpo, fg_color="#ffffff" if idx % 2 == 0 else "#f1f1f1")
            linha.grid(row=idx, column=0, sticky="ew", padx=0, pady=0)

            for i, (valor, largura) in enumerate(zip(dados, larguras)):
                ctk.CTkLabel(
                    linha,
                    text=valor,
                    width=largura,
                    anchor="center",
                    font=("Segoe UI", 11)
                ).grid(row=0, column=i, padx=1, pady=1)

            ctk.CTkButton(
                linha,
                text=btn_texto,
                font=("Segoe UI", 10),
                width=larguras[-1],
                height=26,
                fg_color=btn_cor,
                hover_color=btn_hover,
                command=lambda a_id=aluguel.id, f=frame: alternar_status_pagamento(a_id, f)
            ).grid(row=0, column=len(dados), padx=2, pady=2)

    ctk.CTkButton(
        busca_frame,
        text="🔍 Buscar",
        fg_color="#1D4ED8",
        hover_color="#1E40AF",
        command=filtrar_por_cacamba
    ).grid(row=0, column=1)

    # Cabeçalho
    colunas = ["ID", "Cliente", "Caçamba", "Início", "Fim", "Endereço", "Pago", "Ação"]
    larguras = [50, 160, 80, 90, 90, 300, 60, 60]

    cabecalho = ctk.CTkFrame(frame, fg_color="#dddddd")
    cabecalho.grid(row=2, column=0, sticky="ew", padx=10)
    for i, (titulo, largura) in enumerate(zip(colunas, larguras)):
        ctk.CTkLabel(
            cabecalho,
            text=titulo,
            width=largura,
            anchor="center",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=i, padx=2, pady=3)

    corpo = ctk.CTkScrollableFrame(frame)
    corpo.grid(row=3, column=0, sticky="nsew", padx=10, pady=(2, 20))
    corpo.grid_columnconfigure(0, weight=1)

    # Carregar todos inicialmente
    filtrar_por_cacamba()


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


    def on_token_validado(cliente):
        cliente_info.cliente.clear()
        cliente_info.cliente.update(cliente)  # atualiza o mesmo dicionário, mantém a referência
        print("🔑 Token validado com sucesso!")
        baixar_backup_do_cliente()
        atexit.register(upload_automatico)
        iniciar_agendamento(30)
        mostrar_dashboard(telas["dashboard"])
        mostrar_tela("dashboard")
        botoes_frame.grid()

        

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

    token_view = TokenView(container, on_token_validado)
    token_view.grid(row=0, column=0, sticky="nsew")

    #mostrar_dashboard(telas["dashboard"])
    #mostrar_tela("dashboard")

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

    # ⛔️ Oculta os botões até validar o token
    botoes_frame.grid_remove()


    root.mainloop()

if __name__ == "__main__":
    main()
