from pathlib import Path

import pandas as pd

from arquivos import adicionar_pendentes_mes_anterior
from configs import COLUNAS_SALVAS, NOMES_ABAS_NO_EXCEL
from excel_utils import formatar_planilha_excel
from layouts.filial_mg import LayoutFilialMG
from layouts.matriz import LayoutMatriz
from motor import ConferenciaNotaFiscal
from recusadas import coletar_recusadas, construir_aba_recusadas, suprimir_recusadas


LAYOUTS = {
    "Matriz": LayoutMatriz,
    "Filial": LayoutFilialMG,
}


class NenhumDocumentoError(ValueError):
    """Indica que não há documento novo ou pendente para comparar."""


def exportar_relatorio(caminho, comparacoes, df_notas_somente_erp, df_recusadas):
    """Escreve o workbook final e aplica a formatação das abas."""
    with pd.ExcelWriter(caminho, engine="xlsxwriter") as writer:
        for tipo, comparacao in comparacoes.items():
            comparacao.to_excel(
                writer,
                columns=COLUNAS_SALVAS[tipo],
                sheet_name=NOMES_ABAS_NO_EXCEL[tipo],
                index=False,
            )

        df_notas_somente_erp.to_excel(writer, sheet_name="Notas Somente no ERP", index=False)
        df_recusadas.to_excel(writer, sheet_name="Notas Recusadas", index=False)

        for tipo in comparacoes:
            formatar_planilha_excel(writer, COLUNAS_SALVAS[tipo], NOMES_ABAS_NO_EXCEL[tipo])
        formatar_planilha_excel(writer, df_notas_somente_erp.columns.tolist(), "Notas Somente no ERP")
        formatar_planilha_excel(writer, df_recusadas.columns.tolist(), "Notas Recusadas")


def processar_conferencia(layout, arquivos, caminho_saida=None):
    """Executa o pipeline de conferência sem depender de interface gráfica."""
    if not (arquivos.get("arquivo_notas_entrada") or arquivos.get("arquivo_devolucoes")):
        raise ValueError(
            "Carregue ao menos um relatório do ERP "
            "(Notas de Entrada ou de Devolução do Consistem)."
        )

    dados, df_notas_erp = layout.carregar_dados(arquivos)
    arquivo_anterior = arquivos.get("arquivo_anterior")

    if arquivo_anterior:
        abas_anteriores = pd.ExcelFile(arquivo_anterior).sheet_names
        for tipo in layout.ORDEM_COMPARACAO:
            if NOMES_ABAS_NO_EXCEL[tipo] not in abas_anteriores:
                continue
            dados[tipo] = adicionar_pendentes_mes_anterior(
                dados.get(tipo), arquivo_anterior, tipo
            )

        dados = {
            tipo: dataframe
            for tipo, dataframe in dados.items()
            if dataframe is not None and not dataframe.empty
        }

    if not dados:
        raise NenhumDocumentoError(
            "Carregue ao menos um relatório externo, ou um arquivo anterior "
            "com pendências, para comparar."
        )

    chaves_recusadas = (
        coletar_recusadas(arquivo_anterior, list(dados))
        if arquivo_anterior
        else {tipo: set() for tipo in dados}
    )
    df_recusadas = construir_aba_recusadas(dados, chaves_recusadas)

    for tipo in dados:
        dados[tipo] = suprimir_recusadas(dados[tipo], tipo, chaves_recusadas[tipo])

    conferencia = ConferenciaNotaFiscal()
    comparacoes, df_notas_somente_erp = layout.comparar(
        conferencia, dados, df_notas_erp
    )

    for tipo in comparacoes:
        comparacoes[tipo] = conferencia.formatar_e_limpar_colunas_para_exportar(
            comparacoes[tipo]
        )

    destino = Path(caminho_saida or layout.arquivo_saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    exportar_relatorio(destino, comparacoes, df_notas_somente_erp, df_recusadas)
    return destino
