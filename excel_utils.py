def formatar_planilha_excel(
    writer,
    colunas: list,
    nome_aba: str,
    largura_padrao: int = 28
) -> None:
    workbook = writer.book
    worksheet = writer.sheets[nome_aba]

    formato_cabecalho = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "text_wrap": True,
         "locked": True
    })

    formato_bloqueado = workbook.add_format({
        "locked": True
    })

    formato_editavel = workbook.add_format({
        "locked": False
    })

    worksheet.set_column(0, len(colunas) - 1, largura_padrao, formato_bloqueado)
    worksheet.freeze_panes(1, 0)

    for indice_coluna, nome_coluna in enumerate(colunas):
        worksheet.write(0, indice_coluna, nome_coluna, formato_cabecalho)

    if "Observações" in colunas:
        indice_observacoes = colunas.index("Observações")

        worksheet.set_column(
            indice_observacoes,
            indice_observacoes,
            largura_padrao,
            formato_editavel
        )

        worksheet.protect(
        options={
            "format_cells": False,
            "format_columns": False,
            "format_rows": False,
            "insert_columns": False,
            "delete_columns": False,
            "insert_rows": False,
            "delete_rows": False,
            "sort": True,
            "autofilter": True
        }
    )
        
        