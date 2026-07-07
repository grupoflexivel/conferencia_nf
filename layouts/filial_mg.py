import pandas as pd
from layouts.base import LayoutBase
from configs import COLUNAS_IMPORTADAS,valores_vazios
from seletor_unidade_claude import selecionar_arquivos as selecionar_arquivos_gui
from limpeza import converter_valor_monetario_brasileiro,limpar_numero_documento_servicos
from io import StringIO

class LayoutFilialMG(LayoutBase):
    nome = "Filial_MG"
    arquivo_saida = "comparacao_notas_filial.xlsx"

    def selecionar_arquivos(self):
        campos = [
            {"chave": "arquivo_anterior", "titulo": "Notas da análise anterior", "obrigatorio": False},
            {"chave": "arquivo_notas_entrada", "titulo": "Notas de Entrada do Consistem", "obrigatorio": True},
            {"chave": "arquivo_devolucoes", "titulo": "Notas de Devolução do Consistem", "obrigatorio": True},
            {"chave": "arquivo_qive_entrada", "titulo": "Notas de Entrada do Qive", "obrigatorio": True},
            {"chave": "arquivo_cte", "titulo": "Arquivo de CTEs do Qive", "obrigatorio": True},
            {"chave": "arquivo_servico", "titulo": "Arquivo de Notas de Serviço do Qive", "obrigatorio": True},
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

    def comparar(self, conferencia, dados, df_erp):
        comparacao_qive, df_erp = conferencia.comparar_sat_ou_qive_csw(dados["qive-filial"], df_erp, "ChaveAcesso", "Situacao")
        comparacao_cte, df_erp = conferencia.comparar_sat_ou_qive_csw(dados["cte-filial"], df_erp, "ChaveAcesso", "Situacao")
        comparacao_servico, df_notas_somente_erp = conferencia.comparar_servicos_csw(dados["servico"], df_erp, "Situacao")

        comparacoes = {
            "qive-filial": comparacao_qive,
            "cte-filial": comparacao_cte,
            "servico": comparacao_servico,
        }
        return comparacoes, df_notas_somente_erp

    def aplicar_limpeza_dados(self,dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.copy()
        dataframe = super().aplicar_limpeza_dados(dataframe)

        return dataframe