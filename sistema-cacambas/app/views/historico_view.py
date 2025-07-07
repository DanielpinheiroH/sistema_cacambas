import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models import Aluguel, Cliente, Cacamba
from reportlab.pdfgen import canvas
import os

def abrir_tela_historico():
    janela = ctk.CTkToplevel()
    janela.title("Histórico de Aluguéis")
    janela.geometry("700x500")
    janela.resizable(False, False)

    frame = ctk.CTkFrame(janela, corner_radius=10)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Histórico de Aluguéis", font=("Segoe UI", 20, "bold")).pack(pady=10)

    filtro_var = ctk.StringVar(value="Todos")
    ctk.CTkOptionMenu(
        frame,
        variable=filtro_var,
        values=["Todos", "Ativos", "Encerrados"],
        command=lambda _: carregar_alugueis()
    ).pack(pady=5)

    lista = ctk.CTkTextbox(frame, height=300, width=650, font=("Segoe UI", 12))
    lista.pack(pady=10)

    def carregar_alugueis():
        lista.delete("1.0", "end")
        db = SessionLocal()

        query = db.query(Aluguel).options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))

        if filtro_var.get() == "Ativos":
            query = query.filter(Aluguel.encerrado == False)
        elif filtro_var.get() == "Encerrados":
            query = query.filter(Aluguel.encerrado == True)

        alugueis = query.order_by(Aluguel.data_inicio.desc()).all()
        db.close()

        if not alugueis:
            lista.insert("end", "Nenhum aluguel encontrado.\n")
            return

        for aluguel in alugueis:
            status = "Encerrado ✅" if aluguel.encerrado else "Ativo 🔄"
            texto = (
                f"ID: {aluguel.id} | Cliente: {aluguel.cliente.nome} | "
                f"Caçamba: {aluguel.cacamba.identificacao} | "
                f"Início: {aluguel.data_inicio.strftime('%d/%m/%Y')} | "
                f"Fim: {aluguel.data_fim.strftime('%d/%m/%Y')} | {status}\n"
            )
            lista.insert("end", texto)

    def gerar_recibo_por_id():
        id_str = id_entry.get().strip()
        if not id_str.isdigit():
            messagebox.showerror("Erro", "Informe um ID válido.")
            return

        db = SessionLocal()
        aluguel = db.query(Aluguel).options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))\
            .filter(Aluguel.id == int(id_str)).first()
        db.close()

        if not aluguel:
            messagebox.showerror("Erro", "Aluguel não encontrado.")
            return

        cliente = aluguel.cliente
        cacamba = aluguel.cacamba

        nome_formatado = cliente.nome.strip().lower().replace(" ", "-")
        recibo_dir = os.path.join(os.getcwd(), 'recibos')
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
        c.drawString(50, 660, f"Data de Início: {aluguel.data_inicio.strftime('%d/%m/%Y')}")
        c.drawString(50, 640, f"Data de Devolução: {aluguel.data_fim.strftime('%d/%m/%Y')}")
        c.drawString(50, 620, f"ID do Aluguel: {aluguel.id}")
        c.drawString(50, 580, "Assinatura: ____________________________")
        c.drawString(50, 560, "Data: ____/____/______")
        c.save()

        messagebox.showinfo("Sucesso", f"Recibo salvo em:\n{caminho}")

    ctk.CTkLabel(frame, text="Gerar recibo por ID do aluguel:", font=("Segoe UI", 12)).pack()
    id_entry = ctk.CTkEntry(frame, width=150)
    id_entry.pack(pady=5)
    ctk.CTkButton(frame, text="🧾 Gerar Recibo PDF", command=gerar_recibo_por_id).pack()

    carregar_alugueis()
