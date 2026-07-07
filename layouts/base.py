import pandas as pd
from limpeza import limpar_cnpj_cpf,limpar_numero_documento,limpar_chave_acesso
from relatorios_csw import concatenar_relatorios_erp

class LayoutBase:
    # Nome do arquivo .xlsx gerado (definido em cada unidade)
    arquivo_saida = None

    def carregar_dados(self, arquivos):
        """
        Carrega o relatório do ERP (comum a todas as unidades) e os documentos
        externos específicos da unidade.

        Retorna (dados_por_tipo, df_erp), onde dados_por_tipo é {tipo: dataframe}.
        """
        df_erp = concatenar_relatorios_erp(
            arquivos["arquivo_notas_entrada"],
            arquivos["arquivo_devolucoes"],
        )
        dados = self.carregar_documentos(arquivos)
        return dados, df_erp

    def carregar_documentos(self, arquivos):
        """Cada unidade implementa: devolve {tipo: dataframe} dos documentos externos."""
        raise NotImplementedError

    def comparar(self, conferencia, dados, df_erp):
        """Cada unidade implementa: devolve ({tipo: comparacao}, df_notas_somente_erp)."""
        raise NotImplementedError

    def aplicar_limpeza_dados(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe.copy()

        mapeamento_limpeza = {
            "CNPJ/CPF": limpar_cnpj_cpf,
            "Numero_Documento": limpar_numero_documento,
            "ChaveAcesso": limpar_chave_acesso
        }

        for coluna, funcao_limpeza in mapeamento_limpeza.items():
            if coluna in dataframe.columns:
                dataframe[coluna] = dataframe[coluna].apply(funcao_limpeza)

        return dataframe
