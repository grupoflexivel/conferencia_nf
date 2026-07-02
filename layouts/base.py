import pandas as pd
from limpeza import limpar_cnpj_cpf,limpar_numero_documento,limpar_chave_acesso

class LayoutBase:
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