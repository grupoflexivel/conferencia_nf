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
        "text_wrap": True
    })

    worksheet.set_column(0, len(colunas) - 1, largura_padrao)
    worksheet.freeze_panes(1, 0)

    for indice_coluna, nome_coluna in enumerate(colunas):
        worksheet.write(0, indice_coluna, nome_coluna, formato_cabecalho)