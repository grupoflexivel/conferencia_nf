import pandas as pd
import numpy as np
import warnings
from tkinter import Tk, filedialog, messagebox
import time



# Silencia os avisos chatos do openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

#Configurações Globais
valores_vazios = ['',' ', 'NaN', 'nan', 'Null', 'NULL']

#Configuração de Colunas
COLUNAS_IMPORTADAS = {
    "sat": ['NumeroDocumento','Situacao','ValorTotalNota','NomeEmitente','ChaveAcesso', 'DataEmissao'],
    "erp": ['Documento','Valor','Chave Nf-e','Cód. Par', 'Parâmetro','©CNPJ/CPF/CEI', 'Data Emissão'],
    "cte": ['NÚMERO_CTE','SITUACAO','VALOR_TOTAL_PREST','NOME_EMITENTE','CHAVE_DE_ACESSO', 'DATA_EMISSÃO'],
    "servico": ['Número','CPF/CNPJ - Prestador','Valor Serviços','Prestador - Nome/Razão Social', 'Data de Emissão']
}

COLUNAS_SALVAS = {
    "sat": ['Situacao','ChaveAcesso','NomeEmitente','Numero_Documento','Valor','Numero_Documento_CSW','Valor_CSW',
                    'Cód. Par','Parâmetro', 'DataEmissao','status','Alerta' ],
    "cte": ["Numero_Documento","SITUACAO","Valor","NOME_EMITENTE","ChaveAcesso","Numero_Documento_CSW","Valor_CSW",
            "Cód. Par","Parâmetro","DATA_EMISSÃO","status","Alerta"],
    "servico": ["Numero_Documento","CNPJ/CPF","Nome Prestador","Valor","Numero_Documento_CSW","Valor_CSW",
            "Cód. Par","Parâmetro","ChaveAcesso","CNPJ/CPF_CSW","Data de Emissão","status","Alerta"]
}

COLUNAS_REPROCESSAMENTO = {
    "sat": ['Situacao','ChaveAcesso','NomeEmitente','Numero_Documento','Valor','DataEmissao','status','Alerta' ],

    "cte": ["Numero_Documento","SITUACAO","Valor","NOME_EMITENTE","ChaveAcesso","DATA_EMISSÃO","status","Alerta"],

    "servico": ["Numero_Documento","CNPJ/CPF","Nome Prestador","Valor","ChaveAcesso","Data de Emissão","status","Alerta"]

}

NOMES_ABAS_NO_EXCEL = {
    "sat": "Comparação SAT vs CSW",
    "cte": "Comparação CTE vs CSW",
    "servico": "Comparacao Serviços vs CSW"
}

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
        [dataframe_atual, dataframe_mes_anterior],
        ignore_index=True
    )

    if "Valor" in dataframe_atualizado.columns:
        dataframe_atualizado["Valor"] = pd.to_numeric(
            dataframe_atualizado["Valor"],
            errors="coerce"
        )

    return dataframe_atualizado

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


def analisar_valores_lançados(dataframe: pd.DataFrame ,coluna_valor_doc_conferencia : str,coluna_valor_erp: str) -> pd.DataFrame:
    """
    Essa função só pode ser chamada após a execução do merge entre os dois dataframes de interesse
    Analisa os valores dos documentos fazendo uma comparação com os valores lançados no ERP e no documento de conferência.
    Se ambos os valores baterem o status é OK e não será marcado nada.
    Caso haja uma diferença será definido como 'Nota com valores divergentes'.

     Requisitos:
    - O DataFrame precisa ter a coluna '_merge';
    - A coluna '_merge' deve ter sido criada por merge(..., indicator=True);
    - As colunas de valor informadas precisam existir no DataFrame.
    """

    colunas_obrigatorias = [
        "_merge",
        coluna_valor_doc_conferencia,
        coluna_valor_erp
    ]

    colunas_ausentes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in dataframe.columns
    ]

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {colunas_ausentes}. "
            "Verifique se o merge foi feito com indicator=True e se os nomes das colunas estão corretos."
        )

    valores_merge_validos = {"both", "left_only", "right_only"}
    valores_encontrados = set(dataframe["_merge"].dropna().unique())
    valores_invalidos = valores_encontrados - valores_merge_validos

    if valores_invalidos:
        raise ValueError(
            f"A coluna '_merge' contém valores inesperados: {valores_invalidos}. "
            "Ela deve ser gerada por pandas.merge(..., indicator=True)."
        )
    
    dataframe_copia = dataframe.copy()

    valor_divergente = ~np.isclose(dataframe_copia[coluna_valor_doc_conferencia], dataframe_copia[coluna_valor_erp],atol=0.01) & (dataframe_copia["_merge"] == "both")

    dataframe_copia["Alerta"] = pd.Series(pd.NA, index=dataframe_copia.index, dtype="object")

    dataframe_copia.loc[valor_divergente,"Alerta"] = "Documento com valores divergentes"

    return dataframe_copia


def mapear_coluna_status(dataframe: pd.DataFrame, termo="Lançada") -> pd.DataFrame:

    dataframe_atualizado = dataframe.copy()

    dataframe_atualizado["status"] = dataframe_atualizado["_merge"].map({
    "both": f"{termo} no CSW",
    "left_only": f"Não {termo.lower()} no CSW"
})
    return dataframe_atualizado
    
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

def verificar_situacao_notas_canceladas(dataframe: pd.DataFrame, coluna_situacao: str, coluna_status: str) -> pd.DataFrame:
    
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


#---------------------------------------------------------------------------------------------------
#Inicio da aplicação
#---------------------------------------------------------------------------------------------------
arquivo_anterior = selecionar_arquivo("Selecione o arquivo de notas do mês passado", obrigatorio=False)
arquivo_notas_entrada = selecionar_arquivo("Selecione o arquivo de Notas de Entrada do Consistem")
arquivo_devolucoes = selecionar_arquivo("Selecione o arquivo de Notas de Devolução do Consistem")
arquivo_sat = selecionar_arquivo("Selecione o arquivo SAT")
arquivo_cte = selecionar_arquivo("Selecione o arquivo de CTEs")
arquivo_servico = selecionar_arquivo("Selecione o arquivo de Notas de Serviço")


df_notas_entrada_erp = pd.read_excel(arquivo_notas_entrada,
                                     usecols=COLUNAS_IMPORTADAS["erp"],
                                     skipfooter=1,
                                     dtype={
                                         "Documento" :str,
                                         "©CNPJ/CPF/CEI": str,
                                         "Chave Nf-e" :str
                                     },
                                     na_values=valores_vazios)

df_notas_devolucoes_erp = pd.read_excel(arquivo_devolucoes,
                                        skipfooter=1,
                             usecols=COLUNAS_IMPORTADAS["erp"],
                             dtype={
                                 "Documento" :str,
                                 "©CNPJ/CPF/CEI": str,
                                 "Chave Nf-e" :str
                             },
                             na_values=valores_vazios)

#Concatena as duas listagens do excel que vem do Consistem
df_notas_erp = pd.concat([df_notas_entrada_erp,df_notas_devolucoes_erp], ignore_index=True)

df_notas_sat = pd.read_excel(arquivo_sat,
                                   usecols=COLUNAS_IMPORTADAS["sat"],
                                   dtype={
                                    "NumeroDocumento" :str,
                                   "ChaveAcesso" :str
                                    },
                                    na_values=valores_vazios)

lista_tabelas_ctes = pd.read_html(arquivo_cte, header=0, converters={"CHAVE_DE_ACESSO" :str})
df_ctes = lista_tabelas_ctes[0][COLUNAS_IMPORTADAS["cte"]].astype({"CHAVE_DE_ACESSO" :str})

df_notas_servico = pd.read_excel(arquivo_servico,
                                 usecols=COLUNAS_IMPORTADAS["servico"],
                                 dtype={
                                     "Número" :str,
                                     "CPF/CNPJ - Prestador" :str,
                                 })

#Formata o nome das colunas
df_notas_erp = df_notas_erp.rename(
    columns={
        "Documento" : "Numero_Documento",
        "©CNPJ/CPF/CEI" : "CNPJ/CPF",
        "Fornecedor" : "NomeEmitente",
        "Chave Nf-e" : "ChaveAcesso"
    }
)
df_notas_sat = df_notas_sat.rename(
    columns={
        "NumeroDocumento" : "Numero_Documento",
        #"CnpjOuCpfDoEmitente" : "CNPJ",
        "ValorTotalNota" : "Valor",
    }
)

df_ctes = df_ctes.rename(
    columns={
        "CHAVE_DE_ACESSO" : "ChaveAcesso",
        #"CNPJ_EMITENTE" : "CNPJ",
        "NÚMERO_CTE" : "Numero_Documento",
        "VALOR_TOTAL_PREST" : "Valor"
    }
)

df_notas_servico = df_notas_servico.rename(
    columns={
        "Número" :"Numero_Documento",
        "CPF/CNPJ - Prestador" :'CNPJ/CPF',
        "Valor Serviços" : "Valor",
        "Prestador - Nome/Razão Social" : "Nome Prestador"
    }
)


#Converte coluna object para float64
df_notas_erp["Valor"] = pd.to_numeric(df_notas_erp["Valor"], errors='coerce')

df_notas_servico["Valor"] = converter_valor_monetario_brasileiro(df_notas_servico["Valor"])

df_notas_servico["Valor"] = pd.to_numeric(df_notas_servico["Valor"], errors='coerce')

#Aplicar as funções de formatação

dfs = {
    "df_notas_sat" : df_notas_sat,
    "df_notas_erp" : df_notas_erp,
    "df_ctes" : df_ctes,
    "df_notas_servico" : df_notas_servico
}

mapeamento_limpeza = {
    "CNPJ/CPF": limpar_cnpj_cpf,
    "Numero_Documento": limpar_numero_documento,
    "ChaveAcesso": limpar_chave_acesso
}

for nome, df in dfs.items():
    # Percorre o mapeamento e só aplica se a coluna existir no df
    for coluna, funcao_limpeza in mapeamento_limpeza.items():
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(funcao_limpeza)

if arquivo_anterior:

    df_notas_sat = adicionar_pendentes_mes_anterior(df_notas_sat,arquivo_anterior,"sat")
    df_ctes = adicionar_pendentes_mes_anterior(df_ctes,arquivo_anterior,"cte")
    df_notas_servico = adicionar_pendentes_mes_anterior(df_notas_servico,arquivo_anterior,"servico")


#Usa o SAT como base e vê o que foi lançado no Consistem ou não
comparacao_sat_erp = df_notas_sat.merge(
    df_notas_erp,
    on="ChaveAcesso",
    how="left",
    suffixes=("", "_CSW"), #Não modifico o nome da primeira coluna
    indicator=True
)

#Cria a coluna status com base numa lógica pré definida.
comparacao_sat_erp = mapear_coluna_status(comparacao_sat_erp)
comparacao_sat_erp = analisar_valores_lançados(comparacao_sat_erp,"Valor","Valor_CSW")
comparacao_sat_erp = verificar_situacao_notas_canceladas(comparacao_sat_erp,"Situacao","status")

#Considera somente as notas que sobraram no CSW para continuar a comparação.
df_notas_erp = df_notas_erp[~df_notas_erp['ChaveAcesso'].isin(df_notas_sat['ChaveAcesso'])]

#Usa as notas que sobraram no CSW e verifica quais são CTEs
comparacao_cte_erp = df_ctes.merge(
    df_notas_erp,
    on="ChaveAcesso",
    how="left",
    suffixes=("","_CSW"), #Não modifico o nome da primeira coluna
    indicator=True
)

comparacao_cte_erp = mapear_coluna_status(comparacao_cte_erp)
comparacao_cte_erp["Valor"] = tratar_valor_sem_virgula(comparacao_cte_erp["Valor"], comparacao_cte_erp["Valor_CSW"])
comparacao_cte_erp = analisar_valores_lançados(comparacao_cte_erp,"Valor","Valor_CSW")
comparacao_cte_erp = verificar_situacao_notas_canceladas(comparacao_cte_erp,"SITUACAO","status")

#Considera somente as notas que sobraram no CSW para continuar a comparação.
df_notas_erp = df_notas_erp[~df_notas_erp["ChaveAcesso"].isin(comparacao_cte_erp["ChaveAcesso"])]

#Usa as notas que sobraram no CSW e verifica quais são Notas de Serviço
df_notas_erp["ChaveComparadora"] = df_notas_erp["Numero_Documento"] + "-" + df_notas_erp["CNPJ/CPF"]
df_notas_servico["ChaveComparadora"] = df_notas_servico["Numero_Documento"] + "-" + df_notas_servico["CNPJ/CPF"]

comparacao_notas_servico_erp = df_notas_servico.merge(
    df_notas_erp,
    on="ChaveComparadora",
    how="left",
    suffixes=("","_CSW"), #Não modifico o nome da primeira coluna
    indicator=True
)

comparacao_notas_servico_erp = mapear_coluna_status(comparacao_notas_servico_erp)

comparacao_notas_servico_erp = analisar_valores_lançados(comparacao_notas_servico_erp,"Valor","Valor_CSW")

df_notas_somente_erp = df_notas_erp[~df_notas_erp["ChaveComparadora"].isin(comparacao_notas_servico_erp["ChaveComparadora"])]
df_notas_somente_erp = df_notas_somente_erp.drop(columns=["ChaveComparadora"])

#Salvar somente as colunas desejadas
colunas_para_limpar = ['Numero_Documento_CSW','Valor_CSW','Cód. Par', 'Parâmetro', 'CNPJ/CPF_CSW']

dataframes = [
    comparacao_sat_erp,
    comparacao_cte_erp,
    comparacao_notas_servico_erp
    ]

dataframes_limpos =[
    limpar_colunas_se_coluna_referencia_nulo(df, "Alerta", *colunas_para_limpar)
    for df in dataframes
]

comparacao_sat_erp,comparacao_cte_erp, comparacao_notas_servico_erp = dataframes_limpos


comparacao_sat_erp = comparacao_sat_erp.drop(columns=["_merge"])
comparacao_cte_erp = comparacao_cte_erp.drop(columns=["_merge"])
comparacao_notas_servico_erp = comparacao_notas_servico_erp.drop(columns=["_merge"])

#Salva os Relatórios em Excel
with pd.ExcelWriter("comparacao_notas.xlsx", engine="xlsxwriter") as writer:
    comparacao_sat_erp.to_excel(writer,
                        columns=COLUNAS_SALVAS["sat"],
                        sheet_name="Comparação SAT vs CSW",
                        index=False
                        )
    comparacao_cte_erp.to_excel(writer,
                        columns=COLUNAS_SALVAS["cte"],
                        sheet_name="Comparação CTE vs CSW",
                        index=False
                        )
    comparacao_notas_servico_erp.to_excel(writer,
                        columns=COLUNAS_SALVAS["servico"],
                        sheet_name="Comparacao Serviços vs CSW",
                        index=False
                        )   
    df_notas_somente_erp.to_excel(
        writer,
        sheet_name="Notas Somente no ERP",
        index=False
    )

    formatar_planilha_excel(writer, COLUNAS_SALVAS["sat"], "Comparação SAT vs CSW")
    formatar_planilha_excel(writer, COLUNAS_SALVAS["cte"], "Comparação CTE vs CSW")
    formatar_planilha_excel(writer, COLUNAS_SALVAS["servico"], "Comparacao Serviços vs CSW")
    formatar_planilha_excel(writer, df_notas_somente_erp.columns.tolist(), "Notas Somente no ERP")

print("Execução Finalizada, fechando a aplicação...")

time.sleep(1)

print("Fechando em:")

for i in range(5, 0, -1):
    unidade = "segundo" if i == 1 else "segundos"
    print(f" {i} {unidade}")
    time.sleep(1)

