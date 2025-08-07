import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import requests
import os

API_URL = "https://sistema-cacambas.onrender.com/validar_token"

class TokenView(ctk.CTkFrame):
    def __init__(self, master, on_validado):
        super().__init__(master)
        self.on_validado = on_validado
        self.grid(row=0, column=0, sticky="nsew")

        # Deixa a área da tela expansiva
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame centralizador
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0)
        container.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Ícone (se existir)
        caminho_icone = os.path.join("app", "assets", "icon.png")
        if os.path.exists(caminho_icone):
            imagem = ctk.CTkImage(light_image=Image.open(caminho_icone), size=(250, 200))
            ctk.CTkLabel(container, image=imagem, text="").grid(row=0, column=0, pady=(0, 10))

        # Nome do sistema
        ctk.CTkLabel(
            container,
            text="Sistema de Gerenciamento de Caçambas",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=1, column=0, pady=(5, 5))

        # Subtítulo
        ctk.CTkLabel(
            container,
            text="Acesso com Token",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#000000"
        ).grid(row=2, column=0, pady=(0, 20))

        # Campo de token
        self.token_entry = ctk.CTkEntry(
            container,
            placeholder_text="Digite seu token de acesso",
            placeholder_text_color="#000000",
            width=320,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#000000",
            border_width=2,
            corner_radius=6
        )
        self.token_entry.grid(row=3, column=0, pady=10, padx=20)

        # Botão de entrada
        self.entrar_button = ctk.CTkButton(
            container,
            text="Entrar 🔓",
            width=150,
            height=45,
            font=("Segoe UI", 20, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white",
            corner_radius=8,
            command=self.validar_token
        )
        self.entrar_button.grid(row=4, column=0, pady=(10, 30))

        # Atalho Enter
        self.token_entry.bind("<Return>", lambda event: self.validar_token())

        # CENTRALIZAÇÃO do container
        self.after(100, self.centralizar_container)

    def centralizar_container(self):
        # Pegamos o tamanho da tela e do frame
        largura_total = self.winfo_width()
        altura_total = self.winfo_height()
        container = self.winfo_children()[0]

        largura_container = container.winfo_reqwidth()
        altura_container = container.winfo_reqheight()

        x_offset = max((largura_total - largura_container) // 2, 0)
        y_offset = max((altura_total - altura_container) // 2, 0)

        container.grid_configure(padx=x_offset, pady=y_offset)

    def validar_token(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Erro", "Por favor, insira o token de acesso.")
            return

        try:
            response = requests.post(API_URL, json={"token": token})
            if response.status_code == 200:
                dados_cliente = response.json()
                self.on_validado(dados_cliente)
            else:
                messagebox.showerror("Acesso Negado", "Token inválido ou acesso expirado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro de conexão com o servidor:\n{e}")