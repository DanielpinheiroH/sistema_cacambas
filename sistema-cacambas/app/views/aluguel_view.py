# ═══════════════════════════════════════════════════════════════════════════════
# TELA DE ALUGUEL E DEVOLUÇÃO DE CAÇAMBAS - VISUAL MODERNO
# ═══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models import Cliente, Cacamba, Aluguel


# ═══════════════════════════════════════════════════════════════════════════════
# TELA: NOVO ALUGUEL
# ═══════════════════════════════════════════════════════════════════════════════

def construir_tela_aluguel(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=15)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Título
    ctk.CTkLabel(
        frame,
        text="📄 Registrar Novo Aluguel",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(20, 10))

    # Banco de dados
    with SessionLocal() as db:
        clientes = db.query(Cliente).all()
        cacambas = db.query(Cacamba).filter_by(disponivel=True).all()

    # Cliente
    ctk.CTkLabel(frame, text="👤 Cliente:", font=("Segoe UI", 14)).pack(pady=(5, 0))
    combo_cliente = ctk.CTkOptionMenu(
        frame,
        width=350,
        values=[f"{c.id} - {c.nome}" for c in clientes] or ["Nenhum cliente encontrado"]
    )
    combo_cliente.pack(pady=5)

    # Caçamba
    ctk.CTkLabel(frame, text="🚛 Caçamba disponível:", font=("Segoe UI", 14)).pack(pady=(10, 0))
    combo_cacamba = ctk.CTkOptionMenu(
        frame,
        width=350,
        values=[f"{c.id} - {c.identificacao}" for c in cacambas] or ["Nenhuma disponível"]
    )
    combo_cacamba.pack(pady=5)

    # Data de início
    ctk.CTkLabel(frame, text="📅 Data de Início (dd/mm/aaaa):", font=("Segoe UI", 14)).pack(pady=(10, 0))
    entry_inicio = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 10/07/2025")
    entry_inicio.pack(pady=5)

    # Data de fim
    ctk.CTkLabel(frame, text="📅 Data de Fim (dd/mm/aaaa):", font=("Segoe UI", 14)).pack(pady=(10, 0))
    entry_fim = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 15/07/2025")
    entry_fim.pack(pady=5)

    # Valor do aluguel
    ctk.CTkLabel(frame, text="💲 Valor do aluguel (R$):", font=("Segoe UI", 14)).pack(pady=(10, 0))
    entry_valor = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 450.00")
    entry_valor.pack(pady=5)

    # Botão salvar
    def salvar_aluguel():
        try:
            cliente_id = int(combo_cliente.get().split(" - ")[0])
            cacamba_id = int(combo_cacamba.get().split(" - ")[0])
            data_inicio = datetime.strptime(entry_inicio.get(), "%d/%m/%Y")
            data_fim = datetime.strptime(entry_fim.get(), "%d/%m/%Y")
            valor = float(entry_valor.get().replace(",", "."))

            if data_fim <= data_inicio:
                messagebox.showerror("Erro", "A data de fim deve ser posterior à data de início.")
                return

            with SessionLocal() as db:
                aluguel = Aluguel(
                    cliente_id=cliente_id,
                    cacamba_id=cacamba_id,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    valor=valor
                )
                db.add(aluguel)
                cacamba = db.query(Cacamba).get(cacamba_id)
                cacamba.disponivel = False
                db.commit()

            messagebox.showinfo("Sucesso", "✅ Aluguel registrado com sucesso!")
            combo_cliente.set("")
            combo_cacamba.set("")
            entry_inicio.delete(0, "end")
            entry_fim.delete(0, "end")
            entry_valor.delete(0, "end")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao registrar aluguel:\n{e}")

    ctk.CTkButton(
        frame,
        text="💾 Salvar Aluguel",
        command=salvar_aluguel,
        fg_color="#228B22",
        hover_color="#1E6F1E",
        font=("Segoe UI", 14, "bold"),
        width=200,
        height=40
    ).pack(pady=20)

    return frame

# ═══════════════════════════════════════════════════════════════════════════════
# TELA: REGISTRAR DEVOLUÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def construir_tela_devolucao(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=10)

    ctk.CTkLabel(
        frame,
        text="↩️ Devolução de Caçamba",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(20, 10))

    # Subtítulo
    ctk.CTkLabel(
        frame,
        text="Selecione o aluguel ativo para confirmar a devolução:",
        font=("Segoe UI", 14)
    ).pack(pady=(0, 15))

    with SessionLocal() as db:
        alugueis = db.query(Aluguel).filter_by(encerrado=False)\
            .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba)).all()

    lista_exibicao = [
        f"{a.id} - {a.cliente.nome} | Caçamba: {a.cacamba.identificacao} | Fim: {a.data_fim.strftime('%d/%m/%Y')}"
        for a in alugueis
    ] or ["Nenhum aluguel disponível"]

    combo = ctk.CTkOptionMenu(
        frame,
        values=lista_exibicao,
        width=400
    )
    combo.pack(pady=10)
    combo.set(lista_exibicao[0])

    status_label = ctk.CTkLabel(frame, text="", font=("Segoe UI", 12))
    status_label.pack(pady=5)

    def animar_confirmacao(msg, cor="green"):
        status_label.configure(text=msg, text_color=cor)
        frame.after(2000, lambda: status_label.configure(text=""))

    def confirmar_devolucao():
        selecionado = combo.get()
        if "Nenhum" in selecionado:
            messagebox.showerror("Erro", "Nenhum aluguel selecionado.")
            return

        try:
            aluguel_id = int(selecionado.split(" - ")[0])

            with SessionLocal() as db:
                aluguel = db.query(Aluguel).get(aluguel_id)
                aluguel.encerrado = True

                cacamba = db.query(Cacamba).get(aluguel.cacamba_id)
                cacamba.disponivel = True

                db.commit()

            animar_confirmacao("✅ Devolução registrada com sucesso!", cor="green")

        except Exception as e:
            animar_confirmacao("❌ Erro ao registrar devolução!", cor="red")
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

    ctk.CTkButton(
        frame,
        text="✅ Confirmar Devolução",
        command=confirmar_devolucao,
        fg_color="#4CAF50",
        hover_color="#45A049",
        width=300,
        height=40,
        font=("Segoe UI", 14, "bold")
    ).pack(pady=20)

    return frame
