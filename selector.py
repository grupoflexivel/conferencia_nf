import pandas as pd

# lista_tabelas = pd.read_html("CTEs.xls", header=0, converters={"CHAVE_DE_ACESSO" :str})

# print(lista_tabelas)

# df = lista_tabelas[0]

# df.to_excel("CTEs_excel.xlsx",  index=False, header=False)

# print(df[["NÚMERO_CTE","SITUACAO","VALOR_TOTAL_PREST","NOME_EMITENTE","CNPJ_EMITENTE","CHAVE_DE_ACESSO"]].head())
# print(df["CHAVE_DE_ACESSO"].head())

df = pd.read_excel("NotaServico.xlsx")
print(df.dtypes)
