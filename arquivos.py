from configs import NOMES_ABAS_NO_EXCEL,COLUNAS_REPROCESSAMENTO
import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, messagebox

def selecionar_arquivo(titulo: str, obrigatorio: bool = True) -> str | None:
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
    dataframe = pd.read_excel(arquivo,
                              sheet_name=nome_aba,
                              usecols=colunas_importadas,
                              dtype=str)
    
    dataframe = dataframe[(dataframe["status"] == "Não lançada no CSW") & (dataframe["Alerta"].isna())]
    
    
    return dataframe

def adicionar_pendentes_mes_anterior(dataframe_atual :pd.DataFrame,
                                     arquivo_anterior :str,
                                     tipo_documento :str) -> pd.DataFrame:
    
    dataframe_mes_anterior = carregar_notas_pendentes_mes_anterior(
        arquivo=arquivo_anterior,
        nome_aba=NOMES_ABAS_NO_EXCEL[tipo_documento],
        colunas_importadas=COLUNAS_REPROCESSAMENTO[tipo_documento]
        )
    
    dataframe_atualizado =pd.concat(
        [dataframe_mes_anterior, dataframe_atual],
        ignore_index=True
    )

    if "Valor" in dataframe_atualizado.columns:
        dataframe_atualizado["Valor"] = pd.to_numeric(
            dataframe_atualizado["Valor"],
            errors="coerce"
        )

    return dataframe_atualizado