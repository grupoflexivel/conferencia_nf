import pandas as pd
import numpy as np
import warnings
import traceback
import time

from tkinter import messagebox

from motor import ConferenciaNotaFiscal
from layouts.matriz import LayoutMatriz
from layouts.filial_mg import LayoutFilialMG
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

    empresa_escolhida = input("Qual empresa?")

    if empresa_escolhida == "Matriz":

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

    if empresa_escolhida == "Filial":

        layout = LayoutFilialMG()

        arquivos = layout.selecionar_arquivos()

        arquivo_anterior = arquivos["arquivo_anterior"]
        arquivo_notas_entrada = arquivos["arquivo_notas_entrada"]
        arquivo_devolucoes = arquivos["arquivo_devolucoes"]

        df_notas_erp = concatenar_relatorios_erp(arquivo_notas_entrada,arquivo_devolucoes)

        relatorios_externos = layout.carregar_relatorios_externos_filial(arquivos)

        df_qive_filial = relatorios_externos["qive-filial"]
        df_cte_filial = relatorios_externos["cte-filial"]
        df_servicos_filial = relatorios_externos["servico"]

    #UTILIZADO QUANDO FICARAM NOTAS PENDENTES DO MÊS ANTERIOR
    if arquivo_anterior:

        if empresa_escolhida == "Matriz":

            df_notas_sat = adicionar_pendentes_mes_anterior(df_notas_sat,arquivo_anterior,"sat")
            df_ctes = adicionar_pendentes_mes_anterior(df_ctes,arquivo_anterior,"cte")
            df_notas_servico = adicionar_pendentes_mes_anterior(df_notas_servico,arquivo_anterior,"servico")
        
        if empresa_escolhida == "Filial":
            
            df_qive_filial = adicionar_pendentes_mes_anterior(df_qive_filial, arquivo_anterior, "qive-filial")
            df_cte_filial = adicionar_pendentes_mes_anterior(df_cte_filial,arquivo_anterior, "cte-filial")
            df_servicos_filial = adicionar_pendentes_mes_anterior(df_servicos_filial,arquivo_anterior, "servico")

    #---------------------------------------------------------------------------------------------------------
    #PROCESSAMENTO
    #---------------------------------------------------------------------------------------------------------

    if empresa_escolhida == "Filial":
        conferencia = ConferenciaNotaFiscal()

        comparacao_qive_erp, df_erp = conferencia.comparar_sat_ou_qive_csw(df_qive_filial,df_notas_erp,"ChaveAcesso","Situacao")
        comparacao_cte_erp, df_notas_erp = conferencia.comparar_sat_ou_qive_csw(df_cte_filial,df_erp,"ChaveAcesso","Situacao")
    
        comparacao_notas_servico_erp, df_notas_somente_erp=conferencia.comparar_servicos_csw(df_servicos_filial, df_notas_erp,"Situacao")

    if empresa_escolhida == "Matriz":

        conferencia = ConferenciaNotaFiscal()

        comparacao_sat_erp, df_notas_erp = conferencia.comparar_sat_ou_qive_csw(df_notas_sat,df_notas_erp,"ChaveAcesso","Situacao")
        comparacao_cte_erp, df_notas_erp = conferencia.comparar_cte_matriz_csw(df_ctes, df_notas_erp, "ChaveAcesso", "Situacao" )

        comparacao_notas_servico_erp, df_notas_somente_erp=conferencia.comparar_servicos_csw(df_notas_servico, df_notas_erp,"Situacao")

    #TRATAMENTO DE DADOS PARA EXPORTAR EM .XLSX
    #---------------------------------------------------------------------------------------------------
    if empresa_escolhida == "Matriz":

        comparacao_cte_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_cte_erp)
        comparacao_notas_servico_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_notas_servico_erp)
        comparacao_sat_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_sat_erp)
    
    if empresa_escolhida == "Filial":

        comparacao_qive_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_qive_erp)
        comparacao_cte_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_cte_erp)
        comparacao_notas_servico_erp = conferencia.formatar_e_limpar_colunas_para_exportar(comparacao_notas_servico_erp)


    #---------------------------------------------------------------------------------------------------
    #EXPORTAÇÃO DOS DADOS PARA .XLSX
    #---------------------------------------------------------------------------------------------------
    if empresa_escolhida == "Matriz":

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

    if empresa_escolhida == "Filial":

        with pd.ExcelWriter("comparacao_notas_filial.xlsx", engine="xlsxwriter") as writer:
            comparacao_qive_erp.to_excel(writer,
                                columns=COLUNAS_SALVAS["qive-filial"],
                                sheet_name="Comparação QIVE vs CSW",
                                index=False
                                )
            comparacao_cte_erp.to_excel(writer,
                                columns=COLUNAS_SALVAS["cte-filial"],
                                sheet_name="Comparação CTE-QIVE vs CSW",
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

            formatar_planilha_excel(writer, COLUNAS_SALVAS["qive-filial"], "Comparação QIVE vs CSW")
            formatar_planilha_excel(writer, COLUNAS_SALVAS["cte-filial"], "Comparação CTE-QIVE vs CSW")
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