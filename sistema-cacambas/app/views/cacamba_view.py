from app.controllers.cacamba import (
    registrar_cacamba,
    buscar_cacamba_por_identificacao,  # pode retornar {"identificacao": "123", "localizacao": "Rua X"} ou "localizacao_atual"
    excluir_cacamba
)
import customtkinter as ctk


class TelaCacamba(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#C6C8CA")
        self.grid(row=0, column=0, sticky="nsew")

        # ====== Ajustes de layout geral ======
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Limites de largura do card
        self.MARGEM = 24         # margem horizontal (px)
        self.MAX_LARGURA = 720   # largura máxima do card
        self.MIN_LARGURA = 520   # largura mínima confortável

        # Área que expande 100%
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=0, column=0, sticky="nsew")

        # Card central (centralizado H e V; largura controlada no <Configure>)
        self.card = ctk.CTkFrame(self.conteudo, fg_color="white", corner_radius=12)
        self.card.place(relx=0.5, rely=0.5, anchor="center")  # 👈 agora fica no centro da tela

        # Ajusta a largura do card conforme o tamanho da janela (respeitando min/max)
        self.conteudo.bind("<Configure>", self._ajustar_largura_card)

        self.build()

    def _ajustar_largura_card(self, event=None):
        largura_disp = max(self.conteudo.winfo_width() - 2 * self.MARGEM, 0)
        largura_clamp = max(self.MIN_LARGURA, min(self.MAX_LARGURA, largura_disp))
        self.card.configure(width=largura_clamp)  # ✅ ajustar via configure (não no .place)

    def build(self):
        # Título
        titulo = ctk.CTkLabel(
            self.card,
            text="📦 Cadastro de Caçamba",
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        titulo.pack(pady=(16, 28))

        # Label Identificação
        self.label_ident = ctk.CTkLabel(
            self.card,
            text="Identificação:",
            font=("Segoe UI", 14),
            text_color="#374151"
        )
        self.label_ident.pack(pady=(4, 2), padx=20, anchor="w")

        # Entry Identificação
        self.entry_ident = ctk.CTkEntry(
            self.card,
            justify="center",
            font=("Segoe UI", 12)
        )
        self.entry_ident.pack(pady=(0, 10), padx=20, fill="x")

        # Linha de ações (Pesquisar / Excluir)
        acoes_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        acoes_frame.pack(pady=(0, 18), padx=20, fill="x")

        self.btn_pesquisar = ctk.CTkButton(
            acoes_frame,
            text="🔍 Pesquisar",
            font=("Segoe UI", 12, "bold"),
            height=36,
            width=150,
            fg_color="#0EA5E9",
            hover_color="#0369A1",
            corner_radius=8,
            text_color="white",
            command=self.pesquisar_cacamba
        )
        self.btn_pesquisar.pack(side="left")

        self.btn_excluir = ctk.CTkButton(
            acoes_frame,
            text="🗑️ Excluir",
            font=("Segoe UI", 12, "bold"),
            height=36,
            width=130,
            fg_color="#DC2626",
            hover_color="#991B1B",
            corner_radius=8,
            text_color="white",
            command=self.excluir_cacamba
        )
        self.btn_excluir.pack(side="left", padx=10)

        # Label Localização
        self.label_loc = ctk.CTkLabel(
            self.card,
            text="Localização:",
            font=("Segoe UI", 14),
            text_color="#374151"
        )
        self.label_loc.pack(pady=(4, 2), padx=20, anchor="w")

        # Entry Localização
        self.entry_loc = ctk.CTkEntry(
            self.card,
            justify="center",
            font=("Segoe UI", 12)
        )
        self.entry_loc.pack(pady=(0, 18), padx=20, fill="x")

        # Botão Salvar
        self.btn_salvar = ctk.CTkButton(
            self.card,
            text="💾 Salvar Caçamba",
            font=("Segoe UI", 13, "bold"),
            height=40,
            fg_color="#2563EB",
            hover_color="#1E40AF",
            corner_radius=8,
            text_color="white",
            command=self.salvar_e_atualizar
        )
        self.btn_salvar.pack(pady=(6, 14), padx=20, fill="x")

        # Feedback centralizado
        self.feedback_label = ctk.CTkLabel(
            self.card,
            text="",
            font=("Segoe UI", 13, "bold"),
            anchor="center",
            justify="center",
            text_color="#111827"
        )
        self.feedback_label.pack(pady=(4, 16), padx=20)

    # ====== Novas funcionalidades ======

    def pesquisar_cacamba(self):
        """Busca a caçamba pelo número (identificação) e preenche a localização, se existir."""
        identificacao = self.entry_ident.get().strip()
        if not identificacao:
            self._feedback("⚠️ Informe a identificação para pesquisar.", "#D97706")
            return

        try:
            registro = buscar_cacamba_por_identificacao(identificacao)
        except Exception as e:
            self._feedback(f"❌ Erro na pesquisa: {e}", "#DC2626")
            return

        if registro:
            # Aceita tanto 'localizacao' quanto 'localizacao_atual'
            valor_loc = (
                registro.get("localizacao")
                if "localizacao" in registro
                else registro.get("localizacao_atual", "")
            )
            self.entry_loc.delete(0, "end")
            self.entry_loc.insert(0, str(valor_loc))
            self._feedback("✅ Caçamba encontrada e carregada.", "#059669")
        else:
            self._feedback("🔎 Nenhuma caçamba encontrada para essa identificação.", "#374151")

    def excluir_cacamba(self):
        """Exclui a caçamba pelo número (identificação)."""
        identificacao = self.entry_ident.get().strip()
        if not identificacao:
            self._feedback("⚠️ Informe a identificação para excluir.", "#D97706")
            return

        try:
            ok = excluir_cacamba(identificacao)
        except Exception as e:
            self._feedback(f"❌ Erro ao excluir: {e}", "#DC2626")
            return

        if ok:
            self.entry_ident.delete(0, "end")
            self.entry_loc.delete(0, "end")
            self._feedback("🗑️ Caçamba excluída com sucesso.", "#DC2626")
        else:
            self._feedback("❌ Caçamba não encontrada ou não foi possível excluir.", "#DC2626")

    # ====== Fluxo já existente de salvar ======
    def salvar_e_atualizar(self):
        identificacao = self.entry_ident.get().strip()
        localizacao_atual = self.entry_loc.get().strip()

        if identificacao and localizacao_atual:
            try:
                sucesso = registrar_cacamba(identificacao, localizacao_atual)
            except Exception as e:
                self._feedback(f"❌ Erro ao cadastrar: {e}", "#DC2626")
                return

            if sucesso:
                self._feedback("✅ Caçamba cadastrada com sucesso!", "#059669")
                self.entry_ident.delete(0, "end")
                self.entry_loc.delete(0, "end")
            else:
                self._feedback("❌ Erro ao cadastrar caçamba!", "#DC2626")
        else:
            self._feedback("⚠️ Preencha todos os campos antes de salvar.", "#D97706")

    def _feedback(self, texto: str, cor_hex: str):
        self.feedback_label.configure(text=texto, text_color=cor_hex)


# ✅ Função construtora para uso no main.py
def construir_tela_cacamba(master):
    return TelaCacamba(master)
