import warnings
import traceback
import time

from tkinter import messagebox

from processamento import LAYOUTS, NenhumDocumentoError, processar_conferencia
from seletor_unidade import selecionar_unidade


# Silencia os avisos chatos do openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def tratar_erro_global(erro: Exception) -> None:
    detalhes_tecnicos = traceback.format_exc()

    mensagem_usuario = (
        "Ocorreu um erro durante a execução da conferência de Notas Fiscais. \n\n"
        "Tire um print desta mensagem e envia para o setor de TI. \n\n"
        "Resumo do erro: \n"
        f"{erro}"
    )

    print("\n" + "=" * 80)
    print("ERRO NA CONFERÊNCIA DE NOTAS")
    print("=" * 80)
    print(mensagem_usuario)
    print("\nDetalhes técnicos:")
    print(detalhes_tecnicos)

    try:
        messagebox.showerror(
            "Erro na Conferência de Notas",
            mensagem_usuario
        )

    except Exception:
        pass

    input("\nPressione Enter para Fechar")


def main():
    unidade = selecionar_unidade()
    if not unidade:
        print("Nenhuma unidade selecionada. Encerrando.")
        return

    layout = LAYOUTS[unidade]()

    arquivos = layout.selecionar_arquivos()
    if arquivos is None:
        print("Seleção de arquivos cancelada. Encerrando.")
        return

    # O ERP é obrigatório: pelo menos entrada OU devolução do Consistem.
    if not (arquivos.get("arquivo_notas_entrada") or arquivos.get("arquivo_devolucoes")):
        messagebox.showwarning(
            "Arquivo obrigatório",
            "Carregue ao menos um relatório do ERP (Notas de Entrada ou de Devolução do Consistem).",
        )
        return

    try:
        processar_conferencia(layout, arquivos)
    except NenhumDocumentoError:
        messagebox.showwarning(
            "Nenhum documento",
            "Carregue ao menos um relatório externo, ou um arquivo anterior com pendências, para comparar.",
        )
        return

    print("Execução Finalizada, fechando a aplicação...")
    time.sleep(1)

    print("Fechando em:")
    for i in range(5, 0, -1):
        unidade_tempo = "segundo" if i == 1 else "segundos"
        print(f" {i} {unidade_tempo}")
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()

    except Exception as erro:
        tratar_erro_global(erro)
