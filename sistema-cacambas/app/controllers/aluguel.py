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

        # Frame central com largura e altura definidas
        self.conteudo = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=380
        )
        self.conteudo.grid_columnconfigure(0, weight=1)

        # Constrói o conteúdo
        self.build()

        # Garante que o conteúdo esteja renderizado antes de centralizar
        self.update_idletasks()

        # Centraliza o frame no meio da tela
        self.conteudo.place(relx=0.5, rely=0.5, anchor="center")

    def build(self):
        # Título
        titulo = ctk.CTkLabel(
            self.conteudo,
            text="📦 Cadastro de Caçamba",
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        titulo.pack(pady=(10, 30))

        # Identificação
        self.label_ident = ctk.CTkLabel(
            self.conteudo,
            text="Identificação:",
            font=("Segoe UI", 14),
            text_color="#374151"
        )
        self.label_ident.pack(pady=(5, 2))

        self.entry_ident = ctk.CTkEntry(
            self.conteudo,
            justify="center",
            font=("Segoe UI", 12),
            width=280
        )
        self.entry_ident.pack(pady=(0, 20))

        # Localização
        self.label_loc = ctk.CTkLabel(
            self.conteudo,
            text="Localização:",
            font=("Segoe UI", 14),
            text_color="#374151"
        )
        self.label_loc.pack(pady=(5, 2))

        self.entry_loc = ctk.CTkEntry(
            self.conteudo,
            justify="center",
            font=("Segoe UI", 12),
            width=280
        )
        self.entry_loc.pack(pady=(0, 20))

        # Botão Salvar
        self.btn_salvar = ctk.CTkButton(
            self.conteudo,
            text="💾 Salvar Caçamba",
            font=("Segoe UI", 13, "bold"),
            height=40,
            fg_color="#2563EB",
            hover_color="#1E40AF",
            text_color="white",
            command=self.salvar_e_atualizar
        )
        self.btn_salvar.pack(pady=(10, 15))

        # Feedback visual
        self.feedback_label = ctk.CTkLabel(
            self.conteudo,
            text="",
            font=("Segoe UI", 13, "bold"),
            anchor="center",
            justify="center"
        )
        self.feedback_label.pack(pady=(5, 10))

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
