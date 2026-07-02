import pandas as pd
from comparacao import mapear_coluna_status,analisar_diferenca_entre_valores_lançados,verificar_situacao_notas_canceladas
from limpeza import tratar_valor_sem_virgula

class ConferenciaNotaFiscal:

    def __init__(self):

        self.coluna_valor_doc_referencia = "Valor"
        self.coluna_valor_erp = "Valor_CSW"
        self.coluna_status = "status"
        self.sufixo_erp = "_CSW"


    def realizar_merge(self, dataframe:pd.DataFrame, dataframe_csw:pd.DataFrame, coluna_base_comparacao:str) -> pd.DataFrame:
        
        dataframe = dataframe.copy()
        dataframe_csw = dataframe_csw.copy()

        merge_dataframes = dataframe.merge(
                dataframe_csw,
                on=coluna_base_comparacao,
                how="left",
                suffixes=("", self.sufixo_erp),
                indicator=True
            )
        return merge_dataframes
    
    def realizar_analises_colunas(self, dataframe: pd.DataFrame,coluna_situacao: str, coluna_status: str):
        
        dataframe = dataframe.copy()

        dataframe = mapear_coluna_status(dataframe)
        dataframe = analisar_diferenca_entre_valores_lançados(dataframe, self.coluna_valor_doc_referencia, self.coluna_valor_erp)
        dataframe = verificar_situacao_notas_canceladas(dataframe, coluna_situacao, self.coluna_status )

        return dataframe
    
    def remover_notas_ja_lancadas(self,dataframe:pd.DataFrame, dataframe_csw: pd.DataFrame, coluna_base_comparacao: str):

        dataframe = dataframe.copy()
        dataframe_csw = dataframe_csw.copy()

        notas_restantes_csw = dataframe_csw[~dataframe_csw[coluna_base_comparacao].isin(dataframe[coluna_base_comparacao])]

        return notas_restantes_csw


    def comparar_sat_csw(self, dataframe:pd.DataFrame,dataframe_csw: pd.DataFrame,coluna_base_comparacao: str
                         ,coluna_situacao: str, coluna_status: str) -> pd.DataFrame:

        comparativo = self.realizar_merge(dataframe,dataframe_csw,coluna_base_comparacao)

        comparativo = self.realizar_analises_colunas(comparativo,coluna_situacao,coluna_status)
        
        notas_restantes_csw = self.remover_notas_ja_lancadas(dataframe,dataframe_csw,coluna_base_comparacao)
        
        return comparativo, notas_restantes_csw


    # def comparar_cte_csw(self, dataframe:pd.DataFrame,dataframe_csw: pd.DataFrame,coluna_base_comparacao:str) -> pd.DataFrame:
    #     comparacao_cte_csw = df_ctes.merge(
    #         notas_restantes_erp,
    #         on="ChaveAcesso",
    #         how="left",
    #         suffixes=("","_CSW"), #Não modifico o nome da primeira coluna
    #         indicator=True
    #     )

    #     comparacao_cte_csw = mapear_coluna_status(comparacao_cte_csw)
    #     comparacao_cte_csw["Valor"] = tratar_valor_sem_virgula(comparacao_cte_csw["Valor"], comparacao_cte_csw["Valor_CSW"]) #Específico do arquivo de CTEs
    #     comparacao_cte_csw = analisar_valores_lançados(comparacao_cte_csw,"Valor","Valor_CSW")
    #     comparacao_cte_csw = verificar_situacao_notas_canceladas(comparacao_cte_csw,"SITUACAO","status")

    #     #Considera somente as notas que sobraram no CSW para continuar a comparação.
    #     notas_restantes_erp = notas_restantes_erp[~notas_restantes_erp["ChaveAcesso"].isin(comparacao_cte_csw["ChaveAcesso"])]

    #     #---------------------------------------------------------------------------------------------------
    #     #PROCESSAMENTO ARQUIVO NOTAS DE SERVIÇO
    #     #---------------------------------------------------------------------------------------------------
    #     notas_restantes_erp["ChaveComparadora"] = notas_restantes_erp["Numero_Documento"] + "-" + notas_restantes_erp["CNPJ/CPF"]
    #     df_notas_servico["ChaveComparadora"] = df_notas_servico["Numero_Documento"] + "-" + df_notas_servico["CNPJ/CPF"]

    #     comparacao_notas_servico_csw = df_notas_servico.merge(
    #         notas_restantes_erp,
    #         on="ChaveComparadora",
    #         how="left",
    #         suffixes=("","_CSW"), #Não modifico o nome da primeira coluna
    #         indicator=True
    #     )

    #     comparacao_notas_servico_csw = mapear_coluna_status(comparacao_notas_servico_csw)
    #     comparacao_notas_servico_csw = analisar_valores_lançados(comparacao_notas_servico_csw,"Valor","Valor_CSW")
    #     df_notas_somente_csw = notas_restantes_erp[~notas_restantes_erp["ChaveComparadora"].isin(comparacao_notas_servico_csw["ChaveComparadora"])]
        
        