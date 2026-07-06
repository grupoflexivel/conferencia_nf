import pandas as pd
import numpy as np



   
def limpar_cnpj_cpf(valor):
    if pd.isna(valor):
        return ""
    return str(valor).replace(".","").replace("/","").replace("-","")

def limpar_numero_documento(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip().replace(".0", "").lstrip("0")

def limpar_chave_acesso(valor):
    if pd.isna(valor):
        return np.nan
    return str(valor).replace("'","").replace('.','').strip()

def limpar_colunas_se_coluna_referencia_nulo(dataframe :pd.DataFrame,coluna_referencia :str, *colunas_para_limpar: str) -> pd.DataFrame:
    """
    As informações de algumas colunas somente são exibidas em situações específicas.
    Exemplo: Em casos de não serem identificadas inconsistências entre o ERP e o arquivo de referência não há necessidade de mostrar o valor do documento duas vezes.

    Essa função faz com que o texto dessas colunas "dispensaveis" seja substituido por NaN.

    """
    dataframe_copia = dataframe.copy()

    #condicao_nula = (dataframe_copia[coluna_referencia] == "")
    condicao_nula = dataframe_copia[coluna_referencia].isna()

    colunas_existentes = [
        coluna for coluna in colunas_para_limpar
        if coluna in dataframe_copia.columns
    ]

    dataframe_copia.loc[condicao_nula, colunas_existentes] = np.nan

    return dataframe_copia

def converter_valor_monetario_brasileiro(coluna: pd.Series) -> pd.Series:
    valores_originais = coluna.copy()

    # Primeiro tenta converter diretamente.
    # Isso resolve células que já vieram como número ou texto tipo "1947.55".
    valores_numericos = pd.to_numeric(valores_originais, errors="coerce")

    # Agora identifica o que NÃO conseguiu converter diretamente.
    precisa_tratar_como_texto = valores_numericos.isna() & valores_originais.notna()

    valores_tratados_texto = (
        valores_originais[precisa_tratar_como_texto]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace("\xa0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

    valores_numericos.loc[precisa_tratar_como_texto] = pd.to_numeric(
        valores_tratados_texto,
        errors="coerce"
    )

    return valores_numericos



    
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
    ...

def tratar_valor_sem_virgula(coluna_valor_doc_conferencia : pd.Series, coluna_valor_erp :pd.Series) -> pd.Series:
    """Identifica valores na coluna do documento que vieram sem separador, hoje isso ocorre no documento dos CTEs

    decimal (ex: 226001 em vez de 2260.01) comparando-os com o ERP, e corrige-os para analise
    dividindo por 100 ou 10. Valores redondos (ex: 2260) permanecem intactos.
    """

    condicoes = [
        np.isclose(coluna_valor_doc_conferencia,coluna_valor_erp *100, atol=0.1),
        np.isclose(coluna_valor_doc_conferencia,coluna_valor_erp*10, atol=0.1)
        ]
    
    resultados = [
        coluna_valor_doc_conferencia/100,
        coluna_valor_doc_conferencia/10
    ]

    return np.select(condicoes, resultados, coluna_valor_doc_conferencia)

def converter_data_mista(coluna: pd.Series) -> pd.Series:
    coluna_texto = coluna.astype("string").str.strip()

    data_convertida = pd.to_datetime(
        coluna_texto,
        format="%d/%m/%Y",
        errors="coerce"
    )

    faltantes = data_convertida.isna() & coluna_texto.notna()

    data_convertida.loc[faltantes] = pd.to_datetime(
        coluna_texto.loc[faltantes],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
    )

    faltantes = data_convertida.isna() & coluna_texto.notna()

    data_convertida.loc[faltantes] = pd.to_datetime(
        coluna_texto.loc[faltantes],
        format="%Y-%m-%d",
        errors="coerce"
    )

    faltantes = data_convertida.isna() & coluna_texto.notna()

    data_convertida.loc[faltantes] = pd.to_datetime(
        coluna_texto.loc[faltantes],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    return data_convertida

def ordenar_por_data_emissao(dataframe: pd.DataFrame,coluna_data: str) -> pd.DataFrame:
    dataframe_copia = dataframe.copy()

    dataframe_copia["_data_ordenacao"] = converter_data_mista(
        dataframe_copia[coluna_data]
    )

    dataframe_copia = dataframe_copia.sort_values(
        by="_data_ordenacao",
        ascending=True,
        na_position="last"
    )

    dataframe_copia = dataframe_copia.drop(columns=["_data_ordenacao"])

    return dataframe_copia

def limpar_numero_documento_servicos(valor) -> str:

    """Limpa e padroniza o número de uma Nota Fiscal (NF) tratada como string.

    A função remove resíduos de formatação comuns do Pandas/Excel (como o
    sufixo '.0'), filtra apenas os caracteres numéricos, aplica regras de
    negócio específicas para remoção de prefixos temporais e elimina zeros à
    esquerda.

    Regras de Negócio Aplicadas:
        1. Tratamento de Nulos: Retorna string vazia se o valor for NaN/Null.
        2. Correção de Float: Remove o sufixo '.0' apenas se estiver no final
           da string (evitando corromper zeros no meio do número).
        3. Limpeza de Caracteres: Remove pontos, traços, letras e espaços,
           mantendo apenas dígitos.
        4. Corte de Prefixo: Se o número começar com '20260' e tiver mais de
           10 dígitos, os 4 primeiros caracteres ('2026') são removidos.
        5. Zeros à Esquerda: Remove todos os zeros à esquerda do número final.

    Args:
        valor (Any): O valor original do campo da NF (pode ser str, int, float
          ou NaN).

    Returns:
        str: O número da Nota Fiscal limpo, contendo apenas dígitos, ou uma
             string vazia caso o valor seja inválido ou resulte em zero.

    Examples:
        >>> limpar_numero_nota_fiscal("20260123456")
        '0123456' -> '123456' (Removeu '2026' e o zero à esquerda)

        >>> limpar_numero_nota_fiscal("102.035")
        '102035' (Manteve o zero do meio do número)

        >>> limpar_numero_nota_fiscal("000123-A")
        '123' (Removeu letras, símbolos e zeros à esquerda)

        >>> limpar_numero_nota_fiscal(float('nan'))
        ''

         A ITACEX lança o documento como 202600000054285 mas lançam no CSW como 54285.
    """
    
    if pd.isna(valor):
        return ""

    valor = str(valor).strip()

    if valor.endswith(".0"):
        valor = valor[:-2]

    valor = "".join(caractere for caractere in valor if caractere.isdigit())

    # 4. Regra de negócio: Verifica se começa com '20260' E se possui mais de 9 dígitos,removendo o prefixo (4 primeiros)
    if valor.startswith("20260") and len(valor) > 9:
        valor = valor[4:]

    valor = valor.lstrip("0")

    return valor
