import pandas as pd
import numpy as np

def mapear_coluna_status(dataframe: pd.DataFrame, termo="Lançada") -> pd.DataFrame:

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

    dataframe_copia["Alerta"] = pd.Series(pd.NA, index=dataframe_copia.index, dtype="object")

    dataframe_copia.loc[valor_divergente,"Alerta"] = "Documento com valores divergentes"

    return dataframe_copia

def verificar_situacao_notas_canceladas(dataframe: pd.DataFrame, coluna_situacao: str, coluna_status: str) -> pd.DataFrame:
    
    dataframe_copia = dataframe.copy()

    condicao_cancelado = dataframe_copia[coluna_situacao].str.contains(
        "cancelad[oa]", case=False, na=False
    )

    condicao_lancado = dataframe_copia[coluna_status] == "Lançada no CSW"

    

    dataframe_copia["Alerta"] = np.where(
        condicao_lancado & condicao_cancelado, "Documento Lançado no ERP com status Cancelado",dataframe_copia["Alerta"]
    )

    dataframe_copia["status"] = np.where(
        condicao_cancelado & ~condicao_lancado, dataframe_copia[coluna_situacao], dataframe_copia["status"]
    )

    return dataframe_copia