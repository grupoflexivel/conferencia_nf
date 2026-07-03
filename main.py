import pandas as pd
import numpy as np
import warnings
import traceback
import time

from tkinter import messagebox

from motor import ConferenciaNotaFiscal
from layouts.matriz import LayoutMatriz
from relatorios_csw import concatenar_relatorios_erp
from configs import COLUNAS_SALVAS
from excel_utils import formatar_planilha_excel
from arquivos import adicionar_pendentes_mes_anterior


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
    #---------------------------------------------------------------------------------------------------
    #INICIO DA APLICAÇÃO
    #---------------------------------------------------------------------------------------------------

    layout = LayoutMatriz()

    arquivos = layout.selecionar_arquivos()

    arquivo_anterior = arquivos["arquivo_anterior"]
    arquivo_notas_entrada = arquivos["arquivo_notas_entrada"]
    arquivo_devolucoes = arquivos["arquivo_devolucoes"]

    df_notas_erp = concatenar_relatorios_erp(arquivo_notas_entrada,arquivo_devolucoes)

    relatorios_externos = layout.carregar_relatorios_externos(arquivos)

    df_notas_sat = relatorios_externos["sat"]
    df_ctes = relatorios_externos["cte"]
    df_notas_servico = relatorios_externos["servico"]

    #---------------------------------------------------------------------------------------------------
    #CRIAÇÃO COLUNA OBSERVAÇÕES
    #---------------------------------------------------------------------------------------------------

    for df in [df_notas_sat, df_ctes, df_notas_servico]:
        if "Observações" not in df.columns:
            df["Observações"] = np.nan

    #UTILIZADO QUANDO FICARAM NOTAS PENDENTES DO MÊS ANTERIOR
    if arquivo_anterior:

        df_notas_sat = adicionar_pendentes_mes_anterior(df_notas_sat,arquivo_anterior,"sat")
        df_ctes = adicionar_pendentes_mes_anterior(df_ctes,arquivo_anterior,"cte")
        df_notas_servico = adicionar_pendentes_mes_anterior(df_notas_servico,arquivo_anterior,"servico")

    conferencia = ConferenciaNotaFiscal()

    #---------------------------------------------------------------------------------------------------
    #PROCESSAMENTO ARQUIVO SAT
    #---------------------------------------------------------------------------------------------------
    comparacao_sat_erp, df_notas_erp = conferencia.comparar_sat_csw(df_notas_sat,df_notas_erp,"ChaveAcesso","Situacao")

    #---------------------------------------------------------------------------------------------------
    #PROCESSAMENTO ARQUIVO CTE
    #---------------------------------------------------------------------------------------------------
    comparacao_cte_erp, df_notas_erp = conferencia.comparar_cte_csw(df_ctes, df_notas_erp, "ChaveAcesso", "Situacao" )
    #---------------------------------------------------------------------------------------------------
    #PROCESSAMENTO ARQUIVO NOTAS DE SERVIÇO
    #---------------------------------------------------------------------------------------------------
    df_notas_erp["ChaveComparadora"] = df_notas_erp["Numero_Documento"] + "-" + df_notas_erp["CNPJ/CPF"]
    df_notas_servico["ChaveComparadora"] = df_notas_servico["Numero_Documento"] + "-" + df_notas_servico["CNPJ/CPF"]

    comparacao_notas_servico_erp, df_notas_somente_erp=conferencia.comparar_servicos_csw(df_notas_servico, df_notas_erp, "ChaveComparadora", "Situacao")

    #---------------------------------------------------------------------------------------------------
    #TRATAMENTO DE DADOS PARA EXPORTAR EM .XLSX
    #---------------------------------------------------------------------------------------------------

    comparacao_cte_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_cte_erp)
    comparacao_notas_servico_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_notas_servico_erp)
    comparacao_sat_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_sat_erp)

    #---------------------------------------------------------------------------------------------------
    #EXPORTAÇÃO DOS DADOS PARA .XLSX
    #---------------------------------------------------------------------------------------------------

    def validar_colunas_exportacao(dataframe, colunas_esperadas, nome_relatorio):
        colunas_faltando = [
            coluna for coluna in colunas_esperadas
            if coluna not in dataframe.columns
        ]

        if colunas_faltando:
            raise ValueError(
                f"As seguintes colunas estão faltando no relatório {nome_relatorio}: "
                f"{colunas_faltando}"
            )
        
    validar_colunas_exportacao(comparacao_notas_servico_erp,COLUNAS_SALVAS["servico"],"Serviço vs CSW")

    
    with pd.ExcelWriter("comparacao_notas.xlsx", engine="xlsxwriter") as writer:
        comparacao_sat_erp.to_excel(writer,
                            columns=COLUNAS_SALVAS["sat"],
                            sheet_name="Comparação SAT vs CSW",
                            index=False
                            )
        comparacao_cte_erp.to_excel(writer,
                            columns=COLUNAS_SALVAS["cte"],
                            sheet_name="Comparação CTE vs CSW",
                            index=False
                            )
        comparacao_notas_servico_erp.to_excel(writer,
                            columns=COLUNAS_SALVAS["servico"],
                            sheet_name="Comparacao Serviços vs CSW",
                            index=False
                            )   
        df_notas_somente_erp.to_excel(
            writer,
            sheet_name="Notas Somente no ERP",
            index=False
        )

        formatar_planilha_excel(writer, COLUNAS_SALVAS["sat"], "Comparação SAT vs CSW")
        formatar_planilha_excel(writer, COLUNAS_SALVAS["cte"], "Comparação CTE vs CSW")
        formatar_planilha_excel(writer, COLUNAS_SALVAS["servico"], "Comparacao Serviços vs CSW")
        formatar_planilha_excel(writer, df_notas_somente_erp.columns.tolist(), "Notas Somente no ERP")

    print("Execução Finalizada, fechando a aplicação...")

    time.sleep(1)

    print("Fechando em:")

    for i in range(5, 0, -1):
        unidade = "segundo" if i == 1 else "segundos"
        print(f" {i} {unidade}")
        time.sleep(1)

if __name__ == "__main__":
    
    try:
        main()

    except Exception as erro:
        tratar_erro_global(erro)