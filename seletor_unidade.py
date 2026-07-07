import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


# --- Identidade visual (logo / ícone) -------------------------------------
ARQUIVO_ICONE = "logo.ico"
ARQUIVO_LOGO = "logo_topo.png"


def _caminho_recurso(nome_arquivo):
    """Resolve o caminho de um recurso tanto rodando pelo Python quanto dentro
    do executável do PyInstaller (que descompacta os recursos em sys._MEIPASS)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, nome_arquivo)


def _aplicar_icone(janela):
    """Define o ícone da barra de título/tarefas. Ignora se o arquivo faltar."""
    try:
        janela.iconbitmap(_caminho_recurso(ARQUIVO_ICONE))
    except Exception:
        pass


def _criar_logo(parent):
    """Cria um Label com o logo, ou None se a imagem não existir. Guarda a
    referência da imagem no próprio Label para o Tkinter não descartá-la."""
    try:
        imagem = tk.PhotoImage(file=_caminho_recurso(ARQUIVO_LOGO))
    except Exception:
        return None
    rotulo = tk.Label(parent, image=imagem)
    rotulo.image = imagem  # segura a referência, senão a imagem some
    return rotulo


def selecionar_unidade():
    """
    Exibe um dialog gráfico com botões para o usuário escolher a unidade.
    Retorna 'Matriz' ou 'Filial', ou None se cancelado.
    """
    janela = tk.Tk()
    janela.title("Conferência de Notas Fiscais")
    janela.geometry("400x300")
    janela.resizable(False, False)
    _aplicar_icone(janela)

    # Centralizar janela na tela
    janela.update_idletasks()
    x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
    y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
    janela.geometry(f"+{x}+{y}")

    escolha = {"unidade": None}

    def escolher(unidade):
        escolha["unidade"] = unidade
        janela.destroy()

    logo = _criar_logo(janela)
    if logo:
        logo.pack(anchor="w", padx=12, pady=(10, 0))

    tk.Label(
        janela,
        text="Selecione a unidade para análise:",
        font=("Arial", 12),
        pady=20,
    ).pack()

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=20)

    tk.Button(
        frame_botoes, text="Matriz", command=lambda: escolher("Matriz"),
        font=("Arial", 11), width=15, height=2, bg="#4CAF50", fg="white", cursor="hand2",
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        frame_botoes, text="Filial MG", command=lambda: escolher("Filial"),
        font=("Arial", 11), width=15, height=2, bg="#2196F3", fg="white", cursor="hand2",
    ).pack(side=tk.LEFT, padx=10)

    janela.protocol("WM_DELETE_WINDOW", janela.destroy)
    janela.mainloop()

    return escolha["unidade"]


def selecionar_arquivos(titulo_janela, campos):
    """
    Exibe UMA janela para o usuário selecionar todos os arquivos de uma vez.

    Parameters
    ----------
    titulo_janela : str
        Título exibido no topo da janela (ex: "Selecione os arquivos - Matriz").
    campos : list[dict]
        Cada item descreve um arquivo com as chaves:
          - "chave"       : nome usado no dicionário de retorno
          - "titulo"      : texto mostrado ao usuário
          - "obrigatorio" : bool (se True, precisa ser selecionado para continuar)

    Returns
    -------
    dict | None
        {chave: caminho_ou_None} com o que o usuário escolheu, ou None se ele
        cancelar/fechar a janela.
    """
    TEXTO_VAZIO = "(nenhum arquivo selecionado)"

    janela = tk.Tk()
    janela.title(titulo_janela)
    janela.resizable(False, False)
    _aplicar_icone(janela)

    caminhos = {campo["chave"]: None for campo in campos}
    rotulos_caminho = {}
    confirmado = {"ok": False}

    def escolher(chave):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            caminhos[chave] = caminho
            rotulos_caminho[chave].config(text=os.path.basename(caminho), fg="#1b5e20")

    def continuar():
        faltando = [
            campo["titulo"]
            for campo in campos
            if campo["obrigatorio"] and not caminhos[campo["chave"]]
        ]
        if faltando:
            messagebox.showwarning(
                "Arquivos obrigatórios",
                "Ainda faltam arquivos obrigatórios:\n\n- " + "\n- ".join(faltando),
            )
            return
        confirmado["ok"] = True
        janela.destroy()

    def cancelar():
        confirmado["ok"] = False
        janela.destroy()

    cabecalho = tk.Frame(janela)
    cabecalho.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(10, 5))

    logo = _criar_logo(cabecalho)
    if logo:
        logo.pack(side=tk.LEFT, padx=(0, 15))

    tk.Label(
        cabecalho, text=titulo_janela, font=("Arial", 13, "bold"),
    ).pack(side=tk.LEFT)

    for indice, campo in enumerate(campos, start=1):
        sufixo = "" if campo["obrigatorio"] else "  (opcional)"

        tk.Label(
            janela, text=campo["titulo"] + sufixo, font=("Arial", 10),
            anchor="w", width=52,
        ).grid(row=indice, column=0, sticky="w", padx=15, pady=4)

        tk.Button(
            janela, text="Selecionar…", width=14, cursor="hand2",
            command=lambda chave=campo["chave"]: escolher(chave),
        ).grid(row=indice, column=1, padx=5)

        rotulo = tk.Label(
            janela, text=TEXTO_VAZIO, font=("Arial", 9), fg="#9e9e9e",
            width=44, anchor="w",
        )
        rotulo.grid(row=indice, column=2, sticky="w", padx=5)
        rotulos_caminho[campo["chave"]] = rotulo

    frame_acoes = tk.Frame(janela)
    frame_acoes.grid(row=len(campos) + 1, column=0, columnspan=3, pady=15)

    tk.Button(
        frame_acoes, text="Continuar", width=14, bg="#4CAF50", fg="white",
        cursor="hand2", command=continuar,
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        frame_acoes, text="Cancelar", width=14, cursor="hand2", command=cancelar,
    ).pack(side=tk.LEFT, padx=10)

    janela.protocol("WM_DELETE_WINDOW", cancelar)

    janela.update_idletasks()
    x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
    y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
    janela.geometry(f"+{x}+{y}")

    janela.mainloop()

    if not confirmado["ok"]:
        return None

    return caminhos
