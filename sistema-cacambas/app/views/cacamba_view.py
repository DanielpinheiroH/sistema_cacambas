from app.controllers.cacamba import registrar_cacamba
import customtkinter as ctk

class TelaCacamba(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#F9FAFB")
        self.grid(row=0, column=0, sticky="nsew")

        # Responsividade da janela principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame central com tamanho fixo para manter alinhamento
        self.conteudo = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        self.conteudo.place(relx=0.5, rely=0.5, anchor="center")  # 100% centralizado

        self.build()

    def build(self):
        # Título
        titulo = ctk.CTkLabel(
            self.conteudo,
            text="📦 Cadastro de Caçamba",
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        titulo.pack(pady=(10, 30))

        # Label Identificação
        self.label_ident = ctk.CTkLabel(
            self.conteudo,
            text="Identificação:",
            font=("Segoe UI", 14),
            text_color="#374151"
        )
        self.label_ident.pack(pady=(5, 2))

        # Entry Identificação
        self.entry_ident = ctk.CTkEntry(
            self.conteudo,
            justify="center",
            width=220,
            font=("Segoe UI", 12)
        )
        self.entry_ident.pack(pady=(0, 20))

        # Label Localização
        self.label_loc = ctk.CTkLabel(
            self.conteudo,
            text="Localização:",
            font=("Segoe UI", 14),
            text_color="#374151"
        )
        self.label_loc.pack(pady=(5, 2))

        # Entry Localização
        self.entry_loc = ctk.CTkEntry(
            self.conteudo,
            justify="center",
            width=300,
            font=("Segoe UI", 12)
        )
        self.entry_loc.pack(pady=(0, 20))

        # Botão Salvar
        self.btn_salvar = ctk.CTkButton(
            self.conteudo,
            text="💾 Salvar Caçamba",
            font=("Segoe UI", 13, "bold"),
            height=40,
            width=300,
            fg_color="#2563EB",
            hover_color="#1E40AF",
            corner_radius=8,
            text_color="white",
            command=self.salvar_e_atualizar
        )
        self.btn_salvar.pack(pady=(10, 15))

        # Feedback centralizado
        self.feedback_label = ctk.CTkLabel(
            self.conteudo,
            text="",
            font=("Segoe UI", 13, "bold"),
            anchor="center",
            justify="center",
            text_color="#111827"
        )
        self.feedback_label.pack(pady=(5, 15))

    def salvar_e_atualizar(self):
        identificacao = self.entry_ident.get().strip()
        localizacao = self.entry_loc.get().strip()

        if identificacao and localizacao:
            sucesso = registrar_cacamba(identificacao, localizacao)
            if sucesso:
                self.feedback_label.configure(
                    text="✅ Caçamba cadastrada com sucesso!",
                    text_color="#059669"
                )
                self.entry_ident.delete(0, "end")
                self.entry_loc.delete(0, "end")
            else:
                self.feedback_label.configure(
                    text="❌ Erro ao cadastrar caçamba!",
                    text_color="#DC2626"
                )
        else:
            self.feedback_label.configure(
                text="⚠️ Preencha todos os campos antes de salvar.",
                text_color="#D97706"
            )

# ✅ Função construtora para uso no main.py
def construir_tela_cacamba(master):
    return TelaCacamba(master)
