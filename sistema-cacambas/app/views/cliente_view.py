import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from app.models import Cliente

def abrir_tela_cliente():
    janela = ctk.CTkToplevel()
    janela.title("Cadastro de Cliente")
    janela.geometry("500x420")
    janela.resizable(False, False)

    frame = ctk.CTkFrame(janela, corner_radius=10)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Cadastro de Cliente", font=("Segoe UI", 20, "bold")).pack(pady=10)

    entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome completo", width=400)
    entry_nome.pack(pady=5)

    entry_cpf_cnpj = ctk.CTkEntry(frame, placeholder_text="CPF ou CNPJ", width=400)
    entry_cpf_cnpj.pack(pady=5)

    entry_telefone = ctk.CTkEntry(frame, placeholder_text="Telefone", width=400)
    entry_telefone.pack(pady=5)

    entry_endereco = ctk.CTkEntry(frame, placeholder_text="Endereço", width=400)
    entry_endereco.pack(pady=5)

    def salvar_cliente():
        nome = entry_nome.get().strip()
        cpf_cnpj = entry_cpf_cnpj.get().strip()
        telefone = entry_telefone.get().strip()
        endereco = entry_endereco.get().strip()

        if not nome or not cpf_cnpj:
            messagebox.showerror("Erro", "Nome e CPF/CNPJ são obrigatórios.")
            return

        try:
            db = SessionLocal()
            # Checa duplicidade
            if db.query(Cliente).filter_by(cpf_cnpj=cpf_cnpj).first():
                messagebox.showerror("Erro", "Já existe um cliente com esse CPF/CNPJ.")
                db.close()
                return

            novo_cliente = Cliente(nome=nome, cpf_cnpj=cpf_cnpj, telefone=telefone, endereco=endereco)
            db.add(novo_cliente)
            db.commit()
            db.close()

            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            janela.destroy()

        except SQLAlchemyError as e:
            messagebox.showerror("Erro", f"Erro ao salvar no banco: {e}")

    ctk.CTkButton(frame, text="Salvar Cliente", command=salvar_cliente, width=200).pack(pady=20)
