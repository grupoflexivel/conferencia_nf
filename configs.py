#Configurações Globais
valores_vazios = [""," ", "NaN", "nan", "Null", "NULL"]

#Configuração de Colunas
COLUNAS_IMPORTADAS = {
    "sat": ["NumeroDocumento","Situacao","ValorTotalNota","NomeEmitente","ChaveAcesso", "DataEmissao"],
    "erp": ["Documento","Valor","Chave Nf-e","Cód. Par", "Parâmetro","©CNPJ/CPF/CEI", "Data Emissão"],
    "cte": ["NÚMERO_CTE","SITUACAO","VALOR_TOTAL_PREST","NOME_EMITENTE","CHAVE_DE_ACESSO", "DATA_EMISSÃO"],
    "servico": ["Número","Data de Cancelamento","CPF/CNPJ - Prestador","Valor Serviços","Prestador - Nome/Razão Social", "Data de Emissão"],
    "qive-filial": ["Número","Status","Valor Total da Nota","Nome PJ Emitente","Chave de Acesso", "Data Emissão"],
    "cte-filial" :["Número","Status","Valor","Emitente","Chave de Acesso", "Emissão"]

}

COLUNAS_SALVAS = {
    "sat": ["Observações","status","Numero_Documento","ChaveAcesso","Nome_Emitente","Data_Emissao","Valor","Situacao","Alerta Comparador", "Numero_Documento_CSW","Valor_CSW","Cód. Par","Parâmetro"],

    "cte": ["Observações","status","Numero_Documento","ChaveAcesso","Nome_Emitente","Data_Emissao","Valor","Situacao","Alerta Comparador","Numero_Documento_CSW","Valor_CSW",
            "Cód. Par","Parâmetro"],

    "servico": ["Observações","status","Numero_Documento","Numero_Documento_Original","Nome_Emitente","CNPJ/CPF","Data_Emissao","Valor","Situacao","Alerta Comparador","ChaveAcesso","Numero_Documento_CSW","Valor_CSW","CNPJ/CPF_CSW",
            "Cód. Par","Parâmetro"],
    
    "qive-filial": ["Observações","status","Numero_Documento","Nome_Emitente","CNPJ/CPF","Data_Emissao","Valor","Situacao","Alerta Comparador","ChaveAcesso","Numero_Documento_CSW","Valor_CSW","Cód. Par","Parâmetro"],
    
    "cte-filial" :["Observações","status","Numero_Documento","Nome_Emitente","Data_Emissao","Valor","Situacao","Alerta Comparador","ChaveAcesso","Numero_Documento_CSW","Valor_CSW","Cód. Par","Parâmetro"],
}

COLUNAS_REPROCESSAMENTO = {
    "sat": ["Situacao","ChaveAcesso","Nome_Emitente","Numero_Documento","Valor","Data_Emissao","status","Alerta Comparador","Observações" ],

    "cte": ["Numero_Documento","Situacao","Valor","Nome_Emitente","ChaveAcesso","Data_Emissao","status","Alerta Comparador","Observações"],

    "servico": ["Numero_Documento","Situacao","CNPJ/CPF","Nome_Emitente","Valor","ChaveAcesso","Data_Emissao","status","Alerta Comparador","Observações"],

    "qive-filial": ["Situacao","ChaveAcesso","Nome_Emitente","Numero_Documento","Valor","Data_Emissao","status","Alerta Comparador","Observações"],

    "cte-filial" :["Situacao","ChaveAcesso","Nome_Emitente","Numero_Documento","Valor","Data_Emissao","status","Alerta Comparador","Observações"]

}

NOMES_ABAS_NO_EXCEL = {
    "sat": "Comparação SAT vs CSW",
    "cte": "Comparação CTE vs CSW",
    "servico": "Comparacao Serviços vs CSW",
    "qive-filial":"Comparação QIVE vs CSW",
    "cte-filial":"Comparação CTE-QIVE vs CSW"
}

# Colunas que identificam univocamente uma nota, por tipo de documento.
# Usadas na deduplicação e na supressão de notas recusadas.
CHAVES_DEDUPLICACAO = {
    "sat": ["ChaveAcesso"],
    "cte": ["ChaveAcesso"],
    "servico": ["Numero_Documento", "CNPJ/CPF"],
    "qive-filial": ["ChaveAcesso"],
    "cte-filial": ["ChaveAcesso"],
}

# Nome da aba que guarda o registro persistente de notas recusadas
NOME_ABA_RECUSADAS = "Notas Recusadas"