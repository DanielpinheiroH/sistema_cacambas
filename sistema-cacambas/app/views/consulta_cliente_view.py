import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models import Cliente, Aluguel


def construir_tela_consulta_clientes(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame_principal = ctk.CTkFrame(pai, corner_radius=12)

    ctk.CTkLabel(frame_principal, text="📋 Consulta de Clientes", font=("Segoe UI", 24, "bold")).pack(pady=20)

    conteudo = ctk.CTkFrame(frame_principal)
    conteudo.pack(padx=10, pady=10, fill="both", expand=True)

    coluna_esquerda = ctk.CTkFrame(conteudo)
    coluna_esquerda.pack(side="left", fill="y", padx=(0, 15))

    ctk.CTkLabel(coluna_esquerda, text="👥 Clientes", font=("Segoe UI", 18, "bold")).pack(pady=(0, 12))
    lista_scroll = ctk.CTkScrollableFrame(coluna_esquerda, width=300, height=450, corner_radius=12)
    lista_scroll.pack(fill="y", expand=True)

    coluna_direita = ctk.CTkFrame(conteudo)
    coluna_direita.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(coluna_direita, text="📑 Detalhes do Cliente", font=("Segoe UI", 18, "bold")).pack(pady=(0, 12))
    texto_detalhes = ctk.CTkTextbox(coluna_direita, font=("Segoe UI", 13))
    texto_detalhes.pack(padx=10, pady=5, fill="both", expand=True)
    texto_detalhes.configure(state="disabled")

    cliente_selecionado = {"id": None}

    def exibir_detalhes(cliente_id: int):
        cliente_selecionado["id"] = cliente_id
        with SessionLocal() as db:
            cliente = db.query(Cliente).filter_by(id=cliente_id).first()
            alugueis = db.query(Aluguel).options(joinedload(Aluguel.cacamba)).filter_by(cliente_id=cliente_id).order_by(Aluguel.data_inicio.desc()).all()

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
                    valor = f"R$ {aluguel.valor:.2f}" if aluguel.valor else "Não informado"
                    status_pagamento = "Pago 💰" if aluguel.pago else "Pendente ⏳"
                    endereco_obra = aluguel.endereco_obra if aluguel.endereco_obra else "Não informado"

                    texto_detalhes.insert("end", f"\n🔹 Aluguel ID: {aluguel.id} | Caçamba: {aluguel.cacamba.identificacao}\n")
                    texto_detalhes.insert("end", f"     Início: {data_ini} | Fim: {data_fim} | Status: {status}\n")
                    texto_detalhes.insert("end", f"     Valor: {valor} | Pagamento: {status_pagamento}\n")
                    texto_detalhes.insert("end", f"     Obra: {endereco_obra}\n")

        texto_detalhes.configure(state="disabled")

    def atualizar_cliente():
        cliente_id = cliente_selecionado.get("id")
        if not cliente_id:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro.")
            return

        with SessionLocal() as db:
            cliente = db.query(Cliente).filter_by(id=cliente_id).first()
            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado.")
                return

        janela = ctk.CTkToplevel()
        janela.title("Atualizar Cliente")
        janela.geometry("400x360")

        ctk.CTkLabel(janela, text="Nome:", font=("Segoe UI", 13)).pack(pady=(15, 0))
        entry_nome = ctk.CTkEntry(janela, width=350)
        entry_nome.insert(0, cliente.nome)
        entry_nome.pack()

        ctk.CTkLabel(janela, text="CPF/CNPJ:", font=("Segoe UI", 13)).pack(pady=(10, 0))
        entry_doc = ctk.CTkEntry(janela, width=350)
        entry_doc.insert(0, cliente.cpf_cnpj)
        entry_doc.pack()

        ctk.CTkLabel(janela, text="Telefone:", font=("Segoe UI", 13)).pack(pady=(10, 0))
        entry_tel = ctk.CTkEntry(janela, width=350)
        entry_tel.insert(0, cliente.telefone)
        entry_tel.pack()

        ctk.CTkLabel(janela, text="Endereço:", font=("Segoe UI", 13)).pack(pady=(10, 0))
        entry_end = ctk.CTkEntry(janela, width=350)
        entry_end.insert(0, cliente.endereco)
        entry_end.pack()

        def salvar_alteracoes():
            with SessionLocal() as db:
                cli = db.query(Cliente).filter_by(id=cliente_id).first()
                cli.nome = entry_nome.get()
                cli.cpf_cnpj = entry_doc.get()
                cli.telefone = entry_tel.get()
                cli.endereco = entry_end.get()
                db.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso.")
            janela.destroy()
            recarregar_clientes()
            exibir_detalhes(cliente_id)

        ctk.CTkButton(janela, text="💾 Salvar Alterações", command=salvar_alteracoes, width=200).pack(pady=20)

    def excluir_cliente():
        cliente_id = cliente_selecionado.get("id")
        if not cliente_id:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro.")
            return

        confirm = messagebox.askyesno("Confirmar", "Deseja realmente excluir este cliente?")
        if not confirm:
            return

        with SessionLocal() as db:
            cliente = db.query(Cliente).filter_by(id=cliente_id).first()
            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado.")
                return
            alugueis = db.query(Aluguel).filter_by(cliente_id=cliente_id).count()
            if alugueis > 0:
                messagebox.showerror("Erro", "Este cliente possui aluguéis registrados e não pode ser excluído.")
                return
            db.delete(cliente)
            db.commit()

        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")
        recarregar_clientes()
        texto_detalhes.configure(state="normal")
        texto_detalhes.delete("1.0", "end")
        texto_detalhes.insert("end", "Selecione um cliente para ver os detalhes.")
        texto_detalhes.configure(state="disabled")

    def criar_callback(cliente_id: int):
        return lambda: exibir_detalhes(cliente_id)

    def recarregar_clientes():
        for widget in lista_scroll.winfo_children():
            widget.destroy()

        with SessionLocal() as db:
            clientes = db.query(Cliente).order_by(Cliente.nome.asc()).all()

        if not clientes:
            ctk.CTkLabel(lista_scroll, text="Nenhum cliente cadastrado.").pack(pady=10)
        else:
            for cliente in clientes:
                texto = f"👤 {cliente.nome}"
                ctk.CTkButton(
                    lista_scroll,
                    text=texto,
                    width=280,
                    height=45,
                    font=("Segoe UI", 14, "bold"),
                    fg_color="#6366F1",
                    hover_color="#4F46E5",
                    text_color="white",
                    corner_radius=10,
                    anchor="w",
                    command=criar_callback(cliente.id)
                ).pack(pady=5, padx=10)

    ctk.CTkButton(
        coluna_esquerda,
        text="🔄 Atualizar Lista",
        command=recarregar_clientes,
        width=280,
        fg_color="#10B981",
        hover_color="#059669",
        font=("Segoe UI", 13, "bold")
    ).pack(pady=(10, 15), padx=10)

    botoes_acao = ctk.CTkFrame(coluna_direita)
    botoes_acao.pack(pady=10)

    ctk.CTkButton(
        botoes_acao, text="✏️ Atualizar Cliente", command=atualizar_cliente,
        fg_color="#3B82F6", hover_color="#2563EB", width=180, height=36
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        botoes_acao, text="🗑️ Excluir Cliente", command=excluir_cliente,
        fg_color="#EF4444", hover_color="#DC2626", width=180, height=36
    ).pack(side="right", padx=10)

    recarregar_clientes()
    return frame_principal
