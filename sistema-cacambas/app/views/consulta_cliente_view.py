import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models import Cliente, Aluguel

# Helpers de formatação
def fmt_brl(v):
    try:
        return ("R$ " + f"{float(v):,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "Não informado"

def fmt_data(d):
    try:
        return d.strftime("%d/%m/%Y")
    except Exception:
        return "—"

def construir_tela_consulta_clientes(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame_principal = ctk.CTkFrame(pai, corner_radius=12)
    frame_principal.grid_columnconfigure(0, weight=1)
    frame_principal.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(
        frame_principal,
        text="📋 Consulta de Clientes",
        font=("Segoe UI", 24, "bold")
    ).grid(row=0, column=0, pady=20)

    # ===== Layout base (duas colunas) =====
    conteudo = ctk.CTkFrame(frame_principal)
    conteudo.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    conteudo.grid_columnconfigure(0, weight=0)  # esquerda (lista)
    conteudo.grid_columnconfigure(1, weight=1)  # direita (detalhes + tabela)
    conteudo.grid_rowconfigure(0, weight=1)

    # ===== Coluna Esquerda: busca e lista de clientes =====
    coluna_esquerda = ctk.CTkFrame(conteudo)
    coluna_esquerda.grid(row=0, column=0, sticky="ns", padx=(0, 15))
    coluna_esquerda.grid_rowconfigure(2, weight=1)

    ctk.CTkLabel(
        coluna_esquerda, text="👥 Clientes", font=("Segoe UI", 18, "bold")
    ).grid(row=0, column=0, pady=(0, 12), sticky="w")

    campo_busca = ctk.CTkEntry(
        coluna_esquerda, placeholder_text="Buscar por nome ou CPF/CNPJ", width=280
    )
    campo_busca.grid(row=1, column=0, padx=10, pady=(0, 5))

    lista_scroll = ctk.CTkScrollableFrame(
        coluna_esquerda, width=300, height=450, corner_radius=12
    )
    lista_scroll.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="nsew")

    def criar_callback(cliente_id: int):
        return lambda: exibir_detalhes(cliente_id)

    def buscar_clientes():
        termo = campo_busca.get().strip().lower()
        for w in lista_scroll.winfo_children():
            w.destroy()
        with SessionLocal() as db:
            clientes = (
                db.query(Cliente)
                .filter(
                    (Cliente.nome.ilike(f"%{termo}%"))
                    | (Cliente.cpf_cnpj.ilike(f"%{termo}%"))
                )
                .order_by(Cliente.nome.asc())
                .all()
            )
        if not clientes:
            ctk.CTkLabel(lista_scroll, text="Nenhum cliente encontrado.").pack(pady=10)
        else:
            for cliente in clientes:
                ctk.CTkButton(
                    lista_scroll,
                    text=f"👤 {cliente.nome}",
                    width=280,
                    height=45,
                    font=("Segoe UI", 14, "bold"),
                    fg_color="#6366F1",
                    hover_color="#4F46E5",
                    text_color="white",
                    corner_radius=10,
                    anchor="w",
                    command=criar_callback(cliente.id),
                ).pack(pady=5, padx=10)

    ctk.CTkButton(
        coluna_esquerda,
        text="Pesquisar",
        command=buscar_clientes,
        width=280,
        fg_color="#0EA5E9",
        hover_color="#0284C7",
        font=("Segoe UI", 13, "bold"),
    ).grid(row=3, column=0, pady=(10, 5), padx=10)

    ctk.CTkButton(
        coluna_esquerda,
        text="🔄 Atualizar Lista",
        command=lambda: recarregar_clientes(),
        width=280,
        fg_color="#10B981",
        hover_color="#059669",
        font=("Segoe UI", 13, "bold"),
    ).grid(row=4, column=0, pady=(0, 15), padx=10)

    # Enter na busca
    campo_busca.bind("<Return>", lambda e: buscar_clientes())

    # ===== Coluna Direita: detalhes (topo) e tabela (baixo) =====
    coluna_direita = ctk.CTkFrame(conteudo)
    coluna_direita.grid(row=0, column=1, sticky="nsew")
    coluna_direita.grid_columnconfigure(0, weight=1)
    # linhas: 0 = detalhes, 1 = separador, 2 = header hist., 3 = filtros, 4 = tabela, 5 = botoes ação
    coluna_direita.grid_rowconfigure(4, weight=1)

    # ----- Detalhes do Cliente (separado) -----
    ctk.CTkLabel(
        coluna_direita, text="📑 Dados do Cliente", font=("Segoe UI", 18, "bold")
    ).grid(row=0, column=0, pady=(0, 8), sticky="w", padx=4)

    dados_frame = ctk.CTkFrame(coluna_direita, corner_radius=8)
    dados_frame.grid(row=1, column=0, sticky="ew", padx=6)
    for c in range(4):
        dados_frame.grid_columnconfigure(c, weight=1)

    lbl_nome_val = ctk.CTkLabel(dados_frame, text="—", font=("Segoe UI", 14))
    lbl_doc_val = ctk.CTkLabel(dados_frame, text="—", font=("Segoe UI", 14))
    lbl_tel_val = ctk.CTkLabel(dados_frame, text="—", font=("Segoe UI", 14))
    lbl_end_val = ctk.CTkLabel(dados_frame, text="—", font=("Segoe UI", 14), wraplength=480, justify="left")

    ctk.CTkLabel(dados_frame, text="🧾 Nome:", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 0))
    lbl_nome_val.grid(row=0, column=1, sticky="w", padx=8, pady=(8, 0))

    ctk.CTkLabel(dados_frame, text="📄 CPF/CNPJ:", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, sticky="w", padx=8)
    lbl_doc_val.grid(row=1, column=1, sticky="w", padx=8)

    ctk.CTkLabel(dados_frame, text="📞 Telefone:", font=("Segoe UI", 14, "bold")).grid(row=0, column=2, sticky="w", padx=8, pady=(8, 0))
    lbl_tel_val.grid(row=0, column=3, sticky="w", padx=8, pady=(8, 0))

    ctk.CTkLabel(dados_frame, text="🏠 Endereço:", font=("Segoe UI", 14, "bold")).grid(row=1, column=2, sticky="w", padx=8)
    lbl_end_val.grid(row=1, column=3, sticky="w", padx=8)

    # ----- Título do Histórico -----
    ctk.CTkLabel(
        coluna_direita, text="📜 Histórico de Locações", font=("Segoe UI", 18, "bold")
    ).grid(row=2, column=0, pady=(14, 6), sticky="w", padx=4)

    # ----- Filtro por Endereço -----
    filtro_frame = ctk.CTkFrame(coluna_direita, corner_radius=8)
    filtro_frame.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 4))
    filtro_frame.grid_columnconfigure(0, weight=1)

    entry_busca_end = ctk.CTkEntry(
        filtro_frame, placeholder_text="Pesquisar locação por endereço (ex.: Rua, nº, bairro)"
    )
    entry_busca_end.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

    ctk.CTkButton(
        filtro_frame, text="🔎 Buscar", width=120,
        command=lambda: carregar_historico(cliente_selecionado["id"], entry_busca_end.get().strip())
    ).grid(row=0, column=1, padx=8, pady=8)

    entry_busca_end.bind("<Return>", lambda e: carregar_historico(cliente_selecionado["id"], entry_busca_end.get().strip()))

    # ----- Tabela (scrollable) -----
    tabela_scroll = ctk.CTkScrollableFrame(coluna_direita, corner_radius=8)
    tabela_scroll.grid(row=4, column=0, padx=6, pady=(4, 10), sticky="nsew")
    tabela_scroll.grid_columnconfigure(0, weight=1)

    # Header da tabela
    header = ctk.CTkFrame(tabela_scroll, fg_color="#111827", corner_radius=6)
    header.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
    for i in range(8):
        header.grid_columnconfigure(i, weight=[0,0,0,0,0,0,0,1][i])  # última coluna (Endereço) expande

    def h(lbl, col, w=None):
        c = ctk.CTkLabel(header, text=lbl, font=("Segoe UI", 13, "bold"), text_color="white")
        c.grid(row=0, column=col, padx=6, pady=6, sticky="w")
        if w:
            c.configure(width=w)
        return c

    h("ID", 0)
    h("Caçamba", 1)
    h("Início", 2)
    h("Fim", 3)
    h("Valor", 4)
    h("Pagamento", 5)
    h("Status", 6)
    h("Endereço", 7)

    # Container de linhas
    corpo = ctk.CTkFrame(tabela_scroll, corner_radius=6)
    corpo.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
    corpo.grid_columnconfigure(7, weight=1)

    # Estado atual
    cliente_selecionado = {"id": None}

    # ----- Funções -----
    def limpar_tabela():
        for w in corpo.winfo_children():
            w.destroy()

    def desenhar_linhas(alugueis):
        limpar_tabela()
        if not alugueis:
            ctk.CTkLabel(corpo, text="Nenhuma locação encontrada.").grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for i, aluguel in enumerate(alugueis):
            linha = ctk.CTkFrame(corpo, fg_color="#F3F4F6", corner_radius=6)
            linha.grid(row=i, column=0, columnspan=8, sticky="ew", padx=4, pady=3)
            for c in range(8):
                linha.grid_columnconfigure(c, weight=0)
            linha.grid_columnconfigure(7, weight=1)

            status = "Encerrado ✅" if getattr(aluguel, "encerrado", False) else "Ativo 🔄"
            pagamento = "Pago 💰" if getattr(aluguel, "pago", False) else "Pendente ⏳"

            valores = [
                str(aluguel.id),
                getattr(getattr(aluguel, "cacamba", None), "identificacao", "—"),
                fmt_data(aluguel.data_inicio),
                fmt_data(aluguel.data_fim),
                fmt_brl(aluguel.valor) if aluguel.valor is not None else "Não informado",
                pagamento,
                status,
                aluguel.endereco_obra or "Não informado",
            ]

            for col, texto in enumerate(valores):
                ctk.CTkLabel(linha, text=texto, font=("Segoe UI", 13), anchor="w", justify="left").grid(
                    row=0, column=col, padx=6, pady=6, sticky="w"
                )

    def carregar_historico(cliente_id: int | None, termo_endereco: str = ""):
        if not cliente_id:
            limpar_tabela()
            return
        try:
            with SessionLocal() as db:
                q = (
                    db.query(Aluguel)
                    .options(joinedload(Aluguel.cacamba))
                    .filter(Aluguel.cliente_id == cliente_id)
                )
                if termo_endereco:
                    q = q.filter(Aluguel.endereco_obra.ilike(f"%{termo_endereco}%"))
                alugueis = q.order_by(Aluguel.data_inicio.desc()).all()
            desenhar_linhas(alugueis)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar histórico:\n{e}")
            limpar_tabela()

    def exibir_detalhes(cliente_id: int):
        cliente_selecionado["id"] = cliente_id
        entry_busca_end.delete(0, "end")  # limpa filtro ao trocar cliente
        with SessionLocal() as db:
            cliente = db.query(Cliente).filter_by(id=cliente_id).first()

        # Preenche dados
        if not cliente:
            lbl_nome_val.configure(text="—")
            lbl_doc_val.configure(text="—")
            lbl_tel_val.configure(text="—")
            lbl_end_val.configure(text="—")
            limpar_tabela()
            return

        lbl_nome_val.configure(text=cliente.nome or "—")
        lbl_doc_val.configure(text=cliente.cpf_cnpj or "—")
        lbl_tel_val.configure(text=cliente.telefone or "—")
        lbl_end_val.configure(text=cliente.endereco or "—")

        # Carrega histórico padrão (sem filtro)
        carregar_historico(cliente_id)

    def atualizar_cliente():
        cid = cliente_selecionado.get("id")
        if not cid:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro.")
            return
        with SessionLocal() as db:
            cliente = db.query(Cliente).filter_by(id=cid).first()
            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado.")
                return

        janela = ctk.CTkToplevel()
        janela.title("Atualizar Cliente")
        janela.geometry("400x360")

        ctk.CTkLabel(janela, text="Nome:", font=("Segoe UI", 13)).pack(pady=(15, 0))
        entry_nome = ctk.CTkEntry(janela, width=350)
        entry_nome.insert(0, cliente.nome or "")
        entry_nome.pack()

        ctk.CTkLabel(janela, text="CPF/CNPJ:", font=("Segoe UI", 13)).pack(pady=(10, 0))
        entry_doc = ctk.CTkEntry(janela, width=350)
        entry_doc.insert(0, cliente.cpf_cnpj or "")
        entry_doc.pack()

        ctk.CTkLabel(janela, text="Telefone:", font=("Segoe UI", 13)).pack(pady=(10, 0))
        entry_tel = ctk.CTkEntry(janela, width=350)
        entry_tel.insert(0, cliente.telefone or "")
        entry_tel.pack()

        ctk.CTkLabel(janela, text="Endereço:", font=("Segoe UI", 13)).pack(pady=(10, 0))
        entry_end = ctk.CTkEntry(janela, width=350)
        entry_end.insert(0, cliente.endereco or "")
        entry_end.pack()

        def salvar_alteracoes():
            with SessionLocal() as db:
                cli = db.query(Cliente).filter_by(id=cid).first()
                if not cli:
                    messagebox.showerror("Erro", "Cliente não encontrado.")
                    return
                cli.nome = entry_nome.get().strip()
                cli.cpf_cnpj = entry_doc.get().strip()
                cli.telefone = entry_tel.get().strip()
                cli.endereco = entry_end.get().strip()
                db.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso.")
            janela.destroy()
            recarregar_clientes()
            exibir_detalhes(cid)

        ctk.CTkButton(janela, text="💾 Salvar Alterações", command=salvar_alteracoes, width=200).pack(pady=20)

    def excluir_cliente():
        cid = cliente_selecionado.get("id")
        if not cid:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir este cliente?"):
            return

        with SessionLocal() as db:
            cliente = db.query(Cliente).filter_by(id=cid).first()
            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado.")
                return
            alugueis = db.query(Aluguel).filter_by(cliente_id=cid).count()
            if alugueis > 0:
                messagebox.showerror("Erro", "Este cliente possui aluguéis registrados e não pode ser excluído.")
                return
            db.delete(cliente)
            db.commit()

        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")
        recarregar_clientes()
        # limpa painel direito
        lbl_nome_val.configure(text="—")
        lbl_doc_val.configure(text="—")
        lbl_tel_val.configure(text="—")
        lbl_end_val.configure(text="—")
        limpar_tabela()

    def recarregar_clientes():
        for w in lista_scroll.winfo_children():
            w.destroy()
        with SessionLocal() as db:
            clientes = db.query(Cliente).order_by(Cliente.nome.asc()).all()
        if not clientes:
            ctk.CTkLabel(lista_scroll, text="Nenhum cliente cadastrado.").pack(pady=10)
        else:
            for cliente in clientes:
                ctk.CTkButton(
                    lista_scroll,
                    text=f"👤 {cliente.nome}",
                    width=280,
                    height=45,
                    font=("Segoe UI", 14, "bold"),
                    fg_color="#6366F1",
                    hover_color="#4F46E5",
                    text_color="white",
                    corner_radius=10,
                    anchor="w",
                    command=criar_callback(cliente.id),
                ).pack(pady=5, padx=10)

    # Botões de ação (direita)
    botoes_acao = ctk.CTkFrame(coluna_direita)
    botoes_acao.grid(row=5, column=0, pady=10)
    ctk.CTkButton(
        botoes_acao, text="✏️ Atualizar Cliente", command=atualizar_cliente,
        fg_color="#3B82F6", hover_color="#2563EB", width=180, height=36
    ).pack(side="left", padx=10)
    ctk.CTkButton(
        botoes_acao, text="🗑️ Excluir Cliente", command=excluir_cliente,
        fg_color="#EF4444", hover_color="#DC2626", width=180, height=36
    ).pack(side="right", padx=10)

    # Inicializa
    recarregar_clientes()
    return frame_principal
