# ═══════════════════════════════════════════════════════════════════════════════
# CONSULTA DE CLIENTES - INTERFACE VISUAL COM CARDS INTERATIVOS
# ═══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from app.database import SessionLocal
from app.models import Cliente, Aluguel


def construir_tela_consulta_clientes(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame_principal = ctk.CTkFrame(pai, corner_radius=12)

    # ─── Título ─────────────────────────────────────────────────────────
    ctk.CTkLabel(
        frame_principal,
        text="📋 Consulta de Clientes",
        font=("Segoe UI", 24, "bold")
    ).pack(pady=20)

    # ─── Área principal (lado a lado) ──────────────────────────────────
    conteudo = ctk.CTkFrame(frame_principal)
    conteudo.pack(padx=10, pady=10, fill="both", expand=True)

    # ═══════════════════════════════════════════════════════════════════
    # COLUNA 1 — Lista de Clientes com botões estilizados
    # ═══════════════════════════════════════════════════════════════════
    coluna_esquerda = ctk.CTkFrame(conteudo)
    coluna_esquerda.pack(side="left", fill="y", padx=(0, 15))

    ctk.CTkLabel(
        coluna_esquerda,
        text="👥 Clientes",
        font=("Segoe UI", 18, "bold")
    ).pack(pady=(0, 12))

    lista_scroll = ctk.CTkScrollableFrame(coluna_esquerda, width=300, height=450, corner_radius=12)
    lista_scroll.pack(fill="y", expand=True)

    # ═══════════════════════════════════════════════════════════════════
    # COLUNA 2 — Detalhes do Cliente
    # ═══════════════════════════════════════════════════════════════════
    coluna_direita = ctk.CTkFrame(conteudo)
    coluna_direita.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(
        coluna_direita,
        text="📑 Detalhes do Cliente",
        font=("Segoe UI", 18, "bold")
    ).pack(pady=(0, 12))

    texto_detalhes = ctk.CTkTextbox(coluna_direita, font=("Segoe UI", 13))
    texto_detalhes.pack(padx=10, pady=5, fill="both", expand=True)
    texto_detalhes.configure(state="disabled")

    # ═══════════════════════════════════════════════════════════════════
    # EVENTO: Exibir detalhes ao clicar
    # ═══════════════════════════════════════════════════════════════════
    def exibir_detalhes(cliente_id: int):
        with SessionLocal() as db:
            cliente = db.query(Cliente).filter_by(id=cliente_id).first()
            alugueis = db.query(Aluguel).filter_by(cliente_id=cliente_id).order_by(
                Aluguel.data_inicio.desc()
            ).all()

        texto_detalhes.configure(state="normal")
        texto_detalhes.delete("1.0", "end")

        if not cliente:
            texto_detalhes.insert("end", "Cliente não encontrado.")
        else:
            texto_detalhes.insert("end", f"🧾 Nome: {cliente.nome}\n")
            texto_detalhes.insert("end", f"📄 CPF/CNPJ: {cliente.cpf_cnpj}\n")
            texto_detalhes.insert("end", f"📞 Telefone: {cliente.telefone}\n")
            texto_detalhes.insert("end", f"🏠 Endereço: {cliente.endereco}\n\n")
            texto_detalhes.insert("end", "📜 Histórico de Locações:\n")

            if not alugueis:
                texto_detalhes.insert("end", "Nenhuma locação encontrada.\n")
            else:
                for aluguel in alugueis:
                    status = "Encerrado ✅" if aluguel.encerrado else "Ativo 🔄"
                    data_ini = aluguel.data_inicio.strftime("%d/%m/%Y")
                    data_fim = aluguel.data_fim.strftime("%d/%m/%Y")
                    texto_detalhes.insert("end", f"\n🔹 Caçamba: {aluguel.cacamba.identificacao}\n")
                    texto_detalhes.insert("end", f"     Início: {data_ini} | Fim: {data_fim} | Status: {status}\n")

        texto_detalhes.configure(state="disabled")

    # ═══════════════════════════════════════════════════════════════════
    # CARREGAMENTO DOS CLIENTES — Botões estilo card
    # ═══════════════════════════════════════════════════════════════════
    with SessionLocal() as db:
        clientes = db.query(Cliente).order_by(Cliente.nome.asc()).all()

    if not clientes:
        ctk.CTkLabel(lista_scroll, text="Nenhum cliente cadastrado.").pack(pady=10)
    else:
        for cliente in clientes:
            texto = f"👤 {cliente.nome}"
            botao = ctk.CTkButton(
                lista_scroll,
                text=texto,
                width=280,
                height=45,
                font=("Segoe UI", 14, "bold"),
                fg_color="#4F46E5",      # Roxo moderno
                hover_color="#4338CA",   # Tom mais escuro no hover
                text_color="white",
                corner_radius=12,
                anchor="w",
                command=lambda cid=cliente.id: exibir_detalhes(cid)
            )
            botao.pack(pady=6, padx=10)

    return frame_principal
