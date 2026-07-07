import pandas as pd
from layouts.base import LayoutBase
from configs import COLUNAS_IMPORTADAS,valores_vazios
from arquivos import selecionar_arquivo
from limpeza import converter_valor_monetario_brasileiro,limpar_numero_documento_servicos
from io import StringIO

class LayoutFilialMG(LayoutBase):
    nome = "Filial_MG"

    def selecionar_arquivos(self):
        arquivos = {
            "arquivo_anterior": selecionar_arquivo("Selecione o arquivo de notas do mês passado", obrigatorio=False),
                    
            "arquivo_notas_entrada": selecionar_arquivo("Selecione o arquivo de Notas de Entrada do Consistem"),

            "arquivo_devolucoes": selecionar_arquivo("Selecione o arquivo de Notas de Devolução do Consistem"),

            "arquivo_qive_entrada": selecionar_arquivo("Selecione o arquivo de Notas de Entrada do Qive"),

            "arquivo_cte": selecionar_arquivo("Selecione o arquivo de CTEs do Qive"),

            "arquivo_servico": selecionar_arquivo("Selecione o arquivo de Notas de Serviço do Qive"),
        }

        return arquivos
    
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

    def carregar_relatorios_externos_filial(self, arquivos):
        df_notas_qive_filial = self.carregar_relatorio_qive_filial(arquivos["arquivo_qive_entrada"])
        df_ctes_filial = self.carregar_relatorio_cte_filial(arquivos["arquivo_cte"])
        df_notas_servico_filial = self.carregar_relatorio_servico_filial(arquivos["arquivo_servico"])

        df_notas_qive_filial = self.aplicar_limpeza_dados(df_notas_qive_filial)
        df_ctes_filial = self.aplicar_limpeza_dados(df_ctes_filial)
        df_notas_servico_filial = self.aplicar_limpeza_dados(df_notas_servico_filial)

        return {
            "qive-filial": df_notas_qive_filial,
            "cte-filial": df_ctes_filial,
            "servico": df_notas_servico_filial
        }
    
    def aplicar_limpeza_dados(self,dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.copy()
        dataframe = super().aplicar_limpeza_dados(dataframe)

        return dataframe