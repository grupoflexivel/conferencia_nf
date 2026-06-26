#Configurações Globais
valores_vazios = [""," ", "NaN", "nan", "Null", "NULL"]

#Configuração de Colunas
COLUNAS_IMPORTADAS = {
    "sat": ["NumeroDocumento","Situacao","ValorTotalNota","NomeEmitente","ChaveAcesso", "DataEmissao"],
    "erp": ["Documento","Valor","Chave Nf-e","Cód. Par", "Parâmetro","©CNPJ/CPF/CEI", "Data Emissão"],
    "cte": ["NÚMERO_CTE","SITUACAO","VALOR_TOTAL_PREST","NOME_EMITENTE","CHAVE_DE_ACESSO", "DATA_EMISSÃO"],
    "servico": ["Número","Data de Cancelamento","CPF/CNPJ - Prestador","Valor Serviços","Prestador - Nome/Razão Social", "Data de Emissão"]
}

COLUNAS_SALVAS = {
    "sat": ["Observações","status","Numero_Documento","ChaveAcesso","NomeEmitente","DataEmissao","Valor","Situacao","Alerta Comparador", "Numero_Documento_CSW","Valor_CSW","Cód. Par","Parâmetro"],

    "cte": ["Observações","status","Numero_Documento","ChaveAcesso","NOME_EMITENTE","DATA_EMISSÃO","Valor","SITUACAO","Alerta Comparador","Numero_Documento_CSW","Valor_CSW",
            "Cód. Par","Parâmetro"],

    "servico": ["Observações","status","Numero_Documento","Numero_Documento_Original","Nome Prestador","CNPJ/CPF","Data de Emissão","Valor","Situação","Alerta Comparador","ChaveAcesso","Numero_Documento_CSW","Valor_CSW","CNPJ/CPF_CSW",
            "Cód. Par","Parâmetro"]
}

COLUNAS_REPROCESSAMENTO = {
    "sat": ["Situacao","ChaveAcesso","NomeEmitente","Numero_Documento","Valor","DataEmissao","status","Alerta Comparador","Observações" ],

    "cte": ["Numero_Documento","SITUACAO","Valor","NOME_EMITENTE","ChaveAcesso","DATA_EMISSÃO","status","Alerta Comparador","Observações"],

    "servico": ["Numero_Documento","Situação","CNPJ/CPF","Nome Prestador","Valor","ChaveAcesso","Data de Emissão","status","Alerta Comparador","Observações"]

}

CHAVES_DEDUPLICACAO = {
    "sat": ["ChaveAcesso"],
    "cte": ["ChaveAcesso"],
    "servico": ["Numero_Documento", "CNPJ/CPF"]
}

NOMES_ABAS_NO_EXCEL = {
    "sat": "Comparação SAT vs CSW",
    "cte": "Comparação CTE vs CSW",
    "servico": "Comparacao Serviços vs CSW"
}