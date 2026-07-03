import pandas as pd
from configs import COLUNAS_IMPORTADAS,valores_vazios
from limpeza import limpar_chave_acesso,limpar_cnpj_cpf,limpar_numero_documento

def carregar_relatorio_csw(arquivo: str) -> pd.DataFrame:
    return pd.read_excel(arquivo,
                                        usecols=COLUNAS_IMPORTADAS["erp"],
                                        skipfooter=1,
                                        dtype={
                                            "Documento" :str,
                                            "©CNPJ/CPF/CEI": str,
                                            "Chave Nf-e" :str
                                        },
                                        na_values=valores_vazios)


def padronizar_colunas_csw(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.rename(
        columns={
            "Documento": "Numero_Documento",
            "©CNPJ/CPF/CEI": "CNPJ/CPF",
            "Fornecedor": "NomeEmitente",
            "Chave Nf-e": "ChaveAcesso"
        }
    )

    dataframe["Numero_Documento"] = dataframe["Numero_Documento"].apply(limpar_numero_documento)

    dataframe["ChaveAcesso"] = dataframe["ChaveAcesso"].apply(limpar_chave_acesso)

    dataframe["CNPJ/CPF"] = dataframe["CNPJ/CPF"].apply(limpar_cnpj_cpf)
    
    dataframe["Valor"] = pd.to_numeric(
        dataframe["Valor"],
        errors="coerce"
    )

    return dataframe

def concatenar_relatorios_erp(arquivo_notas_entrada: str, arquivo_notas_devolucao: str) -> pd.DataFrame:
    df_notas_entrada = carregar_relatorio_csw(arquivo_notas_entrada)
    df_notas_devolucao = carregar_relatorio_csw(arquivo_notas_devolucao)

    df_erp = pd.concat(
        [df_notas_entrada,df_notas_devolucao],
        ignore_index=True
        )
    
    df_erp=padronizar_colunas_csw(df_erp)

    return df_erp