from configs import NOMES_ABAS_NO_EXCEL,COLUNAS_REPROCESSAMENTO
import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, messagebox
from comparacao import remover_documentos_duplicados_reprocessamento

def selecionar_arquivo(titulo: str, obrigatorio: bool = True) -> str | None:
    """
    Abre uma interface gráfica (GUI) para que o usuário selecione um arquivo Excel.

    A função inicializa uma instância oculta do Tkinter, exibe uma mensagem informativa 
    com as instruções (título) e abre a janela de busca de arquivos filtrando por 
    extensões do Excel. Caso o arquivo seja obrigatório e o usuário feche a janela 
    sem escolher, um erro é lançado.

    Parameters
    ----------
    titulo : str
        Mensagem ou instrução que será exibida na caixa de diálogo e no topo da 
        janela de seleção (ex: "Selecione o arquivo de faturamento do mês anterior").
    obrigatorio : bool, optional
        Define se a seleção do arquivo é estritamente necessária para a execução do 
        sistema. Se True, a falta de seleção gera uma exceção. O padrão é True.

    Returns
    -------
    str | None
        O caminho completo do arquivo selecionado em formato string. Retorna None 
        apenas se `obrigatorio` for False e o usuário cancelar a seleção.

    Raises
    ------
    ValueError
        Se `obrigatorio` for True e o usuário cancelar ou fechar a janela de 
        seleção sem escolher um arquivo válido.
    """
    janela = Tk()
    janela.withdraw()  # Esconde a janela principal do Tkinter

    messagebox.showinfo("Selecionar arquivo", titulo)

    caminho_arquivo = filedialog.askopenfilename(
        title=titulo,
        filetypes=[
            ("Arquivos Excel", "*.xlsx *.xls"),
            ("Todos os arquivos", "*.*")
        ]
    )

    janela.destroy()

    if not caminho_arquivo and obrigatorio:
        raise ValueError(f"Nenhum arquivo selecionado para: {titulo}")
    
    if not caminho_arquivo:
        return None

    return caminho_arquivo

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
    
    dataframe_mes_anterior = carregar_notas_pendentes_mes_anterior(
        arquivo=arquivo_anterior,
        nome_aba=NOMES_ABAS_NO_EXCEL[tipo_documento],
        colunas_importadas=COLUNAS_REPROCESSAMENTO[tipo_documento]
        )
    
    dataframe_atualizado =pd.concat(
        [dataframe_mes_anterior, dataframe_atual],
        ignore_index=True
    )

    dataframe_atualizado =remover_documentos_duplicados_reprocessamento(dataframe_atualizado,tipo_documento)

    if "Valor" in dataframe_atualizado.columns:
        dataframe_atualizado["Valor"] = pd.to_numeric(
            dataframe_atualizado["Valor"],
            errors="coerce"
        )

    return dataframe_atualizado