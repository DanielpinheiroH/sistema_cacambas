import customtkinter as ctk
from tkinter import messagebox
from tkinter import Canvas
import os

from sqlalchemy.orm import joinedload
from sqlalchemy import Column, Boolean
from app.database import SessionLocal
from app.models import Aluguel
from reportlab.pdfgen import canvas

def construir_tela_historico(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=12)

    # ─── Título ─────────────────────────────────────────────────────────
    ctk.CTkLabel(
        frame,
        text="📜 Histórico de Aluguéis",
        font=("Segoe UI", 26, "bold"),
        text_color="#111827"
    ).pack(pady=(20, 10))

    # ─── Filtro ─────────────────────────────────────────────────────────
    filtro_var = ctk.StringVar(value="Todos")

    filtro_frame = ctk.CTkFrame(frame, fg_color="transparent")
    filtro_frame.pack(pady=(0, 10))

    ctk.CTkLabel(
        filtro_frame,
        text="🔎 Status:",
        font=("Segoe UI", 14)
    ).pack(side="left", padx=(0, 8))

    def carregar_tabela_filtrada():
        status = filtro_var.get()
        exibir_tabela_alugueis_custom(frame, status)

    filtro_menu = ctk.CTkOptionMenu(
        filtro_frame,
        variable=filtro_var,
        values=["Todos", "Ativos", "Encerrados"],
        width=160,
        command=lambda _: carregar_tabela_filtrada()
    )
    filtro_menu.pack(side="left")

    # ─── Função para exibir tabela com filtro ───────────────────────────
    def exibir_tabela_alugueis_custom(destino_frame: ctk.CTkFrame, filtro_status: str = "Todos"):
        # Remove widgets da tabela antiga (menos o título, filtro e recibo)
        for widget in destino_frame.winfo_children()[2:]:
            widget.destroy()

        with SessionLocal() as db:
            query = db.query(Aluguel).options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))

            if filtro_status == "Ativos":
                query = query.filter(Aluguel.encerrado == False)
            elif filtro_status == "Encerrados":
                query = query.filter(Aluguel.encerrado == True)

            alugueis = query.order_by(Aluguel.data_inicio.desc()).all()

        # Cabeçalhos
        cabecalho = ctk.CTkFrame(destino_frame, fg_color="#dddddd")
        cabecalho.pack(fill="x", padx=10)

        colunas = ["ID", "Cliente", "Caçamba", "Início", "Fim", "Status"]
        larguras = [40, 160, 80, 90, 90, 90]

        for i, (titulo, largura) in enumerate(zip(colunas, larguras)):
            label = ctk.CTkLabel(cabecalho, text=titulo, width=largura, anchor="center", font=("Segoe UI", 12, "bold"))
            label.grid(row=0, column=i, padx=2, pady=4)

        corpo = ctk.CTkScrollableFrame(destino_frame, height=320)
        corpo.pack(fill="both", expand=True, padx=10, pady=5)

        if not alugueis:
            ctk.CTkLabel(corpo, text="⚠️ Nenhum aluguel encontrado.", font=("Segoe UI", 13)).pack(pady=20)
            return

        for idx, aluguel in enumerate(alugueis):
            nome_cliente = aluguel.cliente.nome if aluguel.cliente else "?"
            identificacao = aluguel.cacamba.identificacao if aluguel.cacamba else "?"
            status = "✅ Encerrado" if aluguel.encerrado else "🔄 Ativo"
            inicio = aluguel.data_inicio.strftime("%d/%m/%Y")
            fim = aluguel.data_fim.strftime("%d/%m/%Y")

            dados = [str(aluguel.id), nome_cliente, identificacao, inicio, fim, status]

            linha = ctk.CTkFrame(corpo, fg_color="#f6f6f6" if idx % 2 == 0 else "#e2e2e2")
            linha.pack(fill="x")

            for i, (valor, largura) in enumerate(zip(dados, larguras)):
                ctk.CTkLabel(linha, text=valor, width=largura, anchor="center", font=("Segoe UI", 12)).grid(row=0, column=i, padx=2, pady=4)

    # ─── Gerar recibo PDF ───────────────────────────────────────────────
    def gerar_recibo_por_id() -> None:
        id_str = id_entry.get().strip()
        if not id_str.isdigit():
            messagebox.showerror("Erro", "Informe um ID numérico válido.")
            return

        with SessionLocal() as db:
            aluguel = db.query(Aluguel)\
                .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))\
                .filter(Aluguel.id == int(id_str)).first()

        if not aluguel:
            messagebox.showerror("Erro", "Aluguel não encontrado.")
            return

        cliente = aluguel.cliente
        cacamba = aluguel.cacamba

        nome_formatado = cliente.nome.strip().lower().replace(" ", "-")
        recibo_dir = os.path.join(os.getcwd(), "recibos")
        os.makedirs(recibo_dir, exist_ok=True)

        nome_arquivo = f"recibo_{nome_formatado}_{aluguel.id}.pdf"
        caminho = os.path.join(recibo_dir, nome_arquivo)

        c = canvas.Canvas(caminho)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 800, "RECIBO DE LOCAÇÃO DE CAÇAMBA")
        c.setFont("Helvetica", 12)
        c.drawString(50, 760, f"Cliente: {cliente.nome}")
        c.drawString(50, 740, f"CPF/CNPJ: {cliente.cpf_cnpj}")
        c.drawString(50, 720, f"Telefone: {cliente.telefone}")
        c.drawString(50, 700, f"Endereço: {cliente.endereco}")
        c.drawString(50, 680, f"Caçamba: {cacamba.identificacao}")
        c.drawString(50, 660, f"Início: {aluguel.data_inicio.strftime('%d/%m/%Y')}")
        c.drawString(50, 640, f"Devolução: {aluguel.data_fim.strftime('%d/%m/%Y')}")
        c.drawString(50, 620, f"ID do Aluguel: {aluguel.id}")
        c.drawString(50, 580, "Assinatura: ____________________________")
        c.drawString(50, 560, "Data: ____/____/______")
        c.save()

        messagebox.showinfo("Sucesso", f"📄 Recibo salvo em:\n{caminho}")

    # ─── Campo + botão para recibo ───────────────────────────────────────
    recibo_frame = ctk.CTkFrame(frame, fg_color="transparent")
    recibo_frame.pack(pady=(10, 10))

    ctk.CTkLabel(
        recibo_frame,
        text="🎯 Gerar recibo por ID do aluguel:",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(5, 8))

    id_entry = ctk.CTkEntry(
        recibo_frame,
        width=240,
        placeholder_text="Digite o ID do aluguel"
    )
    id_entry.pack(pady=5)

    ctk.CTkButton(
        recibo_frame,
        text="🧾 Gerar PDF",
        command=gerar_recibo_por_id,
        width=220,
        height=42,
        font=("Segoe UI", 13, "bold"),
        fg_color="#2563EB",
        hover_color="#1D4ED8",
        text_color="white",
        corner_radius=12
    ).pack(pady=(10, 10))

    # ─── Carregar a tabela ao abrir ──────────────────────────────────────
    exibir_tabela_alugueis_custom(frame)

    return frame
