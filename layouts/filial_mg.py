import pandas as pd
from layouts.base import LayoutBase
from configs import COLUNAS_IMPORTADAS,valores_vazios
from arquivos import selecionar_arquivo
from limpeza import converter_valor_monetario_brasileiro
from io import StringIO

class LayoutFilialMG(LayoutBase):
    nome = "Filial_MG"

    def selecionar_arquivos(self):
        arquivos = {
            "arquivo_anterior": selecionar_arquivo("Selecione o arquivo de notas do mês passado", obrigatorio=False),
                    
            "arquivo_notas_entrada": selecionar_arquivo("Selecione o arquivo de Notas de Entrada do Consistem"),

            "arquivo_devolucoes": selecionar_arquivo("Selecione o arquivo de Notas de Devolução do Consistem"),

            "arquivo_qive_entrada": selecionar_arquivo("Selecione o arquivo de Notas de Entrada do Qive"),

            #"arquivo_cte": selecionar_arquivo("Selecione o arquivo de CTEs do Qive"),

            #"arquivo_servico": selecionar_arquivo("Selecione o arquivo de Notas de Serviço do Qive"),
        }

        return arquivos
    
    def carregar_relatorio_qive_filial(self,arquivo_sat):

        df_notas_qive_filial = pd.read_excel(arquivo_sat,
                                    sheet_name="relatorio",
                                    usecols=COLUNAS_IMPORTADAS["qive-filial"],
                                    dtype={
                                    "Número" :str,
                                    "Chave de Acesso" :str
                                    },
                                        na_values=valores_vazios)
        
        df_notas_qive_filial = df_notas_qive_filial.rename(
        columns={
            "Número" : "Numero_Documento",
            "Valor Total da Nota" : "Valor",
            "Nome PJ Emitente" : "Nome_Emitente",
            "Data Emissão" : "Data_Emissao",
            "Status" : "Situacao",
            "Chave de Acesso" : "ChaveAcesso"
            }
        )

        df_notas_qive_filial["Valor"] = converter_valor_monetario_brasileiro(df_notas_qive_filial["Valor"])
        df_notas_qive_filial["Valor"] = pd.to_numeric(df_notas_qive_filial["Valor"], errors='coerce')
           
        return df_notas_qive_filial
    

    def carregar_relatorio_cte_filial(self,arquivo_cte):

        with open(arquivo_cte, "rb") as arquivo:
            conteudo_bytes = arquivo.read()

        for encoding in ["utf-8", "cp1252", "latin1"]:
            try:
                conteudo_html = conteudo_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        lista_tabelas_ctes = pd.read_html(StringIO(conteudo_html), header=0, converters={"CHAVE_DE_ACESSO" :str},flavor="html5lib")
        df_ctes = lista_tabelas_ctes[0][COLUNAS_IMPORTADAS["cte"]].astype({"CHAVE_DE_ACESSO" :str})

        df_ctes = df_ctes.rename(
        columns={
            "CHAVE_DE_ACESSO" : "ChaveAcesso",
            "NÚMERO_CTE" : "Numero_Documento",
            "VALOR_TOTAL_PREST" : "Valor",
            "NOME_EMITENTE" : "Nome_Emitente",
            "SITUACAO" : "Situacao",
            "DATA_EMISSÃO" : "Data_Emissao"
            }
        )

        return df_ctes
    
    def carregar_relatorio_servico_matriz(self,arquivo_servico):

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
        
        df_notas_servico["Valor"] = converter_valor_monetario_brasileiro(df_notas_servico["Valor"])
        df_notas_servico["Valor"] = pd.to_numeric(df_notas_servico["Valor"], errors='coerce')

        
        return df_notas_servico

    def carregar_relatorios_externos_filial(self, arquivos):
        df_notas_qive_filial = self.carregar_relatorio_qive_filial(arquivos["arquivo_qive_entrada"])
        #df_ctes = self.carregar_relatorio_cte_matriz(arquivos["arquivo_cte"])
        #df_notas_servico = self.carregar_relatorio_servico_matriz(arquivos["arquivo_servico"])

        #df_notas_qive_filial = self.aplicar_limpeza_dados(df_notas_qive_filial)
        #df_ctes = self.aplicar_limpeza_dados(df_ctes)
        #df_notas_servico = self.aplicar_limpeza_dados(df_notas_servico)

        return {
            "qive-filial": df_notas_qive_filial,
            #"cte": df_ctes,
            #"servico": df_notas_servico
        }
    
    def aplicar_limpeza_dados(self,dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.copy()
        dataframe = super().aplicar_limpeza_dados(dataframe)

        return dataframe