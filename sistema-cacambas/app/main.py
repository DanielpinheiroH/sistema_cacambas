import customtkinter as ctk
from datetime import datetime, timedelta
from .database import init_db, SessionLocal
from .models import Cacamba, Aluguel

# Agora importando funções que constroem telas (não abrem janelas)
from .views.cliente_view import construir_tela_cliente
from .views.cacamba_view import construir_tela_cacamba
from .views.aluguel_view import construir_tela_aluguel, construir_tela_devolucao
from .views.locacao_view import construir_tela_locacao
from .views.historico_view import construir_tela_historico
from app.views.consulta_cliente_view import construir_tela_consulta_clientes

telas = {}  # Dicionário para armazenar as telas

def mostrar_tela(nome):
    """Traz a tela especificada para frente"""
    if nome in telas:
        telas[nome].tkraise()

def mostrar_dashboard(frame):
    """Atualiza o conteúdo do dashboard"""
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

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Sistema de Caçambas - Menu Principal")
    root.geometry("440x650")

    # Container principal para todas as telas
    container = ctk.CTkFrame(root)
    container.pack(expand=True, fill="both")

    # Construção das telas
    telas["dashboard"] = ctk.CTkFrame(container)
    mostrar_dashboard(telas["dashboard"])

    telas["cliente"] = construir_tela_cliente(container)
    telas["cacamba"] = construir_tela_cacamba(container)
    telas["aluguel"] = construir_tela_aluguel(container)
    telas["devolucao"] = construir_tela_devolucao(container)
    telas["locacao"] = construir_tela_locacao(container)
    telas["historico"] = construir_tela_historico(container)
    telas["consulta_clientes"] = construir_tela_consulta_clientes(container)

    # Posicionamento de todas as telas no mesmo local
    for tela in telas.values():
        tela.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Frame de botões
    botoes_frame = ctk.CTkFrame(root, corner_radius=12)
    botoes_frame.pack(pady=10, padx=20, fill="x")

    # Botões de navegação
    ctk.CTkButton(botoes_frame, text="🔄 Atualizar Dashboard", command=lambda: mostrar_dashboard(telas["dashboard"]), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📊 Ir para Dashboard", command=lambda: mostrar_tela("dashboard"), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📝 Nova Locação", command=lambda: mostrar_tela("locacao"), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📋 Novo Cliente", command=lambda: mostrar_tela("cliente"), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="🚛 Caçambas", command=lambda: mostrar_tela("cacamba"), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📆 Aluguéis", command=lambda: mostrar_tela("aluguel"), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="↩️ Devoluções", command=lambda: mostrar_tela("devolucao"), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📄 Histórico", command=lambda: mostrar_tela("historico"), width=250).pack(pady=5)
    ctk.CTkButton(botoes_frame, text="📋 Clientes (Consulta)", command=lambda: mostrar_tela("consulta_clientes"), width=250).pack(pady=5)

    # Exibe inicialmente o dashboard
    mostrar_tela("dashboard")
    root.mainloop()

if __name__ == "__main__":
    main()
