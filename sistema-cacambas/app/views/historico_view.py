import customtkinter as ctk
from tkinter import messagebox
import os
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models import Aluguel
from reportlab.pdfgen import canvas

def construir_tela_historico(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=12)

    # Título
    ctk.CTkLabel(
        frame,
        text="📜 Histórico de Aluguéis",
        font=("Segoe UI", 26, "bold"),
        text_color="#111827"
    ).pack(pady=(20, 10))

    # Filtro
    filtro_var = ctk.StringVar(value="Todos")
    filtro_frame = ctk.CTkFrame(frame, fg_color="transparent")
    filtro_frame.pack(pady=(0, 10))

    ctk.CTkLabel(filtro_frame, text="🔎 Status:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 8))

    # Frame dinâmico da tabela
    tabela_frame = ctk.CTkFrame(frame, fg_color="transparent")
    tabela_frame.pack(fill="both", expand=True)

    def alternar_status_pagamento(aluguel_id: int):
        from app.database import SessionLocal
        from app.models import Aluguel
        from tkinter import messagebox

        with SessionLocal() as db:
            aluguel = db.query(Aluguel).get(aluguel_id)
            if aluguel:
                aluguel.pago = not aluguel.pago
                db.commit()
                status = "Pago" if aluguel.pago else "Não Pago"
                messagebox.showinfo("Sucesso", f"Status de pagamento atualizado para: {status}")
    
    def exibir_tabela_alugueis_custom(filtro_status: str = "Todos"):
        for widget in tabela_frame.winfo_children():
            widget.destroy()

        with SessionLocal() as db:
            query = db.query(Aluguel).options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba))

            if filtro_status == "Ativos":
                query = query.filter(Aluguel.encerrado == False)
            elif filtro_status == "Encerrados":
                query = query.filter(Aluguel.encerrado == True)

            alugueis = query.order_by(Aluguel.data_inicio.desc()).all()

        cabecalho = ctk.CTkFrame(tabela_frame, fg_color="#dddddd")
        cabecalho.pack(fill="x", padx=10)
        colunas = ["ID", "Cliente", "Caçamba", "Início", "Fim", "Status","Endereço da Obra","Pago?", "Ação"]
        larguras = [40, 160, 80, 90, 90, 90, 240, 80, 80]

        for i, (titulo, largura) in enumerate(zip(colunas, larguras)):
            label = ctk.CTkLabel(cabecalho, text=titulo, width=largura, anchor="center", font=("Segoe UI", 12, "bold"))
            label.grid(row=0, column=i, padx=2, pady=4)

        corpo = ctk.CTkScrollableFrame(tabela_frame, height=320)
        corpo.pack(fill="both", expand=True, padx=10, pady=5)

        if not alugueis:
            ctk.CTkLabel(corpo, text="⚠️ Nenhum aluguel encontrado.", font=("Segoe UI", 13)).pack(pady=20)
            return

        for idx, aluguel in enumerate(alugueis):
            pago = "✅" if aluguel.pago else "❌"
            btn_texto = "↩️ Estornar" if aluguel.pago else "💰 Marcar"
            btn_cor = "#F59E0B" if aluguel.pago else "#10B981"
            btn_hover = "#D97706" if aluguel.pago else "#059669"
            dados = [
                str(aluguel.id),
                aluguel.cliente.nome if aluguel.cliente else "?",
                aluguel.cacamba.identificacao if aluguel.cacamba else "?",
                aluguel.data_inicio.strftime("%d/%m/%Y"),
                aluguel.data_fim.strftime("%d/%m/%Y"),
                "✅ Encerrado" if aluguel.encerrado else "🔄 Ativo",
                aluguel.endereco_obra or "—",
                pago
            ]
            linha = ctk.CTkFrame(corpo, fg_color="#f6f6f6" if idx % 2 == 0 else "#e2e2e2")
            linha.pack(fill="x")

            for i, (valor, largura) in enumerate(zip(dados, larguras)):
                ctk.CTkLabel(linha, text=valor, width=largura, anchor="center", font=("Segoe UI", 12)).grid(row=0, column=i, padx=2, pady=4)
                ctk.CTkButton(
                    linha,
                    text=btn_texto,
                    width=90,
                    height=30,
                    font=("Segoe UI", 12),
                    fg_color=btn_cor,
                    hover_color=btn_hover,
                    command=lambda a_id=aluguel.id:alternar_status_pagamento(a_id)
                ).grid(row=0, column=len(dados), padx=4)
    filtro_menu = ctk.CTkOptionMenu(
        filtro_frame,
        variable=filtro_var,
        values=["Todos", "Ativos", "Encerrados"],
        width=160,
        command=lambda _: exibir_tabela_alugueis_custom(filtro_var.get())
    )
    filtro_menu.pack(side="left")

    # Campo + botão para recibo
    recibo_frame = ctk.CTkFrame(frame, fg_color="transparent")
    recibo_frame.pack(pady=(10, 0))

    ctk.CTkLabel(recibo_frame, text="🎯 Gerar recibo por ID do aluguel:", font=("Segoe UI", 14, "bold")).pack(pady=(5, 8))

    id_entry = ctk.CTkEntry(recibo_frame, width=240, placeholder_text="Digite o ID do aluguel")
    id_entry.pack(pady=5)

    def gerar_recibo_por_id():
        id_str = id_entry.get().strip()
        if not id_str.isdigit():
            messagebox.showerror("Erro", "Informe um ID numérico válido.")
            return

        with SessionLocal() as db:
            aluguel = db.query(Aluguel).options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba)).filter(Aluguel.id == int(id_str)).first()

        if not aluguel:
            messagebox.showerror("Erro", "Aluguel não encontrado.")
            return

        cliente, cacamba = aluguel.cliente, aluguel.cacamba
        nome_formatado = cliente.nome.strip().lower().replace(" ", "-")
        recibo_dir = os.path.join(os.getcwd(), "recibos")
        os.makedirs(recibo_dir, exist_ok=True)

        caminho = os.path.join(recibo_dir, f"recibo_{nome_formatado}_{aluguel.id}.pdf")
        c = canvas.Canvas(caminho)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 800, "RECIBO DE LOCAÇÃO DE CAÇAMBA")
        c.setFont("Helvetica", 12)
        c.drawString(50, 760, f"Cliente: {cliente.nome}")
        c.drawString(50, 740, f"CPF/CNPJ: {cliente.cpf_cnpj}")
        c.drawString(50, 720, f"Telefone: {cliente.telefone}")
        c.drawString(50, 680, f"Endereço da Obra: {aluguel.endereco_obra or '—'}")
        c.drawString(50, 700, f"Endereço: {cliente.endereco}")
        c.drawString(50, 680, f"Caçamba: {cacamba.identificacao}")
        c.drawString(50, 660, f"Início: {aluguel.data_inicio.strftime('%d/%m/%Y')}")
        c.drawString(50, 640, f"Devolução: {aluguel.data_fim.strftime('%d/%m/%Y')}")
        c.drawString(50, 620, f"ID do Aluguel: {aluguel.id}")
        c.drawString(50, 580, "Assinatura: ____________________________")
        c.drawString(50, 560, "Data: ____/____/______")
        c.save()

        messagebox.showinfo("Sucesso", f"📄 Recibo salvo em:\n{caminho}")

    ctk.CTkButton(
        recibo_frame,
        text="🧾 Gerar PDF",
        command=gerar_recibo_por_id,
        width=220,
        height=42,
        font=("Segoe UI", 13, "bold"),
        fg_color="#2563EB",
        hover_color="#1D4ED8",
        text_color="white",
        corner_radius=12
    ).pack(pady=(10, 10))

    ctk.CTkButton(
        recibo_frame,
        text="🔄 Atualizar Histórico",
        command=lambda: exibir_tabela_alugueis_custom(filtro_var.get()),
        width=200,
        height=36,
        font=("Segoe UI", 12, "bold"),
        fg_color="#10B981",
        hover_color="#059669",
        text_color="white",
        corner_radius=12
    ).pack(pady=(0, 20))

    exibir_tabela_alugueis_custom()
    return frame
