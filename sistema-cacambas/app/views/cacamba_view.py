# ═══════════════════════════════════════════════════════════════════════════════
# CADASTRO DE CAÇAMBAS - VISUAL REESTILIZADO COM LAYOUT MODERNO
# ═══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import Cacamba


def construir_tela_cacamba(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=12)
    # Não chame .pack() aqui
# Apenas crie o frame e retorne

    # Título
    ctk.CTkLabel(
        frame,
        text="🗂️ Formulário de Cadastro de Caçamba",
        font=("Segoe UI", 26, "bold")
    ).pack(pady=(10, 25))

    # Área de formulários (container interno)
    form_frame = ctk.CTkFrame(frame, fg_color="transparent")
    form_frame.pack(pady=10)

    # Campo: Identificação
    lbl_id = ctk.CTkLabel(form_frame, text="🆔 Identificação:", font=("Segoe UI", 14))
    lbl_id.grid(row=0, column=0, sticky="w", padx=10, pady=8)
    entry_id = ctk.CTkEntry(form_frame, width=300, placeholder_text="Ex: CMB-101")
    entry_id.grid(row=0, column=1, padx=10, pady=8)

    # Campo: Localização
    lbl_local = ctk.CTkLabel(form_frame, text="📍 Localização:", font=("Segoe UI", 14))
    lbl_local.grid(row=1, column=0, sticky="w", padx=10, pady=8)
    entry_local = ctk.CTkEntry(form_frame, width=300, placeholder_text="Ex: Pátio Leste")
    entry_local.grid(row=1, column=1, padx=10, pady=8)

    # Checkbox: Disponibilidade
    var_disponivel = ctk.BooleanVar(value=True)
    chk_disponivel = ctk.CTkCheckBox(
        form_frame,
        text="Disponível para locação",
        variable=var_disponivel,
        font=("Segoe UI", 13)
    )
    chk_disponivel.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    # Mensagem de status
    status_msg = ctk.CTkLabel(frame, text="", font=("Segoe UI", 13))
    status_msg.pack(pady=5)

    def exibir_status(msg, cor="#10B981"):
        status_msg.configure(text=msg, text_color=cor)
        frame.after(3000, lambda: status_msg.configure(text=""))

    # Função: salvar
    def salvar_cacamba():
        identificacao = entry_id.get().strip()
        localizacao = entry_local.get().strip()
        disponivel = var_disponivel.get()

        if not identificacao:
            exibir_status("❌ Identificação obrigatória!", "#EF4444")
            return

        try:
            with SessionLocal() as db:
                if db.query(Cacamba).filter_by(identificacao=identificacao).first():
                    exibir_status("⚠️ Identificação já cadastrada.", "#F59E0B")
                    return

                nova_cacamba = Cacamba(
                    identificacao=identificacao,
                    localizacao_atual=localizacao,
                    disponivel=disponivel
                )
                db.add(nova_cacamba)
                db.commit()

            entry_id.delete(0, "end")
            entry_local.delete(0, "end")
            var_disponivel.set(True)
            exibir_status("✅ Caçamba cadastrada com sucesso!", "#10B981")

        except SQLAlchemyError as e:
            messagebox.showerror("Erro no Banco de Dados", f"{e}")

    # Botão: Salvar
    ctk.CTkButton(
        frame,
        text="💾 Cadastrar Caçamba",
        command=salvar_cacamba,
        width=240,
        height=42,
        font=("Segoe UI", 14, "bold"),
        fg_color="#3B82F6",
        hover_color="#2563EB",
        text_color="white",
        corner_radius=10
    ).pack(pady=(20, 10))

    return frame
