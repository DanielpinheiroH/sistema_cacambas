import customtkinter as ctk
from tkinter import messagebox
from app.database import SessionLocal
from app.models import Cliente, Aluguel, Cacamba
from datetime import datetime

def construir_tela_consulta_clientes(pai):
    frame_principal = ctk.CTkFrame(pai, corner_radius=10)

    ctk.CTkLabel(frame_principal, text="Clientes Cadastrados", font=("Segoe UI", 18, "bold")).pack(pady=10)

    lista_clientes = ctk.CTkTextbox(frame_principal, height=150)
    lista_clientes.pack(pady=5, fill="x")

    frame_detalhes = ctk.CTkFrame(frame_principal)
    frame_detalhes.pack(pady=10, fill="both", expand=True)

    detalhes_label = ctk.CTkLabel(frame_detalhes, text="Selecione um cliente para ver os detalhes", font=("Segoe UI", 14))
    detalhes_label.pack(pady=5)

    texto_detalhes = ctk.CTkTextbox(frame_detalhes)
    texto_detalhes.pack(padx=10, pady=5, fill="both", expand=True)

    db = SessionLocal()
    clientes = db.query(Cliente).all()
    db.close()

    nomes = [f"{c.id} - {c.nome}" for c in clientes]
    lista_clientes.insert("1.0", "\n".join(nomes))

    def on_cliente_click(event):
        try:
            linha = lista_clientes.get("insert linestart", "insert lineend").strip()
            cliente_id = int(linha.split(" - ")[0])
        except:
            messagebox.showerror("Erro", "Não foi possível identificar o cliente.")
            return

        db = SessionLocal()
        cliente = db.query(Cliente).filter_by(id=cliente_id).first()
        alugueis = db.query(Aluguel).filter_by(cliente_id=cliente.id).order_by(Aluguel.data_inicio.desc()).all()
        db.close()

        texto_detalhes.configure(state="normal")
        texto_detalhes.delete("1.0", "end")

        texto_detalhes.insert("end", f"🧾 Nome: {cliente.nome}\n")
        texto_detalhes.insert("end", f"📄 CPF/CNPJ: {cliente.cpf_cnpj}\n")
        texto_detalhes.insert("end", f"📞 Telefone: {cliente.telefone}\n")
        texto_detalhes.insert("end", f"🏠 Endereço: {cliente.endereco}\n")
        texto_detalhes.insert("end", f"\n📜 Histórico de Locações:\n")

        if not alugueis:
            texto_detalhes.insert("end", "Nenhuma locação encontrada.\n")
        else:
            for aluguel in alugueis:
                status = "Encerrado" if aluguel.encerrado else "Ativo"
                data_ini = aluguel.data_inicio.strftime("%d/%m/%Y")
                data_fim = aluguel.data_fim.strftime("%d/%m/%Y")
                texto_detalhes.insert("end", f"\n🔹 Caçamba: {aluguel.cacamba.identificacao}\n")
                texto_detalhes.insert("end", f"     Início: {data_ini} | Fim: {data_fim} | Status: {status}\n")

        texto_detalhes.configure(state="disabled")

    lista_clientes.bind("<ButtonRelease-1>", on_cliente_click)

    return frame_principal
