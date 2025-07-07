import customtkinter as ctk
from datetime import datetime, timedelta
from .database import init_db, SessionLocal
from .views.cliente_view import abrir_tela_cliente
from .views.cacamba_view import abrir_tela_cacamba
from .views.aluguel_view import abrir_tela_aluguel, abrir_tela_devolucao
from .views.locacao_view import abrir_tela_locacao
from .models import Cacamba, Aluguel
from .views.historico_view import abrir_tela_historico
from app.views.consulta_cliente_view import abrir_tela_consulta_clientes    

def mostrar_dashboard(frame, root):
    for widget in frame.winfo_children():
        widget.destroy()

    db = SessionLocal()
    total_disponiveis = db.query(Cacamba).filter_by(disponivel=True).count()
    total_alugadas = db.query(Cacamba).filter_by(disponivel=False).count()
    hoje = datetime.today()
    limite = hoje + timedelta(days=2)
    vencendo = db.query(Aluguel).filter(
        Aluguel.encerrado == False,
        Aluguel.data_fim <= limite
    ).count()
    db.close()

    ctk.CTkLabel(frame, text="📊 Dashboard", font=("Segoe UI", 20, "bold")).pack(pady=10)

    ctk.CTkLabel(frame, text=f"🚛 Caçambas Alugadas: {total_alugadas}", font=("Segoe UI", 14)).pack(pady=5)
    ctk.CTkLabel(frame, text=f"✅ Caçambas Disponíveis: {total_disponiveis}", font=("Segoe UI", 14)).pack(pady=5)
    ctk.CTkLabel(frame, text=f"⚠️ Vencendo em até 2 dias: {vencendo}", font=("Segoe UI", 14), text_color="red").pack(pady=5)

def main():
    init_db()

    ctk.set_appearance_mode("light")  # Ou "dark"
    ctk.set_default_color_theme("blue")  # Ou "dark-blue", "green" ou seu próprio tema .json

    root = ctk.CTk()
    root.title("Sistema de Caçambas - Menu Principal")
    root.geometry("440x650")

    # Frame do Dashboard
    dashboard_frame = ctk.CTkFrame(root, corner_radius=12)
    dashboard_frame.pack(pady=20, padx=20, fill="x")

    mostrar_dashboard(dashboard_frame, root)

    # Frame dos botões
    botoes_frame = ctk.CTkFrame(root, corner_radius=12)
    botoes_frame.pack(pady=10, padx=20, fill="x")

    ctk.CTkButton(botoes_frame, text="🔄 Atualizar Dashboard", command=lambda: mostrar_dashboard(dashboard_frame, root), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📝 Nova Locação", command=abrir_tela_locacao, width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📋 Novo Cliente", command=abrir_tela_cliente, width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="🚛 Caçambas", command=abrir_tela_cacamba, width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📆 Aluguéis", command=abrir_tela_aluguel, width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="↩️ Devoluções", command=abrir_tela_devolucao, width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📄 Histórico", command=abrir_tela_historico, width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📋 Clientes (Consulta)", command=abrir_tela_consulta_clientes, width=250).pack(pady=5)
    root.mainloop()

if __name__ == "__main__":
    main()
