import pandas as pd
import warnings
import traceback
import time

from tkinter import messagebox

from motor import ConferenciaNotaFiscal
from layouts.matriz import LayoutMatriz
from layouts.filial_mg import LayoutFilialMG
from configs import COLUNAS_SALVAS, NOMES_ABAS_NO_EXCEL
from excel_utils import formatar_planilha_excel
from arquivos import adicionar_pendentes_mes_anterior
from recusadas import coletar_recusadas, suprimir_recusadas, construir_aba_recusadas
from seletor_unidade_claude import selecionar_unidade


# Silencia os avisos chatos do openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Cada unidade é uma classe de layout
LAYOUTS = {
    "Matriz": LayoutMatriz,
    "Filial": LayoutFilialMG,
}


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


def exportar_relatorio(caminho, comparacoes, df_notas_somente_erp, df_recusadas):
    """
    Escreve o .xlsx com uma aba por tipo comparado, mais 'Notas Somente no ERP'
    e 'Notas Recusadas'. Os nomes das abas e as colunas vêm do configs.
    """
    with pd.ExcelWriter(caminho, engine="xlsxwriter") as writer:
        for tipo, comparacao in comparacoes.items():
            comparacao.to_excel(
                writer,
                columns=COLUNAS_SALVAS[tipo],
                sheet_name=NOMES_ABAS_NO_EXCEL[tipo],
                index=False,
            )

        df_notas_somente_erp.to_excel(writer, sheet_name="Notas Somente no ERP", index=False)
        df_recusadas.to_excel(writer, sheet_name="Notas Recusadas", index=False)

        for tipo in comparacoes:
            formatar_planilha_excel(writer, COLUNAS_SALVAS[tipo], NOMES_ABAS_NO_EXCEL[tipo])
        formatar_planilha_excel(writer, df_notas_somente_erp.columns.tolist(), "Notas Somente no ERP")
        formatar_planilha_excel(writer, df_recusadas.columns.tolist(), "Notas Recusadas")


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

    arquivo_anterior = arquivos["arquivo_anterior"]

    # 1. Carregamento (ERP comum + documentos externos da unidade)
    dados, df_notas_erp = layout.carregar_dados(arquivos)

    # 2. Notas pendentes do mês anterior
    if arquivo_anterior:
        for tipo in dados:
            dados[tipo] = adicionar_pendentes_mes_anterior(dados[tipo], arquivo_anterior, tipo)

    # 3. Notas recusadas: monta o registro (antes de suprimir) e remove da base
    chaves_recusadas = (
        coletar_recusadas(arquivo_anterior, list(dados))
        if arquivo_anterior else {tipo: set() for tipo in dados}
    )
    df_recusadas = construir_aba_recusadas(dados, chaves_recusadas)
    for tipo in dados:
        dados[tipo] = suprimir_recusadas(dados[tipo], tipo, chaves_recusadas[tipo])

    # 4. Processamento (a parte específica de cada unidade)
    conferencia = ConferenciaNotaFiscal()
    comparacoes, df_notas_somente_erp = layout.comparar(conferencia, dados, df_notas_erp)

    # 5. Formatação das colunas para exportar
    for tipo in comparacoes:
        comparacoes[tipo] = conferencia.formatar_e_limpar_colunas_para_exportar(comparacoes[tipo])

    # 6. Exportação
    exportar_relatorio(layout.arquivo_saida, comparacoes, df_notas_somente_erp, df_recusadas)

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
