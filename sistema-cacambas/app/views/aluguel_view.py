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
    combo_cliente = ctk.CTkOptionMenu(frame, width=350, values=[])
    combo_cliente.pack(pady=5)

    # Caçamba
    ctk.CTkLabel(frame, text="🚛 Caçamba disponível:", font=("Segoe UI", 14)).pack(pady=(10, 0))
    combo_cacamba = ctk.CTkOptionMenu(frame, width=350, values=[])
    combo_cacamba.pack(pady=5)

   

    # Função para atualizar as listas de clientes e caçambas
    def atualizar_listas(combo_cliente_widget, combo_cacamba_widget):
        with SessionLocal() as db:
            clientes = db.query(Cliente).all()
            cacambas = db.query(Cacamba).filter_by(disponivel=True).all()

        valores_clientes = [f"{c.id} - {c.nome}" for c in clientes] or ["Nenhum cliente encontrado"]
        valores_cacambas = [f"{c.id} - {c.identificacao}" for c in cacambas] or ["Nenhuma disponível"]

        combo_cliente_widget.configure(values=valores_clientes)
        combo_cacamba_widget.configure(values=valores_cacambas)

        if valores_clientes:
            combo_cliente_widget.set(valores_clientes[0])
        else:
            combo_cliente_widget.set("")

        if valores_cacambas:
            combo_cacamba_widget.set(valores_cacambas[0])
        else:
            combo_cacamba_widget.set("")
    
    # Chamada inicial ao abrir a tela
    atualizar_listas(combo_cliente, combo_cacamba)
    combo_cacamba.pack(pady=5)

    # Data de início
    ctk.CTkLabel(frame, text="📅 Data de Início (dd/mm/aaaa):", font=("Segoe UI", 14)).pack(pady=(10, 0))
    entry_inicio = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 10/07/2025")
    entry_inicio.pack(pady=5)

    # Data de fim
    ctk.CTkLabel(frame, text="📅 Data de Fim (dd/mm/aaaa):", font=("Segoe UI", 14)).pack(pady=(10, 0))
    entry_fim = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 15/07/2025")
    entry_fim.pack(pady=5)

    # Endereço da Obra
    ctk.CTkLabel(frame, text="📍 Endereço da Obra:", font=("Segoe UI", 14)).pack(pady=(10, 0))
    entry_endereco = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: Rua A, nº 123 - Bairro X")
    entry_endereco.pack(pady=5)
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
            
            endereco_obra = entry_endereco.get().strip()
            if not endereco_obra:
                messagebox.showerror("Erro", "Informe o endereço da obra.")
                return

            with SessionLocal() as db:
                aluguel = Aluguel(
                   cliente_id=cliente_id,
                   cacamba_id=cacamba_id,
                   data_inicio=data_inicio,
                   data_fim=data_fim,
                   valor=valor,
                   endereco_obra=endereco_obra
                )
                db.add(aluguel)
                cacamba = db.query(Cacamba).get(cacamba_id)
                cacamba.disponivel = False
                db.commit()
            
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
 # Botão para atualizar as listas
    ctk.CTkButton(
        frame,
        text="🔄 Atualizar Caçambas",
        command=lambda: atualizar_listas(combo_cliente, combo_cacamba),
        fg_color="#1E90FF",
        hover_color="#1C86EE",
        font=("Segoe UI", 12, "bold"),
        width=200,
        height=30
    ).pack(pady=(5, 10))

    return frame

# ═══════════════════════════════════════════════════════════════════════════════
# TELA: REGISTRAR DEVOLUÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def construir_tela_devolucao(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=16)
    frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
    frame.grid_columnconfigure(0, weight=1)

    # ─── Título ─────────────────────────────────────
    ctk.CTkLabel(
        frame,
        text="↩️ Devolução de Caçambas",
        font=("Segoe UI", 26, "bold"),
        text_color="#111827"
    ).grid(row=0, column=0, pady=(30, 10), sticky="n")

    # ─── Subtítulo ─────────────────────────────────
    ctk.CTkLabel(
        frame,
        text="Selecione um aluguel ativo para confirmar a devolução:",
        font=("Segoe UI", 15),
        text_color="#374151"
    ).grid(row=1, column=0, pady=(0, 20), sticky="n")

    # ─── Combo de Aluguéis ─────────────────────────
    combo_var = ctk.StringVar()
    combo = ctk.CTkOptionMenu(frame, variable=combo_var, values=[], width=460)
    combo.grid(row=2, column=0, pady=(0, 10))

    # ─── Status da Operação ────────────────────────
    status_label = ctk.CTkLabel(frame, text="", font=("Segoe UI", 13))
    status_label.grid(row=3, column=0, pady=(5, 10))

    # ─── Atualizar Lista ───────────────────────────
    def atualizar_lista_alugueis():
        with SessionLocal() as db:
            alugueis = (
                db.query(Aluguel)
                .filter_by(encerrado=False)
                .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))
                .order_by(Aluguel.data_fim.asc())
                .all()
            )

        opcoes = [
            f"{a.id} - {a.cliente.nome} | {a.cacamba.identificacao} | Até: {a.data_fim.strftime('%d/%m/%Y')}"
            for a in alugueis
        ] or ["Nenhum aluguel ativo disponível"]

        combo.configure(values=opcoes)
        combo.set(opcoes[0])

    atualizar_lista_alugueis()

    # ─── Animação de status ────────────────────────
    def animar_status(msg, cor):
        status_label.configure(text=msg, text_color=cor)
        frame.after(3000, lambda: status_label.configure(text=""))

    # ─── Confirmar Devolução ───────────────────────
    def confirmar_devolucao():
        selecao = combo.get()
        if "Nenhum" in selecao:
            animar_status("❌ Nenhum aluguel selecionado", "#dc2626")
            return

        try:
            aluguel_id = int(selecao.split(" - ")[0])

            with SessionLocal() as db:
                aluguel = db.query(Aluguel).get(aluguel_id)
                aluguel.encerrado = True
                cacamba = db.query(Cacamba).get(aluguel.cacamba_id)
                cacamba.disponivel = True
                db.commit()

            animar_status("✅ Devolução registrada com sucesso!", "#22c55e")
            atualizar_lista_alugueis()

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
            animar_status("❌ Falha ao processar devolução.", "#dc2626")

    # ─── Botão Confirmar ───────────────────────────
    ctk.CTkButton(
        frame,
        text="✅ Confirmar Devolução",
        command=confirmar_devolucao,
        font=("Segoe UI", 14, "bold"),
        width=240,
        height=42,
        fg_color="#2563EB",
        hover_color="#1D4ED8",
        text_color="white",
        corner_radius=12
    ).grid(row=4, column=0, pady=(10, 5))

    # ─── Botão Atualizar ───────────────────────────
    ctk.CTkButton(
        frame,
        text="🔄 Atualizar Lista",
        command=atualizar_lista_alugueis,
        font=("Segoe UI", 12, "bold"),
        width=200,
        height=36,
        fg_color="#9CA3AF",
        hover_color="#6B7280",
        corner_radius=10
    ).grid(row=5, column=0, pady=(0, 30))

    return frame