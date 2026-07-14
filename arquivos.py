from configs import NOMES_ABAS_NO_EXCEL,COLUNAS_REPROCESSAMENTO
import pandas as pd
import numpy as np
from comparacao import remover_documentos_duplicados_reprocessamento

def carregar_notas_pendentes_mes_anterior(arquivo: str, nome_aba:str, colunas_importadas: list):
    """
    Carrega uma aba específica de um arquivo Excel e filtra apenas as notas fiscais 
    que restaram pendentes no mês anterior.

    A função otimiza a leitura do arquivo importando apenas as colunas necessárias, 
    força todos os dados para o tipo texto (`str`) para evitar perda de zeros à esquerda, 
    e aplica um filtro rígido: retorna apenas linhas onde o status seja "Não lançada no CSW" 
    e que não possuam nenhum Alerta associado (valores nulos).

    Parameters
    ----------
    arquivo : str
        Caminho completo ou nome do arquivo Excel a ser lido.
    nome_aba : str
        O nome exato da aba (sheet) dentro do arquivo Excel onde os dados estão localizados.
    colunas_importadas : list of str
        Lista contendo os nomes das colunas que devem ser lidas (equivalente ao `usecols`). 
        Deve obrigatoriamente incluir as colunas 'status' e 'Alerta' para que o filtro funcione.

    Returns
    -------
    pd.DataFrame
        Um DataFrame filtrado contendo apenas os registros de notas pendentes e válidas 
        do período anterior.

    Raises
    ------
    KeyError
        Se as colunas 'status' ou 'Alerta' não estiverem presentes na lista `colunas_importadas` 
        ou na aba do Excel correspondente.
    FileNotFoundError
        Se o caminho especificado em `arquivo` não for encontrado.
    """
    dataframe = pd.read_excel(arquivo,
                              sheet_name=nome_aba,
                              usecols=colunas_importadas,
                              dtype=str)
    
    dataframe = dataframe[(dataframe["status"] == "Não lançada no CSW")] #& (dataframe["Alerta"].isna())]
    
    
    return dataframe

def adicionar_pendentes_mes_anterior(dataframe_atual :pd.DataFrame,
                                     arquivo_anterior :str,
                                     tipo_documento :str) -> pd.DataFrame:
    """
    Carrega os documentos pendentes do mês anterior e os consolida (concatena) 
    junto ao DataFrame do mês atual.

    A função busca o arquivo do período anterior, filtra a aba e as colunas 
    corretas com base no tipo de documento informado, empilha os dados antigos 
    abaixo dos novos e garante que a coluna de valores financeiros seja 
    corretamente tipada como numérica.

    Parameters
    ----------
    dataframe_atual : pd.DataFrame
        DataFrame contendo os dados e documentos do mês vigente.
    arquivo_anterior : str
        Caminho completo ou nome do arquivo Excel contendo os dados do mês anterior.
    tipo_documento : str
        Chave que identifica o tipo de documento que está sendo processado 
        (ex: 'NF', 'Cupom'). Utilizada para mapear os dicionários globais 
        `NOMES_ABAS_NO_EXCEL` e `COLUNAS_REPROCESSAMENTO`.

    Returns
    -------
    pd.DataFrame
        Um novo DataFrame unificado, contendo os registros do mês anterior 
        e do mês atual, com os índices resetados e a coluna 'Valor' (se existente) 
        convertida para o tipo numérico.

    Notes
    -----
    - Esta função depende de uma função auxiliar chamada `carregar_notas_pendentes_mes_anterior`.
    - Esta função depende de duas estruturas globais/constantes pré-definidas:
      `NOMES_ABAS_NO_EXCEL` (dicionário) e `COLUNAS_REPROCESSAMENTO` (dicionário).
    - Valores não numéricos na coluna 'Valor' serão convertidos em `NaN` (`errors='coerce'`)"""

    nome_aba = NOMES_ABAS_NO_EXCEL[tipo_documento]

    # O arquivo anterior pode ter sido gerado sem este tipo de documento (a aba
    # não existe). Nesse caso não há pendentes a adicionar: devolve a base atual.
    if nome_aba not in pd.ExcelFile(arquivo_anterior).sheet_names:
        return dataframe_atual

    dataframe_mes_anterior = carregar_notas_pendentes_mes_anterior(
        arquivo=arquivo_anterior,
        nome_aba=nome_aba,
        colunas_importadas=COLUNAS_REPROCESSAMENTO[tipo_documento]
        )
    
    # dataframe_atual pode ser None quando não houve arquivo novo desse tipo
    # (só existem pendências do mês anterior a reprocessar).
    partes = [
        parte for parte in (dataframe_mes_anterior, dataframe_atual)
        if parte is not None
    ]
    dataframe_atualizado = pd.concat(partes, ignore_index=True)

    dataframe_atualizado =remover_documentos_duplicados_reprocessamento(dataframe_atualizado,tipo_documento)

    if "Valor" in dataframe_atualizado.columns:
        dataframe_atualizado["Valor"] = pd.to_numeric(
            dataframe_atualizado["Valor"],
            errors="coerce"
        )

    return dataframe_atualizado