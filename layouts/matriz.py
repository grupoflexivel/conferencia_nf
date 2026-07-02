import pandas as pd
from layouts.base import LayoutBase
from configs import COLUNAS_IMPORTADAS,valores_vazios
from arquivos import selecionar_arquivo
from limpeza import converter_valor_monetario_brasileiro,limpar_cnpj_cpf,limpar_numero_documento,limpar_chave_acesso,limpar_numero_documento_servicos
from io import StringIO

class LayoutMatriz(LayoutBase):
    nome = "Matriz"

    def selecionar_arquivos(self):
        arquivos = {
            "arquivo_anterior": selecionar_arquivo("Selecione o arquivo de notas do mês passado", obrigatorio=False),
                    
            "arquivo_notas_entrada": selecionar_arquivo("Selecione o arquivo de Notas de Entrada do Consistem"),

            "arquivo_devolucoes": selecionar_arquivo("Selecione o arquivo de Notas de Devolução do Consistem"),

            "arquivo_sat": selecionar_arquivo("Selecione o arquivo SAT"),

            "arquivo_cte": selecionar_arquivo("Selecione o arquivo de CTEs"),

            "arquivo_servico": selecionar_arquivo("Selecione o arquivo de Notas de Serviço"),
        }

        return arquivos
    
    def carregar_relatorio_sat_matriz(self,arquivo_sat):

        df_notas_sat = pd.read_excel(arquivo_sat,
                                    usecols=COLUNAS_IMPORTADAS["sat"],
                                    dtype={
                                        "NumeroDocumento" :str,
                                    "ChaveAcesso" :str
                                        },
                                        na_values=valores_vazios)
        
        df_notas_sat = df_notas_sat.rename(
        columns={
            "NumeroDocumento" : "Numero_Documento",
            #"CnpjOuCpfDoEmitente" : "CNPJ",
            "ValorTotalNota" : "Valor",
            }
        )    
        return df_notas_sat


    def carregar_relatorio_cte_matriz(self,arquivo_cte):

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
            #"CNPJ_EMITENTE" : "CNPJ",
            "NÚMERO_CTE" : "Numero_Documento",
            "VALOR_TOTAL_PREST" : "Valor"
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
            "Prestador - Nome/Razão Social" : "Nome Prestador"
            }
        )
        
        df_notas_servico["Valor"] = converter_valor_monetario_brasileiro(df_notas_servico["Valor"])
        df_notas_servico["Valor"] = pd.to_numeric(df_notas_servico["Valor"], errors='coerce')

        
        return df_notas_servico

    def carregar_relatorios_externos(self, arquivos):
        df_notas_sat = self.carregar_relatorio_sat_matriz(arquivos["arquivo_sat"])
        df_ctes = self.carregar_relatorio_cte_matriz(arquivos["arquivo_cte"])
        df_notas_servico = self.carregar_relatorio_servico_matriz(arquivos["arquivo_servico"])

        df_notas_sat = self.aplicar_limpeza_dados(df_notas_sat)
        df_ctes = self.aplicar_limpeza_dados(df_ctes)
        df_notas_servico = self.aplicar_limpeza_dados(df_notas_servico)

        return {
            "sat": df_notas_sat,
            "cte": df_ctes,
            "servico": df_notas_servico
        }
    
    def aplicar_limpeza_dados(self,dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.copy()
        dataframe = super().aplicar_limpeza_dados(dataframe)

        return dataframe