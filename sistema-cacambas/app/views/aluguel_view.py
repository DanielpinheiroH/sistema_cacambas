import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models import Cliente, Cacamba, Aluguel

# ---------- TELA DE ALUGUEL ----------
def abrir_tela_aluguel():
    janela = ctk.CTkToplevel()
    janela.title("Registrar Aluguel")
    janela.geometry("500x400")

    frame = ctk.CTkFrame(janela)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    db = SessionLocal()
    clientes = db.query(Cliente).all()
    cacambas = db.query(Cacamba).filter_by(disponivel=True).all()
    db.close()

    ctk.CTkLabel(frame, text="Cliente", font=("Segoe UI", 14)).pack()
    combo_cliente = ctk.CTkOptionMenu(frame, values=[f"{c.id} - {c.nome}" for c in clientes])
    combo_cliente.pack(pady=5)
    if clientes:
        combo_cliente.set(f"{clientes[0].id} - {clientes[0].nome}")

    ctk.CTkLabel(frame, text="Caçamba", font=("Segoe UI", 14)).pack()
    combo_cacamba = ctk.CTkOptionMenu(frame, values=[f"{c.id} - {c.identificacao}" for c in cacambas])
    combo_cacamba.pack(pady=5)
    if cacambas:
        combo_cacamba.set(f"{cacambas[0].id} - {cacambas[0].identificacao}")

    entry_data_fim = ctk.CTkEntry(frame, placeholder_text="Data de Fim (dd/mm/aaaa)", width=300)
    entry_data_fim.pack(pady=10)

    def registrar_aluguel():
        try:
            cliente_id = int(combo_cliente.get().split(" - ")[0])
            cacamba_id = int(combo_cacamba.get().split(" - ")[0])
            data_fim_str = entry_data_fim.get().strip()
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")

            db = SessionLocal()
            novo_aluguel = Aluguel(cliente_id=cliente_id, cacamba_id=cacamba_id, data_fim=data_fim)
            db.add(novo_aluguel)

            cacamba = db.query(Cacamba).get(cacamba_id)
            cacamba.disponivel = False

            db.commit()
            db.close()

            messagebox.showinfo("Sucesso", "Aluguel registrado com sucesso!")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar aluguel: {e}")

    ctk.CTkButton(frame, text="Salvar Aluguel", command=registrar_aluguel, width=200).pack(pady=20)

# ---------- TELA DE DEVOLUÇÃO ----------
def abrir_tela_devolucao():
    janela = ctk.CTkToplevel()
    janela.title("Registrar Devolução")
    janela.geometry("600x400")

    frame = ctk.CTkFrame(janela)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    db = SessionLocal()
    alugueis = db.query(Aluguel).filter_by(encerrado=False)\
        .options(joinedload(Aluguel.cliente), joinedload(Aluguel.cacamba)).all()
    db.close()

    lista_exibicao = [
        f"{a.id} - {a.cliente.nome} - Caçamba {a.cacamba.identificacao} - Devolução: {a.data_fim.strftime('%d/%m/%Y')}"
        for a in alugueis
    ]

    ctk.CTkLabel(frame, text="Selecione um aluguel para devolver:", font=("Segoe UI", 14)).pack(pady=10)
    combo = ctk.CTkOptionMenu(frame, values=lista_exibicao)
    combo.pack(pady=10)
    combo.set(lista_exibicao[0] if lista_exibicao else "Nenhum aluguel disponível")

    def confirmar_devolucao():
        try:
            if not combo.get() or "Nenhum" in combo.get():
                messagebox.showerror("Erro", "Nenhum aluguel selecionado.")
                return

            aluguel_id = int(combo.get().split(" - ")[0])
            db = SessionLocal()

            aluguel = db.query(Aluguel).get(aluguel_id)
            aluguel.encerrado = True

            cacamba = db.query(Cacamba).get(aluguel.cacamba_id)
            cacamba.disponivel = True

            db.commit()
            db.close()

            messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar devolução: {e}")

    ctk.CTkButton(frame, text="Registrar Devolução", command=confirmar_devolucao, width=250).pack(pady=20)
