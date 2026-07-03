import pandas as pd
import numpy as np
from comparacao import mapear_coluna_status,analisar_diferenca_entre_valores_lançados,verificar_situacao_notas_canceladas,verificar_cancelamentos
from limpeza import tratar_valor_sem_virgula, limpar_numero_documento_servicos,limpar_colunas_se_coluna_referencia_nulo,ordenar_por_data_emissao

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
    
    def realizar_analises_colunas(self, dataframe: pd.DataFrame,coluna_situacao: str,
                                 tratar_valores_sem_virgula: bool = False, verificar_cancelamentos_notas_servico : bool = False) -> pd.DataFrame:
        
        dataframe = dataframe.copy()

        dataframe = mapear_coluna_status(dataframe)

        if tratar_valores_sem_virgula:

            dataframe[self.coluna_valor_doc_referencia] = tratar_valor_sem_virgula(
                dataframe[self.coluna_valor_doc_referencia],
                dataframe[self.coluna_valor_erp]
            )

        dataframe = analisar_diferenca_entre_valores_lançados(dataframe, self.coluna_valor_doc_referencia, self.coluna_valor_erp)

        if verificar_cancelamentos_notas_servico:

            dataframe = verificar_cancelamentos(dataframe,"Data de Cancelamento","Situacao")

        dataframe = verificar_situacao_notas_canceladas(dataframe, coluna_situacao, self.coluna_status )

        return dataframe
    
    def remover_notas_ja_lancadas(self,dataframe:pd.DataFrame, dataframe_csw: pd.DataFrame, coluna_base_comparacao: str):

        dataframe = dataframe.copy()
        dataframe_csw = dataframe_csw.copy()

        notas_restantes_csw = dataframe_csw[~dataframe_csw[coluna_base_comparacao].isin(dataframe[coluna_base_comparacao])]

        return notas_restantes_csw

    def formatar_e_limpar_colunas_para_exportar(self, dataframe: pd.DataFrame):
    
        dataframe = dataframe.copy()

        colunas_para_limpar_dados = ['Numero_Documento_CSW','Valor_CSW','Cód. Par', 'Parâmetro', 'CNPJ/CPF_CSW']
        dataframe = limpar_colunas_se_coluna_referencia_nulo(dataframe, "Alerta Comparador", *colunas_para_limpar_dados)
        dataframe = ordenar_por_data_emissao(dataframe,"Data_Emissao")
        
        if "Observações" not in dataframe.columns:
            dataframe["Observações"] = np.nan

        return dataframe 

    def comparar_sat_ou_qive_csw(self, dataframe:pd.DataFrame,dataframe_csw: pd.DataFrame,coluna_base_comparacao: str
                         ,coluna_situacao: str) -> tuple[pd.DataFrame]:

        comparativo = self.realizar_merge(dataframe,dataframe_csw,coluna_base_comparacao)

        comparativo = self.realizar_analises_colunas(comparativo,coluna_situacao)
        
        notas_restantes_csw = self.remover_notas_ja_lancadas(dataframe,dataframe_csw,coluna_base_comparacao)
        
        return comparativo, notas_restantes_csw
    
    def comparar_cte_matriz_csw(self, dataframe:pd.DataFrame, dataframe_csw: pd.DataFrame, coluna_base_comparacao: str,
                         coluna_situacao: str) -> tuple[pd.DataFrame]:

        comparativo = self.realizar_merge(dataframe, dataframe_csw, coluna_base_comparacao)

        comparativo = self.realizar_analises_colunas(comparativo,coluna_situacao,tratar_valores_sem_virgula=True)

        notas_restantes_csw = self.remover_notas_ja_lancadas(dataframe,dataframe_csw,coluna_base_comparacao)

        return comparativo, notas_restantes_csw
    
    def comparar_servicos_matriz_csw(self, dataframe:pd.DataFrame, dataframe_csw: pd.DataFrame, coluna_base_comparacao: str,
                         coluna_situacao: str) -> tuple[pd.DataFrame]:
        
        dataframe = dataframe.copy()
        dataframe["Numero_Documento_Original"] = dataframe["Numero_Documento"]
        dataframe["Numero_Documento"] = dataframe["Numero_Documento"].apply(limpar_numero_documento_servicos)

        comparativo = self.realizar_merge(dataframe, dataframe_csw, coluna_base_comparacao)

        comparativo = self.realizar_analises_colunas(comparativo,coluna_situacao,verificar_cancelamentos_notas_servico=True)

        notas_restantes_csw = self.remover_notas_ja_lancadas(dataframe,dataframe_csw,coluna_base_comparacao)

        return comparativo, notas_restantes_csw

        