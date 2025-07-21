import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models import Cliente, Cacamba, Aluguel
from reportlab.pdfgen import canvas
import os


def construir_tela_locacao(pai: ctk.CTkFrame) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(pai, corner_radius=12)
    frame.columnconfigure(0, weight=1)

    # Título
    ctk.CTkLabel(
        frame, text="📝 Nova Locação", font=("Segoe UI", 22, "bold")
    ).grid(row=0, column=0, pady=(20, 10))

    # Formulário
    form = ctk.CTkFrame(frame, fg_color="transparent")
    form.grid(row=1, column=0, padx=20, pady=10)

    entry_cpf = ctk.CTkEntry(form, placeholder_text="📄 CPF/CNPJ do Cliente", width=400)
    entry_nome = ctk.CTkEntry(form, placeholder_text="👤 Nome completo", width=400)
    entry_telefone = ctk.CTkEntry(form, placeholder_text="📞 Telefone", width=400)
    entry_endereco = ctk.CTkEntry(form, placeholder_text="🏠 Endereço", width=400)

    entry_cpf.grid(row=0, column=0, pady=4)
    entry_nome.grid(row=1, column=0, pady=4)
    entry_telefone.grid(row=2, column=0, pady=4)
    entry_endereco.grid(row=3, column=0, pady=4)

    def buscar_cliente():
        cpf = entry_cpf.get().strip()
        if not cpf:
            messagebox.showwarning("Aviso", "Informe o CPF/CNPJ para buscar.")
            return

        with SessionLocal() as db:
            cliente = db.query(Cliente).filter(Cliente.cpf_cnpj == cpf).first()

        if cliente:
            entry_nome.delete(0, "end")
            entry_nome.insert(0, cliente.nome)
            entry_telefone.delete(0, "end")
            entry_telefone.insert(0, cliente.telefone)
            entry_endereco.delete(0, "end")
            entry_endereco.insert(0, cliente.endereco)
            messagebox.showinfo("Cliente encontrado", "Dados preenchidos automaticamente.")
        else:
            messagebox.showinfo("Não encontrado", "Cliente não encontrado. Preencha os dados abaixo.")

    ctk.CTkButton(form, text="🔍 Buscar Cliente", command=buscar_cliente, width=200).grid(row=4, column=0, pady=10)

    # Seleção de Caçamba
    combo_cacamba = ctk.CTkOptionMenu(form, values=["Carregando..."], width=400)
    combo_cacamba.grid(row=5, column=0, pady=10)

    def atualizar_opcoes_cacamba():
        with SessionLocal() as db:
            cacambas = db.query(Cacamba).filter_by(disponivel=True).all()
        opcoes = [f"{c.id} - {c.identificacao}" for c in cacambas]
        combo_cacamba.configure(values=opcoes if opcoes else ["Nenhuma disponível"])
        combo_cacamba.set("Selecione a caçamba" if opcoes else "Nenhuma disponível")

    atualizar_opcoes_cacamba()

    entry_data_fim = ctk.CTkEntry(form, placeholder_text="📅 Data de Devolução (dd/mm/aaaa)", width=400)
    entry_data_fim.grid(row=6, column=0, pady=4)

    def gerar_recibo_pdf(cliente, aluguel, cacamba) -> str:
        recibo_dir = os.path.join(os.getcwd(), "recibos")
        os.makedirs(recibo_dir, exist_ok=True)
        nome_formatado = cliente.nome.strip().lower().replace(" ", "-")
        caminho = os.path.join(recibo_dir, f"recibo_{nome_formatado}_{aluguel.id}.pdf")
        c = canvas.Canvas(caminho)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 800, "RECIBO DE LOCAÇÃO DE CAÇAMBA")
        c.setFont("Helvetica", 12)
        c.drawString(50, 760, f"Cliente: {cliente.nome}")
        c.drawString(50, 740, f"CPF/CNPJ: {cliente.cpf_cnpj}")
        c.drawString(50, 720, f"Telefone: {cliente.telefone}")
        c.drawString(50, 700, f"Endereço: {cliente.endereco}")
        c.drawString(50, 680, f"Caçamba: {cacamba.identificacao}")
        c.drawString(50, 660, f"Início: {aluguel.data_inicio.strftime('%d/%m/%Y')}")
        c.drawString(50, 640, f"Devolução: {aluguel.data_fim.strftime('%d/%m/%Y')}")
        c.drawString(50, 620, f"ID do Aluguel: {aluguel.id}")
        c.drawString(50, 580, "Assinatura: ____________________________")
        c.drawString(50, 560, "Data: ____/____/______")
        c.save()
        return caminho

    def confirmar_locacao():
        cpf = entry_cpf.get().strip()
        nome = entry_nome.get().strip()
        telefone = entry_telefone.get().strip()
        endereco = entry_endereco.get().strip()
        cacamba_valor = combo_cacamba.get()
        cacamba_id = cacamba_valor.split(" - ")[0] if " - " in cacamba_valor else None
        data_fim_str = entry_data_fim.get().strip()

        if not (cpf and nome and telefone and endereco and cacamba_id and data_fim_str):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Data de devolução inválida.")
            return

        try:
            with SessionLocal() as db:
                cliente = db.query(Cliente).filter(Cliente.cpf_cnpj == cpf).first()
                if not cliente:
                    cliente = Cliente(nome=nome, cpf_cnpj=cpf, telefone=telefone, endereco=endereco)
                    db.add(cliente)
                    db.flush()

                aluguel = Aluguel(cliente_id=cliente.id, cacamba_id=int(cacamba_id), data_fim=data_fim, encerrado=False)
                db.add(aluguel)

                cacamba = db.query(Cacamba).filter_by(id=int(cacamba_id)).first()
                cacamba.disponivel = False

                db.commit()

                recibo_path = gerar_recibo_pdf(cliente, aluguel, cacamba)
                messagebox.showinfo("Sucesso", f"✅ Locação registrada com sucesso!\n📄 Recibo salvo em:\n{recibo_path}")

                entry_cpf.delete(0, "end")
                entry_nome.delete(0, "end")
                entry_telefone.delete(0, "end")
                entry_endereco.delete(0, "end")
                entry_data_fim.delete(0, "end")
                atualizar_opcoes_cacamba()

        except SQLAlchemyError as e:
            messagebox.showerror("Erro", f"Erro no banco de dados:\n{e}")

    ctk.CTkButton(
        form,
        text="✅ Confirmar Aluguel",
        command=confirmar_locacao,
        width=250
    ).grid(row=7, column=0, pady=20)

    return frame
