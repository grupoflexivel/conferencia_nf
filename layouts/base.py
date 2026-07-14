import pandas as pd
from limpeza import limpar_cnpj_cpf,limpar_numero_documento,limpar_chave_acesso
from relatorios_csw import concatenar_relatorios_erp

class LayoutBase:
    # Nome do arquivo .xlsx gerado (definido em cada unidade)
    arquivo_saida = None

    # Ordem em que os documentos são comparados contra o ERP. O que sobra do ERP
    # depois da última comparação existente vira "Notas Somente no ERP".
    ORDEM_COMPARACAO = []

    def carregar_dados(self, arquivos):
        """
        Carrega o relatório do ERP (obrigatório, ao menos entrada ou devolução) e
        os documentos externos que foram informados.

        Retorna (dados_por_tipo, df_erp), onde dados_por_tipo é {tipo: dataframe}
        contendo APENAS os tipos cujo arquivo foi selecionado.
        """
        df_erp = concatenar_relatorios_erp(
            arquivos.get("arquivo_notas_entrada"),
            arquivos.get("arquivo_devolucoes"),
        )
        dados = self.carregar_documentos(arquivos)
        return dados, df_erp

    def _carregar_se_presente(self, arquivos, chave_arquivo, loader):
        """
        Carrega e limpa um documento externo somente se o arquivo foi informado.
        Devolve o DataFrame pronto ou None (quando o usuário não selecionou o arquivo).
        """
        caminho = arquivos.get(chave_arquivo)
        if not caminho:
            return None
        return self.aplicar_limpeza_dados(loader(caminho))

    def carregar_documentos(self, arquivos):
        """Cada unidade implementa: devolve {tipo: dataframe} só dos documentos presentes."""
        raise NotImplementedError

    def _comparar_tipo(self, conferencia, tipo, df_documento, df_erp):
        """
        Cada unidade implementa: compara um tipo de documento contra o ERP e
        devolve (comparacao, df_erp_restante).
        """
        raise NotImplementedError

    def comparar(self, conferencia, dados, df_erp):
        """
        Percorre os tipos presentes (na ORDEM_COMPARACAO), encadeando o ERP: cada
        comparação consome o ERP e passa o restante para a próxima. O que sobra no
        fim são as 'Notas Somente no ERP'.
        """
        comparacoes = {}
        df_restante = df_erp

        for tipo in self.ORDEM_COMPARACAO:
            if tipo not in dados:
                continue
            comparacao, df_restante = self._comparar_tipo(conferencia, tipo, dados[tipo], df_restante)
            comparacoes[tipo] = comparacao

        return comparacoes, df_restante

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
