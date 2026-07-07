import pandas as pd
from layouts.base import LayoutBase
from configs import COLUNAS_IMPORTADAS,valores_vazios
from seletor_unidade_claude import selecionar_arquivos as selecionar_arquivos_gui
from limpeza import converter_valor_monetario_brasileiro,limpar_numero_documento_servicos
from io import StringIO

class LayoutMatriz(LayoutBase):
    nome = "Matriz"
    arquivo_saida = "comparacao_notas.xlsx"

    def selecionar_arquivos(self):
        campos = [
            {"chave": "arquivo_anterior", "titulo": "Notas da análise anterior", "obrigatorio": False},
            {"chave": "arquivo_notas_entrada", "titulo": "Notas de Entrada do Consistem", "obrigatorio": True},
            {"chave": "arquivo_devolucoes", "titulo": "Notas de Devolução do Consistem", "obrigatorio": True},
            {"chave": "arquivo_sat", "titulo": "Arquivo SAT", "obrigatorio": True},
            {"chave": "arquivo_cte", "titulo": "Arquivo de CTEs", "obrigatorio": True},
            {"chave": "arquivo_servico", "titulo": "Arquivo de Notas de Serviço", "obrigatorio": True},
        ]

        return selecionar_arquivos_gui("Selecione os arquivos - Matriz", campos)
    
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
            "ValorTotalNota" : "Valor",
            "NomeEmitente" : "Nome_Emitente",
            "DataEmissao" : "Data_Emissao"
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

        # Normaliza o número na carga para que a deduplicação do reprocessamento
        # e o merge usem a mesma chave que foi salva no mês anterior (ex: 202600000054871 -> 54871).
        df_notas_servico["Numero_Documento_Original"] = df_notas_servico["Numero_Documento"]
        df_notas_servico["Numero_Documento"] = df_notas_servico["Numero_Documento"].apply(limpar_numero_documento_servicos)

        df_notas_servico["Valor"] = converter_valor_monetario_brasileiro(df_notas_servico["Valor"])
        df_notas_servico["Valor"] = pd.to_numeric(df_notas_servico["Valor"], errors='coerce')


        return df_notas_servico

    def carregar_documentos(self, arquivos):
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

    def comparar(self, conferencia, dados, df_erp):
        comparacao_sat, df_erp = conferencia.comparar_sat_ou_qive_csw(dados["sat"], df_erp, "ChaveAcesso", "Situacao")
        comparacao_cte, df_erp = conferencia.comparar_cte_matriz_csw(dados["cte"], df_erp, "ChaveAcesso", "Situacao")
        comparacao_servico, df_notas_somente_erp = conferencia.comparar_servicos_csw(dados["servico"], df_erp, "Situacao")

        comparacoes = {
            "sat": comparacao_sat,
            "cte": comparacao_cte,
            "servico": comparacao_servico,
        }
        return comparacoes, df_notas_somente_erp

    def aplicar_limpeza_dados(self,dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.copy()
        dataframe = super().aplicar_limpeza_dados(dataframe)

        return dataframe