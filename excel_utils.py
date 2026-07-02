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

    formato_editavel = workbook.add_format({
        "locked": False
    })

    # Libera todas as células da planilha para edição
    worksheet.set_column(0, len(colunas) - 1, largura_padrao, formato_editavel)

    worksheet.freeze_panes(1, 0)

    # Reescreve somente o cabeçalho como bloqueado
    for indice_coluna, nome_coluna in enumerate(colunas):
        worksheet.write(0, indice_coluna, nome_coluna, formato_cabecalho)

    # Cria o filtro no cabeçalho
    ultima_linha = worksheet.dim_rowmax

    if ultima_linha is None:
        ultima_linha = 0

    worksheet.autofilter(
        0,
        0,
        ultima_linha,
        len(colunas) - 1
    )  

    # Protege a aba, mas só o que estiver com locked=True fica bloqueado
    worksheet.protect(
        options={
            "format_cells": True,
            "format_columns": True,
            "format_rows": True,
            "insert_columns": False,
            "delete_columns": False,
            "insert_rows": True,
            "delete_rows": True,
            "sort": True,
            "autofilter": True
        }
    )