import customtkinter as ctk
from tkinter import messagebox
import requests

API_URL = "http://127.0.0.1:8000/validar_token"

class TokenView(ctk.CTkFrame):
    def __init__(self, master, on_validado):
        super().__init__(master)
        self.on_validado = on_validado
        self.grid(row=0, column=0, sticky="nsew")

        # Layout responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # Título
        ctk.CTkLabel(
            self,
            text="🔐 Acesso ao Sistema",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=1, column=0, pady=(10, 10), sticky="n")

        # Campo de token
        self.token_entry = ctk.CTkEntry(
            self,
            placeholder_text="Digite seu token de acesso",
            width=300,
            height=40
        )
        self.token_entry.grid(row=2, column=0, pady=10, padx=20)

        # Botão "Entrar"
        self.entrar_button = ctk.CTkButton(
            self,
            text="Entrar",
            width=120,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.validar_token
        )
        self.entrar_button.grid(row=3, column=0, pady=(10, 30))

        # Enter ativa botão
        self.token_entry.bind("<Return>", lambda event: self.validar_token())

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