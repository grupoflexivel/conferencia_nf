"""
Notas recusadas.

O usuário marca o status como "Recusada" no arquivo de conferência. A partir
daí a nota é removida da comparação, mesmo continuando a vir "Autorizada" na
base durante o mês. Como a nota some da base no mês seguinte, o registro de
recusadas se limpa sozinho: a cada execução ele só mantém as notas que ainda
existem na base atual.

Fluxo (chamado pelo main.py):
    1. coletar_recusadas       -> lê o arquivo anterior e devolve as chaves recusadas
    2. construir_aba_recusadas -> monta a aba "Notas Recusadas" (registro que se limpa sozinho)
    3. suprimir_recusadas      -> remove as recusadas da base antes do merge
"""

import pandas as pd

from configs import NOMES_ABAS_NO_EXCEL, CHAVES_DEDUPLICACAO, NOME_ABA_RECUSADAS

# Separador usado para juntar as colunas-chave numa única string (ex: "54871|111")
SEPARADOR_CHAVE = "|"

# Colunas gravadas na aba "Notas Recusadas" (registro interno, legível)
COLUNAS_LEDGER = [
    "tipo", "status", "Numero_Documento", "CNPJ/CPF", "ChaveAcesso",
    "Nome_Emitente", "Data_Emissao", "Valor", "Situacao",
]


# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------

def _construir_chave(dataframe: pd.DataFrame, colunas_chave: list) -> pd.Series:
    """
    Junta as colunas-chave numa única string por linha.

    Ex.: para Serviço (Numero_Documento + CNPJ/CPF) a linha vira "54871|111".
    Para SAT (só ChaveAcesso) vira a própria chave.
    """
    chave = dataframe[colunas_chave[0]].astype("string").str.strip().fillna("")

    for coluna in colunas_chave[1:]:
        proxima_coluna = dataframe[coluna].astype("string").str.strip().fillna("")
        chave = chave + SEPARADOR_CHAVE + proxima_coluna

    return chave


def _status_recusada(serie_status: pd.Series) -> pd.Series:
    """Verdadeiro nas linhas cujo status indica recusa (Recusada/Recusado/Recusadas...)."""
    return serie_status.astype("string").str.contains(
        r"Recusad[oa]s?", case=False, na=False, regex=True
    )


def _ler_aba(arquivo: str, nome_aba: str) -> pd.DataFrame:
    """Lê a aba como texto. Se a aba não existir, devolve um DataFrame vazio."""
    try:
        return pd.read_excel(arquivo, sheet_name=nome_aba, dtype=str)
    except (ValueError, KeyError):
        return pd.DataFrame()


def _chaves_do_dataframe(dataframe: pd.DataFrame, colunas_chave: list) -> set:
    """Conjunto de chaves de um DataFrame (vazio se faltar coluna ou não houver dados)."""
    if dataframe.empty or any(coluna not in dataframe.columns for coluna in colunas_chave):
        return set()
    return set(_construir_chave(dataframe, colunas_chave))


# ---------------------------------------------------------------------------
# Funções usadas pelo main
# ---------------------------------------------------------------------------

def coletar_recusadas(arquivo_anterior: str, tipos: list) -> dict:
    """
    Lê o arquivo anterior e devolve {tipo: conjunto_de_chaves_recusadas}.

    Junta duas origens:
      - Novas   : linhas com status "Recusada" na aba de comparação.
      - Herdadas: linhas da aba de registro "Notas Recusadas".
    """
    ledger = _ler_aba(arquivo_anterior, NOME_ABA_RECUSADAS)

    recusadas_por_tipo = {}

    for tipo in tipos:
        colunas_chave = CHAVES_DEDUPLICACAO[tipo]

        comparacao = _ler_aba(arquivo_anterior, NOMES_ABAS_NO_EXCEL[tipo])
        if "status" in comparacao.columns:
            novas = comparacao[_status_recusada(comparacao["status"])]
        else:
            novas = pd.DataFrame()

        if "tipo" in ledger.columns:
            herdadas = ledger[ledger["tipo"] == tipo]
        else:
            herdadas = pd.DataFrame()

        recusadas_por_tipo[tipo] = (
            _chaves_do_dataframe(novas, colunas_chave)
            | _chaves_do_dataframe(herdadas, colunas_chave)
        )

    return recusadas_por_tipo


def suprimir_recusadas(df_base: pd.DataFrame, tipo: str, chaves: set) -> pd.DataFrame:
    """Remove da base as linhas cuja chave esteja no conjunto de recusadas."""
    if not chaves or df_base.empty:
        return df_base

    chave_da_linha = _construir_chave(df_base, CHAVES_DEDUPLICACAO[tipo])
    return df_base[~chave_da_linha.isin(chaves)].copy()


def construir_aba_recusadas(bases_por_tipo: dict, chaves_por_tipo: dict) -> pd.DataFrame:
    """
    Monta o conteúdo da aba "Notas Recusadas" a partir da base ATUAL (antes de
    suprimir). Só entram as recusadas que ainda existem na base — é isso que faz
    o registro se limpar sozinho quando a nota some no mês seguinte.
    """
    partes = []

    for tipo, df_base in bases_por_tipo.items():
        chaves = chaves_por_tipo.get(tipo)
        if not chaves or df_base.empty:
            continue

        colunas_chave = CHAVES_DEDUPLICACAO[tipo]
        chave_da_linha = _construir_chave(df_base, colunas_chave)
        recusadas = df_base[chave_da_linha.isin(chaves)].copy()

        if recusadas.empty:
            continue

        recusadas = recusadas.drop_duplicates(subset=colunas_chave, keep="last")
        recusadas["tipo"] = tipo
        recusadas["status"] = "Recusada"
        partes.append(recusadas.reindex(columns=COLUNAS_LEDGER))

    if not partes:
        return pd.DataFrame(columns=COLUNAS_LEDGER)

    return pd.concat(partes, ignore_index=True)
