import pandas as pd
from layouts.base import LayoutBase
from configs import COLUNAS_IMPORTADAS,valores_vazios
from seletor_unidade import selecionar_arquivos as selecionar_arquivos_gui
from limpeza import converter_valor_monetario_brasileiro,limpar_numero_documento_servicos
from io import StringIO

class LayoutFilialMG(LayoutBase):
    nome = "Filial_MG"
    arquivo_saida = "comparacao_notas_filial.xlsx"
    ORDEM_COMPARACAO = ["qive-filial", "cte-filial", "servico"]

    def selecionar_arquivos(self):
        campos = [
            {"chave": "arquivo_anterior", "titulo": "Notas da análise anterior", "obrigatorio": False},
            {"chave": "arquivo_notas_entrada", "titulo": "Notas de Entrada do Consistem", "obrigatorio": False},
            {"chave": "arquivo_devolucoes", "titulo": "Notas de Devolução do Consistem", "obrigatorio": False},
            {"chave": "arquivo_qive_entrada", "titulo": "Notas de Entrada do Qive", "obrigatorio": False},
            {"chave": "arquivo_cte", "titulo": "Arquivo de CTEs do Qive", "obrigatorio": False},
            {"chave": "arquivo_servico", "titulo": "Arquivo de Notas de Serviço do Qive", "obrigatorio": False},
        ]

        return selecionar_arquivos_gui("Selecione os arquivos - Filial MG", campos)
    
    def carregar_relatorio_qive_filial(self,arquivo_qive):

        dataframe = pd.read_excel(arquivo_qive,
                                    sheet_name="relatorio",
                                    usecols=COLUNAS_IMPORTADAS["qive-filial"],
                                    dtype={
                                    "Número" :str,
                                    "Chave de Acesso" :str
                                    },
                                        na_values=valores_vazios)
        
        dataframe = dataframe.rename(
        columns={
            "Número" : "Numero_Documento",
            "Valor Total da Nota" : "Valor",
            "Nome PJ Emitente" : "Nome_Emitente",
            "Data Emissão" : "Data_Emissao",
            "Status" : "Situacao",
            "Chave de Acesso" : "ChaveAcesso"
            }
        )

        dataframe["Valor"] = converter_valor_monetario_brasileiro(dataframe["Valor"])
        dataframe["Valor"] = pd.to_numeric(dataframe["Valor"], errors='coerce')
           
        return dataframe
    
    def carregar_relatorio_cte_filial(self,arquivo_cte_filial):

        dataframe = pd.read_excel(arquivo_cte_filial,
                                    #sheet_name="relatorio",
                                    usecols=COLUNAS_IMPORTADAS["cte-filial"],
                                    dtype={
                                    "Número" :str,
                                    "Chave de Acesso" :str
                                    },
                                        na_values=valores_vazios)
        
        dataframe = dataframe.rename(
        columns={
            "Número" : "Numero_Documento",
            #"Valor Total da Nota" : "Valor",
            "Emitente" : "Nome_Emitente",
            "Emissão" : "Data_Emissao",
            "Status" : "Situacao",
            "Chave de Acesso" : "ChaveAcesso"
            }
        )

        dataframe["Valor"] = converter_valor_monetario_brasileiro(dataframe["Valor"])
        dataframe["Valor"] = pd.to_numeric(dataframe["Valor"], errors='coerce')
           
        return dataframe
        
    def carregar_relatorio_servico_filial(self,arquivo_servico):

        df_notas_servico = pd.read_excel(arquivo_servico,
                                usecols=COLUNAS_IMPORTADAS["servico"],
                                dtype={
                                    "Número" :str,
                                    "CPF/CNPJ - Prestador" :str,
                                })
        
        df_notas_servico = df_notas_servico.rename(
        columns={
            "Número" :"Numero_Documento",
            "CPF/CNPJ - Prestador" :'CNPJ/CPF',
            "Valor Serviços" : "Valor",
            "Prestador - Nome/Razão Social" : "Nome_Emitente",
            "Data de Emissão" : "Data_Emissao"
            }
        )

        # Normaliza o número na carga para que a deduplicação do reprocessamento
        # e o merge usem a mesma chave que foi salva no mês anterior (ex: 202600000054871 -> 54871).
        df_notas_servico["Numero_Documento_Original"] = df_notas_servico["Numero_Documento"]
        df_notas_servico["Numero_Documento"] = df_notas_servico["Numero_Documento"].apply(limpar_numero_documento_servicos)

        df_notas_servico["Valor"] = converter_valor_monetario_brasileiro(df_notas_servico["Valor"])
        df_notas_servico["Valor"] = pd.to_numeric(df_notas_servico["Valor"], errors='coerce')


        return df_notas_servico

    def carregar_documentos(self, arquivos):
        documentos = {
            "qive-filial": self._carregar_se_presente(arquivos, "arquivo_qive_entrada", self.carregar_relatorio_qive_filial),
            "cte-filial": self._carregar_se_presente(arquivos, "arquivo_cte", self.carregar_relatorio_cte_filial),
            "servico": self._carregar_se_presente(arquivos, "arquivo_servico", self.carregar_relatorio_servico_filial),
        }
        return {tipo: df for tipo, df in documentos.items() if df is not None}

    def _comparar_tipo(self, conferencia, tipo, df_documento, df_erp):
        if tipo == "servico":
            return conferencia.comparar_servicos_csw(df_documento, df_erp, "Situacao")
        return conferencia.comparar_sat_ou_qive_csw(df_documento, df_erp, "ChaveAcesso", "Situacao")

    def aplicar_limpeza_dados(self,dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.copy()
        dataframe = super().aplicar_limpeza_dados(dataframe)

        return dataframe