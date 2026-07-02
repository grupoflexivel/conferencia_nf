import pandas as pd
import numpy as np
import warnings
import traceback
import time

from tkinter import Tk, filedialog, messagebox
from io import StringIO

from layouts.matriz import LayoutMatriz
from relatorios_csw import concatenar_relatorios_erp
from configs import valores_vazios,COLUNAS_IMPORTADAS,COLUNAS_SALVAS,COLUNAS_REPROCESSAMENTO,NOMES_ABAS_NO_EXCEL
from limpeza import (limpar_cnpj_cpf,limpar_numero_documento,limpar_chave_acesso,limpar_colunas_se_coluna_referencia_nulo,converter_valor_monetario_brasileiro,
    tratar_valor_sem_virgula,converter_data_mista,ordenar_por_data_emissao,limpar_numero_documento_servicos)
from excel_utils import formatar_planilha_excel
from arquivos import adicionar_pendentes_mes_anterior, carregar_notas_pendentes_mes_anterior,selecionar_arquivo
from comparacao import mapear_coluna_status, analisar_valores_lançados, verificar_cancelamentos, verificar_situacao_notas_canceladas, remover_documentos_duplicados_reprocessamento

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

    #---------------------------------------------------------------------------------------------------

    df_notas_erp = concatenar_relatorios_erp(arquivo_notas_entrada,arquivo_devolucoes)

    relatorios_externos = layout.carregar_relatorios_externos(arquivos)

    df_notas_sat = relatorios_externos["sat"]
    df_ctes = relatorios_externos["cte"]
    df_notas_servico = relatorios_externos["servico"]

    #---------------------------------------------------------------------------------------------------
    #FORMATAÇÃO DE COLUNAS
    #---------------------------------------------------------------------------------------------------
    df_notas_servico["Valor"] = converter_valor_monetario_brasileiro(df_notas_servico["Valor"])
    df_notas_servico["Valor"] = pd.to_numeric(df_notas_servico["Valor"], errors='coerce')

    dfs = {
        "df_notas_sat" : df_notas_sat,
        "df_notas_erp" : df_notas_erp,
        "df_ctes" : df_ctes,
        "df_notas_servico" : df_notas_servico
    }

    mapeamento_limpeza = {
        "CNPJ/CPF": limpar_cnpj_cpf,
        "Numero_Documento": limpar_numero_documento,
        "ChaveAcesso": limpar_chave_acesso
    }

    for nome, df in dfs.items():
        # Percorre o mapeamento e só aplica se a coluna existir no df
        for coluna, funcao_limpeza in mapeamento_limpeza.items():
            if coluna in df.columns:
                df[coluna] = df[coluna].apply(funcao_limpeza)

    for df in [df_notas_sat, df_ctes, df_notas_servico]:
        if "Observações" not in df.columns:
            df["Observações"] = np.nan

    #UTILIZADO QUANDO FICARAM NOTAS PENDENTES DO MÊS ANTERIOR
    if arquivo_anterior:

        df_notas_sat = adicionar_pendentes_mes_anterior(df_notas_sat,arquivo_anterior,"sat")
        df_ctes = adicionar_pendentes_mes_anterior(df_ctes,arquivo_anterior,"cte")
        df_notas_servico = adicionar_pendentes_mes_anterior(df_notas_servico,arquivo_anterior,"servico")

    #---------------------------------------------------------------------------------------------------
    #PROCESSAMENTO ARQUIVO SAT
    #---------------------------------------------------------------------------------------------------
    comparacao_sat_erp = df_notas_sat.merge(
        df_notas_erp,
        on="ChaveAcesso",
        how="left",
        suffixes=("", "_CSW"), #Não modifico o nome da primeira coluna
        indicator=True
    )

    #Cria a coluna status com base numa lógica pré definida.
    comparacao_sat_erp = mapear_coluna_status(comparacao_sat_erp)
    comparacao_sat_erp = analisar_valores_lançados(comparacao_sat_erp,"Valor","Valor_CSW")
    comparacao_sat_erp = verificar_situacao_notas_canceladas(comparacao_sat_erp,"Situacao","status")

    #Considera somente as notas que sobraram no CSW para continuar a comparação.
    df_notas_erp = df_notas_erp[~df_notas_erp['ChaveAcesso'].isin(df_notas_sat['ChaveAcesso'])]

    #---------------------------------------------------------------------------------------------------
    #PROCESSAMENTO ARQUIVO CTE
    #---------------------------------------------------------------------------------------------------
    comparacao_cte_erp = df_ctes.merge(
        df_notas_erp,
        on="ChaveAcesso",
        how="left",
        suffixes=("","_CSW"), #Não modifico o nome da primeira coluna
        indicator=True
    )

    comparacao_cte_erp = mapear_coluna_status(comparacao_cte_erp)
    comparacao_cte_erp["Valor"] = tratar_valor_sem_virgula(comparacao_cte_erp["Valor"], comparacao_cte_erp["Valor_CSW"]) #Específico do arquivo de CTEs
    comparacao_cte_erp = analisar_valores_lançados(comparacao_cte_erp,"Valor","Valor_CSW")
    comparacao_cte_erp = verificar_situacao_notas_canceladas(comparacao_cte_erp,"SITUACAO","status")

    #Considera somente as notas que sobraram no CSW para continuar a comparação.
    df_notas_erp = df_notas_erp[~df_notas_erp["ChaveAcesso"].isin(comparacao_cte_erp["ChaveAcesso"])]

    #---------------------------------------------------------------------------------------------------
    #PROCESSAMENTO ARQUIVO NOTAS DE SERVIÇO
    #---------------------------------------------------------------------------------------------------
    df_notas_erp["ChaveComparadora"] = df_notas_erp["Numero_Documento"] + "-" + df_notas_erp["CNPJ/CPF"]
    df_notas_servico["ChaveComparadora"] = df_notas_servico["Numero_Documento"] + "-" + df_notas_servico["CNPJ/CPF"]

    comparacao_notas_servico_erp = df_notas_servico.merge(
        df_notas_erp,
        on="ChaveComparadora",
        how="left",
        suffixes=("","_CSW"), #Não modifico o nome da primeira coluna
        indicator=True
    )

    comparacao_notas_servico_erp = mapear_coluna_status(comparacao_notas_servico_erp)
    comparacao_notas_servico_erp = analisar_valores_lançados(comparacao_notas_servico_erp,"Valor","Valor_CSW")
    df_notas_somente_erp = df_notas_erp[~df_notas_erp["ChaveComparadora"].isin(comparacao_notas_servico_erp["ChaveComparadora"])]
    #-------------------------------------------------------------------------
    #COMPARAÇÃO EXTRA, HOJE FEITO SOMENTE PARA AS NOTAS DE SERVIÇO
    """Essa comparação somente ocorre pois lançam as NFs de Serviço com número de documento diferente do que sai no relatório
    Exemplo: 20260000000005574 lançada como 5574. Como não colocam também a Chave de Acesso acabamos ficando sem ChaveComparadora."""
    #-------------------------------------------------------------------------

    notas_servicos_nao_lancadas = comparacao_notas_servico_erp[
        comparacao_notas_servico_erp["status"] == "Não lançada no CSW"
    ].copy()

    notas_servicos_nao_lancadas = notas_servicos_nao_lancadas.drop(
        columns=["_merge"],
        errors="ignore"
    )

    notas_servicos_nao_lancadas["Numero_Documento_Original"] = (
        notas_servicos_nao_lancadas["Numero_Documento"]
    )

    notas_servicos_nao_lancadas["Numero_Documento"] = (
        notas_servicos_nao_lancadas["Numero_Documento"]
        .apply(limpar_numero_documento_servicos)
    )

    notas_servicos_nao_lancadas["ChaveComparadora"] = (
        notas_servicos_nao_lancadas["Numero_Documento"]
        + "-"
        + notas_servicos_nao_lancadas["CNPJ/CPF"]
    )

    notas_servicos_nao_lancadas = notas_servicos_nao_lancadas.drop(
        columns=[
            "Numero_Documento_CSW",
            "Valor_CSW",
            "Cód. Par",
            "Parâmetro",
            "CNPJ/CPF_CSW",
            "ChaveAcesso_CSW",
            "Data Emissão"
        ],
        errors="ignore"
    )

    comparacao_notas_servicos_nao_lancadas = notas_servicos_nao_lancadas.merge(
        df_notas_somente_erp,
        on="ChaveComparadora",
        how="left",
        suffixes=("", "_CSW"),
        indicator=True
    )

    comparacao_notas_servicos_nao_lancadas = comparacao_notas_servicos_nao_lancadas.drop(
        columns=["status", "Alerta Comparador"],
        errors="ignore"
    )

    comparacao_notas_servicos_nao_lancadas = mapear_coluna_status(comparacao_notas_servicos_nao_lancadas)

    comparacao_notas_servicos_nao_lancadas = analisar_valores_lançados(comparacao_notas_servicos_nao_lancadas,"Valor","Valor_CSW")

    comparacao_servico_primeira_tentativa = comparacao_notas_servico_erp[
        comparacao_notas_servico_erp["status"] != "Não lançada no CSW"].copy()

    comparacao_notas_servico_erp = pd.concat([comparacao_servico_primeira_tentativa,comparacao_notas_servicos_nao_lancadas],ignore_index=True)

    comparacao_notas_servico_erp = verificar_cancelamentos(comparacao_notas_servico_erp, "Data de Cancelamento","Situação")

    comparacao_notas_servico_erp = verificar_situacao_notas_canceladas(comparacao_notas_servico_erp,"Situação","status")

    df_notas_somente_erp = df_notas_erp[~df_notas_erp["ChaveComparadora"].isin(comparacao_notas_servico_erp["ChaveComparadora"])]

    #-------------------------------------------------------------------------
    #------------COMPARAÇÃO EXTRA FINALIZADA
    #-------------------------------------------------------------------------

    #---------------------------------------------------------------------------------------------------
    #TRATAMENTO DE DADOS PARA EXPORTAR EM .XLSX
    #---------------------------------------------------------------------------------------------------
    colunas_para_limpar = ['Numero_Documento_CSW','Valor_CSW','Cód. Par', 'Parâmetro', 'CNPJ/CPF_CSW']

    dataframes = [
        comparacao_sat_erp,
        comparacao_cte_erp,
        comparacao_notas_servico_erp
        ]

    dataframes_limpos =[
        limpar_colunas_se_coluna_referencia_nulo(df, "Alerta Comparador", *colunas_para_limpar)
        for df in dataframes
    ]

    comparacao_sat_erp, comparacao_cte_erp, comparacao_notas_servico_erp = dataframes_limpos

    comparacao_sat_erp = ordenar_por_data_emissao(comparacao_sat_erp,"DataEmissao")

    comparacao_cte_erp = ordenar_por_data_emissao(comparacao_cte_erp,"DATA_EMISSÃO")

    comparacao_notas_servico_erp = ordenar_por_data_emissao(comparacao_notas_servico_erp,"Data de Emissão")

    dataframes_relatorio = [
        comparacao_sat_erp,
        comparacao_cte_erp,
        comparacao_notas_servico_erp
    ]
    for df in dataframes_relatorio:
        df.drop(columns=["_merge"], errors="ignore", inplace=True)

        if "Observações" not in df.columns:
            df["Observações"] = np.nan

    df_notas_somente_erp = df_notas_somente_erp.drop(columns=["ChaveComparadora"],errors="ignore")
    #---------------------------------------------------------------------------------------------------
    #EXPORTAÇÃO DOS DADOS PARA .XLSX
    #---------------------------------------------------------------------------------------------------
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