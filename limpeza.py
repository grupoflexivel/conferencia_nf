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
    """Limpa, padroniza e extrai apenas os dígitos numéricos de um documento.

    Esta função é utilizada para tratar a diferença entre o código das notas de serviço lançadas no CSW e o que vem do documento de referência.
    Ela remove nulos, pontuações, resíduos de conversão para float (.0), zeros à esquerda e trata um caso específico
    de strings com 15 dígitos (removendo os 4 primeiros caracteres).

    Args:
        valor (Any): O valor bruto do documento a ser limpo. Pode ser string,
            número (int/float) ou valores nulos (None/NaN).

    Returns:
        str: Uma string contendo apenas os números limpos e padronizados,
            ou uma string vazia caso o valor de entrada seja nulo.

    Exemplos:
        >>> limpar_numero_documento_servicos(" 123.456-78 ")
        '12345678'
        >>> limpar_numero_documento_servicos(98765.0)
        '98765'
        >>> limpar_numero_documento_servicos("000123")
        '123'
        >>> limpar_numero_documento_servicos("111122223333444") # 15 dígitos
        '22223333444'
        
        A ITACEX lança o documento como 202600000054285 mas lançam no CSW como 54285.
    """
    if pd.isna(valor):
        return ""

    valor = str(valor).strip().replace(".0", "")

    valor = "".join(caractere for caractere in valor if caractere.isdigit())

    # 4. Regra de negócio: Se o resultado tem 15 dígitos, remove o prefixo (4 primeiros)
    if len(valor) == 15:
        valor = valor[4:]

    return valor.lstrip("0")
