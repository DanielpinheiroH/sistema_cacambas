from app.controllers.cacamba import registrar_cacamba, listar_cacambas_disponiveis
import customtkinter as ctk

class TelaCacamba(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.build()

    def build(self):
        self.label = ctk.CTkLabel(self, text="Identificação:")
        self.label.pack()

        self.entry_ident = ctk.CTkEntry(self)
        self.entry_ident.pack()

        self.label_loc = ctk.CTkLabel(self, text="Localização Atual:")
        self.label_loc.pack()

        self.entry_loc = ctk.CTkEntry(self)
        self.entry_loc.pack()

        self.btn_salvar = ctk.CTkButton(self, text="Salvar Caçamba", command=self.salvar_e_atualizar)
        self.btn_salvar.pack(pady=10)

        self.lista_cacambas = ctk.CTkComboBox(self, values=[])
        self.lista_cacambas.pack()

        self.atualizar_lista_cacambas()

    def salvar_e_atualizar(self):
        identificacao = self.entry_ident.get()
        localizacao = self.entry_loc.get()
        if registrar_cacamba(identificacao, localizacao):
            ctk.CTkLabel(self, text="Caçamba cadastrada com sucesso!").pack()
            self.atualizar_lista_cacambas()
        else:
            ctk.CTkLabel(self, text="Erro ao cadastrar caçamba!").pack()

    def atualizar_lista_cacambas(self):
        cacambas = listar_cacambas_disponiveis()
        opcoes = [c.identificacao for c in cacambas]
        self.lista_cacambas.configure(values=opcoes)
