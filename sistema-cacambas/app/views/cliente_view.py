# ═══════════════════════════════════════════════════════════════════════════════
# CADASTRO DE CLIENTE - INTERFACE MODERNA
# ═══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import Cliente


def construir_tela_cliente(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=10)

    # ─── Título ─────────────────────────────────────────────────────────
    ctk.CTkLabel(
        frame,
        text="👤 Cadastro de Cliente",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(20, 10))

    # ─── Campo: Nome completo ───────────────────────────────────────────
    entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome completo", width=400)
    entry_nome.pack(pady=6)

    # ─── Campo: CPF ou CNPJ ─────────────────────────────────────────────
    entry_cpf_cnpj = ctk.CTkEntry(frame, placeholder_text="CPF ou CNPJ", width=400)
    entry_cpf_cnpj.pack(pady=6)

    # ─── Campo: E-mail ──────────────────────────────────────────────────
    entry_email = ctk.CTkEntry(frame, placeholder_text="E-mail", width=400)
    entry_email.pack(pady=6)

    # ─── Campo: Endereço ────────────────────────────────────────────────
    entry_endereco = ctk.CTkEntry(frame, placeholder_text="Endereço (rua, avenida etc.)", width=400)
    entry_endereco.pack(pady=6)

    # ─── Campo: Número ──────────────────────────────────────────────────
    entry_numero = ctk.CTkEntry(frame, placeholder_text="Número", width=400)
    entry_numero.pack(pady=6)

    # ─── Botão de salvar ────────────────────────────────────────────────
    def salvar_cliente():
        nome = entry_nome.get().strip()
        cpf_cnpj = entry_cpf_cnpj.get().strip()
        email = entry_email.get().strip()
        endereco = entry_endereco.get().strip()
        numero = entry_numero.get().strip()

        if not nome or not cpf_cnpj:
            messagebox.showerror("Erro", "Nome e CPF/CNPJ são obrigatórios.")
            return

        try:
            with SessionLocal() as db:
                if db.query(Cliente).filter_by(cpf_cnpj=cpf_cnpj).first():
                    messagebox.showerror("Erro", "Já existe um cliente com este CPF/CNPJ.")
                    return

                novo = Cliente(
                    nome=nome,
                    cpf_cnpj=cpf_cnpj,
                    email=email,
                    endereco=f"{endereco}, Nº {numero}"
                )
                db.add(novo)
                db.commit()

            messagebox.showinfo("Sucesso", "✅ Cliente cadastrado com sucesso!")

            entry_nome.delete(0, "end")
            entry_cpf_cnpj.delete(0, "end")
            entry_email.delete(0, "end")
            entry_endereco.delete(0, "end")
            entry_numero.delete(0, "end")

        except SQLAlchemyError as e:
            messagebox.showerror("Erro", f"Erro ao salvar no banco:\n{e}")

    ctk.CTkButton(
        frame,
        text="💾 Salvar Cliente",
        command=salvar_cliente,
        width=250,
        height=40,
        font=("Segoe UI", 14, "bold")
    ).pack(pady=20)

    return frame