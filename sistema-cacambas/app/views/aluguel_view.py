# ═══════════════════════════════════════════════════════════════════════════════
# TELA: NOVO ALUGUEL (com sugestões de endereços anteriores por cliente)
# ═══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from app.database import SessionLocal
from app.models import Cliente, Cacamba, Aluguel

# ➜ ADICIONE ESTA LINHA:
from sqlalchemy.orm import joinedload


def construir_tela_aluguel(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=15)
    frame.grid_rowconfigure(tuple(range(40)), weight=0)
    frame.grid_columnconfigure(0, weight=1)

    # Título
    ctk.CTkLabel(
        frame,
        text="📄 Registrar Novo Aluguel",
        font=("Segoe UI", 22, "bold")
    ).grid(row=0, column=0, pady=(20, 10))

    # ----------------- Cliente -----------------
    ctk.CTkLabel(frame, text="👤 Cliente:", font=("Segoe UI", 14)).grid(row=1, column=0, pady=(5, 0))

    # callback quando selecionar um cliente
    def on_cliente_change(valor_escolhido: str):
        cliente_id = _option_to_id(valor_escolhido)
        carregar_sugestoes_enderecos(cliente_id)

    combo_cliente = ctk.CTkOptionMenu(frame, width=350, values=[], command=on_cliente_change)
    combo_cliente.grid(row=2, column=0, pady=5)

    # ----------------- Caçamba -----------------
    ctk.CTkLabel(frame, text="🚛 Caçamba disponível:", font=("Segoe UI", 14)).grid(row=3, column=0, pady=(10, 0))
    combo_cacamba = ctk.CTkOptionMenu(frame, width=350, values=[])
    combo_cacamba.grid(row=4, column=0, pady=5)

    # ----------------- Datas -----------------
    ctk.CTkLabel(frame, text="📅 Data de Início (dd/mm/aaaa):", font=("Segoe UI", 14)).grid(row=5, column=0, pady=(10, 0))
    entry_inicio = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 10/07/2025")
    entry_inicio.grid(row=6, column=0, pady=5)

    ctk.CTkLabel(frame, text="📅 Data de Fim (dd/mm/aaaa):", font=("Segoe UI", 14)).grid(row=7, column=0, pady=(10, 0))
    entry_fim = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 15/07/2025")
    entry_fim.grid(row=8, column=0, pady=5)

    # ----------------- Endereço -----------------
    ctk.CTkLabel(frame, text="📍 Endereço da Obra:", font=("Segoe UI", 14)).grid(row=9, column=0, pady=(10, 0))
    entry_endereco = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: Rua A, nº 123 - Bairro X")
    entry_endereco.grid(row=10, column=0, pady=5)

    # Label e OptionMenu de sugestões (inicialmente escondidos)
    label_sug = ctk.CTkLabel(frame, text="Endereços anteriores (opcional):", font=("Segoe UI", 12))
    combo_sugestoes = ctk.CTkOptionMenu(frame, width=350, values=[])

    def on_sugestao_select(valor: str):
        # Ao escolher uma sugestão, preenche o entry
        if valor and not valor.startswith("—"):
            entry_endereco.delete(0, "end")
            entry_endereco.insert(0, valor)

    combo_sugestoes.configure(command=on_sugestao_select)

    def mostrar_sugestoes(enderecos: list[str]):
        """Mostra/atualiza o seletor de sugestões ou esconde se vazio."""
        if enderecos:
            combo_sugestoes.configure(values=enderecos)
            # placeholder visual
            try:
                combo_sugestoes.set("— selecionar endereço anterior —")
            except Exception:
                pass
            # grid apenas quando houver o que mostrar
            label_sug.grid(row=11, column=0, pady=(2, 0))
            combo_sugestoes.grid(row=12, column=0, pady=5)
        else:
            # esconder se não houver sugestões
            try:
                label_sug.grid_remove()
                combo_sugestoes.grid_remove()
            except Exception:
                pass

    def carregar_sugestoes_enderecos(cliente_id: int | None):
        """Busca no banco os endereços já usados por esse cliente (sem duplicar, mais recentes primeiro)."""
        if not cliente_id:
            mostrar_sugestoes([])
            return

        try:
            with SessionLocal() as db:
                registros = (
                    db.query(Aluguel.endereco_obra)
                      .filter(Aluguel.cliente_id == cliente_id)
                      .order_by(Aluguel.id.desc())
                      .all()
                )
            # flatten + únicos preservando ordem
            vistos = set()
            enderecos_unicos = []
            for (end,) in registros:
                if end and end not in vistos:
                    vistos.add(end)
                    enderecos_unicos.append(end)
            # limita p/ não ficar gigante
            mostrar_sugestoes(enderecos_unicos[:10])
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar endereços anteriores:\n{e}")
            mostrar_sugestoes([])

    # ----------------- Valor -----------------
    ctk.CTkLabel(frame, text="💲 Valor do aluguel (R$):", font=("Segoe UI", 14)).grid(row=13, column=0, pady=(10, 0))
    entry_valor = ctk.CTkEntry(frame, width=350, placeholder_text="Ex: 450.00")
    entry_valor.grid(row=14, column=0, pady=5)

    # ----------------- Atualizar listas (clientes/caçambas) -----------------
    def _option_to_id(valor: str) -> int | None:
        if not valor or "Nenhum" in valor or "Nenhuma" in valor:
            return None
        try:
            return int(valor.split(" - ", 1)[0])
        except Exception:
            return None

    def atualizar_listas():
        with SessionLocal() as db:
            clientes = db.query(Cliente).all()
            cacambas = db.query(Cacamba).filter_by(disponivel=True).all()

        valores_clientes = [f"{c.id} - {c.nome}" for c in clientes] or ["Nenhum cliente encontrado"]
        valores_cacambas = [f"{c.id} - {c.identificacao}" for c in cacambas] or ["Nenhuma disponível"]

        combo_cliente.configure(values=valores_clientes)
        combo_cacamba.configure(values=valores_cacambas)

        combo_cliente.set(valores_clientes[0] if valores_clientes else "")
        combo_cacamba.set(valores_cacambas[0] if valores_cacambas else "")

        # carrega sugestões para o cliente atualmente selecionado
        on_cliente_change(combo_cliente.get())

    atualizar_listas()

    # ----------------- Salvar -----------------
    def salvar_aluguel():
        try:
            cliente_id = _option_to_id(combo_cliente.get())
            cacamba_id = _option_to_id(combo_cacamba.get())
            if not cliente_id:
                messagebox.showwarning("Atenção", "Selecione um cliente válido.")
                return
            if not cacamba_id:
                messagebox.showwarning("Atenção", "Selecione uma caçamba disponível.")
                return

            data_inicio = datetime.strptime(entry_inicio.get().strip(), "%d/%m/%Y")
            data_fim = datetime.strptime(entry_fim.get().strip(), "%d/%m/%Y")
            if data_fim <= data_inicio:
                messagebox.showerror("Erro", "A data de fim deve ser posterior à data de início.")
                return

            endereco_obra = entry_endereco.get().strip()
            if not endereco_obra:
                messagebox.showerror("Erro", "Informe o endereço da obra.")
                return

            valor = float(entry_valor.get().replace(",", "."))

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
                cacamba = db.get(Cacamba, cacamba_id)
                cacamba.disponivel = False
                db.commit()

            # Limpa
            combo_cacamba.set("")
            entry_inicio.delete(0, "end")
            entry_fim.delete(0, "end")
            entry_valor.delete(0, "end")
            entry_endereco.delete(0, "end")

            # Atualiza listas e sugestões (endereço recém-registrado passa a aparecer)
            atualizar_listas()
            messagebox.showinfo("Sucesso", "Aluguel registrado com sucesso!")

        except ValueError:
            messagebox.showerror("Erro", "Verifique as datas e o valor do aluguel.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao registrar aluguel:\n{e}")

    # Botões
    ctk.CTkButton(
        frame,
        text="💾 Salvar Aluguel",
        command=salvar_aluguel,
        fg_color="#228B22",
        hover_color="#1E6F1E",
        font=("Segoe UI", 14, "bold"),
        width=200,
        height=40
    ).grid(row=15, column=0, pady=(20, 5))

    ctk.CTkButton(
        frame,
        text="🔄 Atualizar Caçambas",
        command=atualizar_listas,
        fg_color="#1E90FF",
        hover_color="#1C86EE",
        font=("Segoe UI", 12, "bold"),
        width=200,
        height=30
    ).grid(row=16, column=0, pady=(5, 30))

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