import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from app.models import Cacamba

def construir_tela_cacamba(pai):
    frame = ctk.CTkFrame(pai, corner_radius=10)

    ctk.CTkLabel(frame, text="Cadastro de Caçamba", font=("Segoe UI", 20, "bold")).pack(pady=10)

    entry_id = ctk.CTkEntry(frame, placeholder_text="Identificação (ex: CMB-001)", width=400)
    entry_id.pack(pady=8)

    entry_local = ctk.CTkEntry(frame, placeholder_text="Localização atual", width=400)
    entry_local.pack(pady=8)

    var_disponivel = ctk.BooleanVar(value=True)
    chk_disponivel = ctk.CTkCheckBox(frame, text="Disponível", variable=var_disponivel)
    chk_disponivel.pack(pady=10)

    def salvar_cacamba():
        identificacao = entry_id.get().strip()
        localizacao = entry_local.get().strip()
        disponivel = var_disponivel.get()

        if not identificacao:
            messagebox.showerror("Erro", "A identificação é obrigatória.")
            return

        try:
            db = SessionLocal()

            # Verifica duplicidade
            if db.query(Cacamba).filter_by(identificacao=identificacao).first():
                messagebox.showerror("Erro", "Já existe uma caçamba com essa identificação.")
                db.close()
                return

            nova = Cacamba(
                identificacao=identificacao,
                localizacao_atual=localizacao,
                disponivel=disponivel
            )
            db.add(nova)
            db.commit()
            db.close()

            messagebox.showinfo("Sucesso", "Caçamba cadastrada com sucesso!")

            # Limpa os campos após sucesso
            entry_id.delete(0, "end")
            entry_local.delete(0, "end")
            var_disponivel.set(True)

        except SQLAlchemyError as e:
            messagebox.showerror("Erro", f"Erro ao salvar no banco: {e}")

    ctk.CTkButton(frame, text="Salvar Caçamba", command=salvar_cacamba, width=200).pack(pady=15)

    return frame
