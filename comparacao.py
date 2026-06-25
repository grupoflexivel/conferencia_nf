import pandas as pd
import numpy as np

def mapear_coluna_status(dataframe: pd.DataFrame, termo="Lançada") -> pd.DataFrame:
    """
    Mapeia e atualiza a coluna 'status' com base no resultado de um merge anterior.

    Esta função utiliza a coluna técnica `_merge` (gerada automaticamente pelo pandas 
    ao utilizar a função `pd.merge(..., indicator=True)`) para identificar a origem 
    dos dados e definir se o documento foi ou não processado no sistema CSW.

    Parameters
    ----------
    dataframe : pd.DataFrame
        O DataFrame que passou por uma operação de merge recente e possui 
        a coluna '_merge'.
    termo : str, optional
        O verbo ou termo no particípio que define a ação realizada (ex: "Lançada", 
        "Integrada", "Importada"). O padrão é "Lançada".

    Returns
    -------
    pd.DataFrame
        Uma cópia do DataFrame original contendo a nova coluna 'status' preenchida 
        de acordo com as regras de mapeamento."""

    dataframe_atualizado = dataframe.copy()

    dataframe_atualizado["status"] = dataframe_atualizado["_merge"].map({
    "both": f"{termo} no CSW",
    "left_only": f"Não {termo.lower()} no CSW"
})
    return dataframe_atualizado

def analisar_valores_lançados(dataframe: pd.DataFrame ,coluna_valor_doc_conferencia : str,coluna_valor_erp: str) -> pd.DataFrame:
    """
    Essa função só pode ser chamada após a execução do merge entre os dois dataframes de interesse
    Analisa os valores dos documentos fazendo uma comparação com os valores lançados no ERP e no documento de conferência.
    Se ambos os valores baterem o status é OK e não será marcado nada.
    Caso haja uma diferença será definido como 'Nota com valores divergentes'.

     Requisitos:
    - O DataFrame precisa ter a coluna '_merge';
    - A coluna '_merge' deve ter sido criada por merge(..., indicator=True);
    - As colunas de valor informadas precisam existir no DataFrame.
    """

    colunas_obrigatorias = [
        "_merge",
        coluna_valor_doc_conferencia,
        coluna_valor_erp
    ]

    colunas_ausentes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in dataframe.columns
    ]

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {colunas_ausentes}. "
            "Verifique se o merge foi feito com indicator=True e se os nomes das colunas estão corretos."
        )

    valores_merge_validos = {"both", "left_only", "right_only"}
    valores_encontrados = set(dataframe["_merge"].dropna().unique())
    valores_invalidos = valores_encontrados - valores_merge_validos

    if valores_invalidos:
        raise ValueError(
            f"A coluna '_merge' contém valores inesperados: {valores_invalidos}. "
            "Ela deve ser gerada por pandas.merge(..., indicator=True)."
        )
    
    dataframe_copia = dataframe.copy()

    valor_divergente = ~np.isclose(dataframe_copia[coluna_valor_doc_conferencia], dataframe_copia[coluna_valor_erp],atol=0.01) & (dataframe_copia["_merge"] == "both")

    dataframe_copia["Alerta Comparador"] = pd.Series(pd.NA, index=dataframe_copia.index, dtype="object")

    dataframe_copia.loc[valor_divergente,"Alerta Comparador"] = "Documento com valores divergentes"

    return dataframe_copia

def verificar_situacao_notas_canceladas(dataframe: pd.DataFrame, coluna_situacao: str, coluna_status: str) -> pd.DataFrame:
    """
    Analisa e atualiza o status de documentos (notas) cancelados em um DataFrame,
    gerando alertas caso haja inconsistências com o sistema ERP.

    A função varre o DataFrame procurando por registros onde a `coluna_situacao` 
    indique cancelamento (via expressão regular). Com base nisso, ela aplica duas regras:
    1. Se o documento estiver cancelado na situação, mas constar como "Lançada no CSW" 
       no status, preenche a coluna 'Alerta Comparador'.
    2. Se o documento estiver cancelado e NÃO estiver lançado no CSW, atualiza a 
       coluna 'status' com o valor da situação atual.

    Parameters
    ----------
    dataframe : pd.DataFrame
        O DataFrame original contendo os dados das notas fiscais/documentos.
    coluna_situacao : str
        O nome da coluna que armazena o estado do documento (ex: 'Cancelada', 'Faturada').
        A busca aceita variações como "cancelado" ou "cancelada" (case-insensitive).
    coluna_status : str
        O nome da coluna que indica o status de lançamento no sistema (ex: 'Lançada no CSW').

    Returns
    -------
    pd.DataFrame
        Uma cópia do DataFrame original com as colunas ' Comparador' e 'status' 
        devidamente atualizadas/criadas."""
    
    dataframe_copia = dataframe.copy()

    condicao_cancelado = dataframe_copia[coluna_situacao].str.contains(
        "cancelad[oa]", case=False, na=False
    )

    condicao_lancado = dataframe_copia[coluna_status] == "Lançada no CSW"

    

    dataframe_copia["Alerta Comparador"] = np.where(
        condicao_lancado & condicao_cancelado, "Documento Lançado no ERP com status Cancelado",dataframe_copia["Alerta Comparador"]
    )

    dataframe_copia["status"] = np.where(
        condicao_cancelado & ~condicao_lancado, dataframe_copia[coluna_situacao], dataframe_copia["status"]
    )

    return dataframe_copia

def verificar_cancelamentos(dataframe: pd.DataFrame, coluna_data_cancelamento: str, coluna_situação: str) -> pd.DataFrame:
    """Identifica notas canceladas com base na presença da data de cancelamento.

    Note:
        Esta função é utilizada exclusivamente para o arquivo de **Notas de
        Serviço**, pois este é o único layout que traz a data de cancelamento
        preenchida quando a nota é cancelada. Os demais arquivos já trazem a
        coluna de situação explicitamente como "Cancelada".

    Args:
        dataframe (pd.DataFrame): O DataFrame original contendo os dados das
          notas.
        coluna_data_cancelamento (str): O nome da coluna que contém a data de
          cancelamento.
        coluna_situação (str): O nome da coluna de status onde o resultado será
          gravado.

    Returns:
        pd.DataFrame: Uma cópia do DataFrame original com a coluna de status
        atualizada com "Cancelado" ou np.nan.
    """

    dataframe_copia = dataframe.copy()

    dataframe_copia[coluna_situação] = pd.Series(dtype="string", index=dataframe_copia.index)

    condicao_cancelado = dataframe_copia[coluna_data_cancelamento].notna()

    dataframe_copia.loc[condicao_cancelado,coluna_situação] = "Cancelado" 

    return dataframe_copia


