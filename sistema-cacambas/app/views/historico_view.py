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

    filtro_menu = ctk.CTkOptionMenu(
        filtro_frame,
        variable=filtro_var,
        values=["Todos", "Ativos", "Encerrados"],
        width=160,
        command=lambda _: carregar_alugueis()
    )
    filtro_menu.pack(side="left")

    # ─── Lista de aluguéis ──────────────────────────────────────────────
    lista = ctk.CTkTextbox(
        frame,
        height=320,
        width=720,
        font=("Segoe UI", 13),
        corner_radius=10,
        border_width=1.5,
        border_color="#E5E7EB"
    )
    lista.pack(pady=10)

    def carregar_alugueis() -> None:
        lista.delete("1.0", "end")

        with SessionLocal() as db:
            query = db.query(Aluguel).options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))

            if filtro_var.get() == "Ativos":
                query = query.filter(Aluguel.encerrado.is_(False))
            elif filtro_var.get() == "Encerrados":
                query = query.filter(Aluguel.encerrado.is_(True))

            alugueis = query.order_by(Aluguel.data_inicio.desc()).all()

        if not alugueis:
            lista.insert("end", "⚠️ Nenhum aluguel encontrado.\n")
            return

        
        

        for aluguel in alugueis:
            status = "✅ Encerrado" if aluguel.encerrado else "🔄 Ativo"
            texto = (
                f"📦 ID: {aluguel.id} | Cliente: {aluguel.cliente.nome}\n"
                f"   🏷️ Caçamba: {aluguel.cacamba.identificacao}\n"
                f"   📅 Início: {aluguel.data_inicio.strftime('%d/%m/%Y')} | "
                f"Fim: {aluguel.data_fim.strftime('%d/%m/%Y')} | Status: {status}\n\n"
            )
            lista.insert("end", texto)


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
        fg_color="#2563EB",         # Azul moderno
        hover_color="#1D4ED8",
        text_color="white",
        corner_radius=12
    ).pack(pady=(10, 10))

    carregar_alugueis()
    return frame
