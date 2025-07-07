import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from app.models import Cliente, Cacamba, Aluguel
from reportlab.pdfgen import canvas
import os

def construir_tela_locacao(pai):
    frame = ctk.CTkFrame(pai, corner_radius=10)
    ctk.CTkLabel(frame, text="Nova Locação", font=("Segoe UI", 20, "bold")).pack(pady=10)

    # CAMPOS DO CLIENTE
    entry_cpf = ctk.CTkEntry(frame, placeholder_text="CPF/CNPJ do Cliente", width=400)
    entry_cpf.pack(pady=5)

    entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome", width=400)
    entry_nome.pack(pady=5)

    entry_telefone = ctk.CTkEntry(frame, placeholder_text="Telefone", width=400)
    entry_telefone.pack(pady=5)

    entry_endereco = ctk.CTkEntry(frame, placeholder_text="Endereço", width=400)
    entry_endereco.pack(pady=5)

    def buscar_cliente():
        cpf = entry_cpf.get().strip()
        if not cpf:
            messagebox.showwarning("Aviso", "Informe o CPF/CNPJ para buscar.")
            return

        db = SessionLocal()
        cliente = db.query(Cliente).filter(Cliente.cpf_cnpj == cpf).first()
        db.close()

        if cliente:
            entry_nome.delete(0, "end")
            entry_nome.insert(0, cliente.nome)
            entry_telefone.delete(0, "end")
            entry_telefone.insert(0, cliente.telefone)
            entry_endereco.delete(0, "end")
            entry_endereco.insert(0, cliente.endereco)
            messagebox.showinfo("Cliente encontrado", "Cliente preenchido automaticamente.")
        else:
            messagebox.showinfo("Não encontrado", "Cliente não encontrado. Preencha os dados abaixo.")

    ctk.CTkButton(frame, text="🔍 Buscar Cliente", command=buscar_cliente).pack(pady=8)

    # CAÇAMBAS DISPONÍVEIS
    def atualizar_opcoes_cacamba():
        db = SessionLocal()
        cacambas = db.query(Cacamba).filter_by(disponivel=True).all()
        db.close()

        opcoes = [f"{c.id} - {c.identificacao}" for c in cacambas]
        if opcoes:
            combo_cacamba.configure(values=opcoes)
            combo_cacamba.set("Selecione a caçamba")
        else:
            combo_cacamba.configure(values=["Nenhuma disponível"])
            combo_cacamba.set("Nenhuma disponível")

    combo_cacamba = ctk.CTkOptionMenu(frame, values=["Carregando..."])
    combo_cacamba.pack(pady=10)
    atualizar_opcoes_cacamba()

    entry_data_fim = ctk.CTkEntry(frame, placeholder_text="Data de Devolução (dd/mm/aaaa)", width=400)
    entry_data_fim.pack(pady=5)

    def gerar_recibo_pdf(cliente, aluguel, cacamba):
        recibo_dir = os.path.join(os.getcwd(), 'recibos')
        os.makedirs(recibo_dir, exist_ok=True)

        nome_formatado = cliente.nome.strip().lower().replace(" ", "-")
        nome_arquivo = f"recibo_{nome_formatado}_{aluguel.id}.pdf"
        caminho = os.path.join(recibo_dir, nome_arquivo)

        c = canvas.Canvas(caminho)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 800, "RECIBO DE LOCAÇÃO DE CAÇAMBA")
        c.setFont("Helvetica", 12)
        c.drawString(50, 760, f"Cliente: {cliente.nome}")
        c.drawString(50, 740, f"CPF/CNPJ: {cliente.cpf_cnpj}")
        c.drawString(50, 720, f"Telefone: {cliente.telefone}")
        c.drawString(50, 700, f"Endereço: {cliente.endereco}")
        c.drawString(50, 680, f"Caçamba: {cacamba.identificacao}")
        c.drawString(50, 660, f"Data de Início: {aluguel.data_inicio.strftime('%d/%m/%Y')}")
        c.drawString(50, 640, f"Data de Devolução: {aluguel.data_fim.strftime('%d/%m/%Y')}")
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
            db = SessionLocal()

            cliente = db.query(Cliente).filter(Cliente.cpf_cnpj == cpf).first()
            if not cliente:
                cliente = Cliente(nome=nome, cpf_cnpj=cpf, telefone=telefone, endereco=endereco)
                db.add(cliente)
                db.flush()

            aluguel = Aluguel(
                cliente_id=cliente.id,
                cacamba_id=int(cacamba_id),
                data_fim=data_fim,
                encerrado=False
            )
            db.add(aluguel)

            cacamba = db.query(Cacamba).filter_by(id=int(cacamba_id)).first()
            cacamba.disponivel = False

            db.commit()

            recibo_path = gerar_recibo_pdf(cliente, aluguel, cacamba)
            messagebox.showinfo("Sucesso", f"Locação registrada!\nRecibo salvo em:\n{recibo_path}")

            # Limpa os campos
            entry_cpf.delete(0, "end")
            entry_nome.delete(0, "end")
            entry_telefone.delete(0, "end")
            entry_endereco.delete(0, "end")
            entry_data_fim.delete(0, "end")
            atualizar_opcoes_cacamba()

        except SQLAlchemyError as e:
            db.rollback()
            messagebox.showerror("Erro", f"Erro no banco de dados:\n{e}")
        finally:
            db.close()

    ctk.CTkButton(frame, text="✅ Confirmar Aluguel", command=confirmar_locacao, width=250).pack(pady=20)

    return frame
