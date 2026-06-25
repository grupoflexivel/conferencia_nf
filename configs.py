#Configurações Globais
valores_vazios = ['',' ', 'NaN', 'nan', 'Null', 'NULL']

#Configuração de Colunas
COLUNAS_IMPORTADAS = {
    "sat": ['NumeroDocumento','Situacao','ValorTotalNota','NomeEmitente','ChaveAcesso', 'DataEmissao'],
    "erp": ['Documento','Valor','Chave Nf-e','Cód. Par', 'Parâmetro','©CNPJ/CPF/CEI', 'Data Emissão'],
    "cte": ['NÚMERO_CTE','SITUACAO','VALOR_TOTAL_PREST','NOME_EMITENTE','CHAVE_DE_ACESSO', 'DATA_EMISSÃO'],
    "servico": ['Número','Data de Cancelamento','CPF/CNPJ - Prestador','Valor Serviços','Prestador - Nome/Razão Social', 'Data de Emissão']
}

COLUNAS_SALVAS = {
    "sat": ['Situacao','ChaveAcesso','NomeEmitente','Numero_Documento','Valor','Numero_Documento_CSW','Valor_CSW',
                    'Cód. Par','Parâmetro', 'DataEmissao','status','Alerta Comparador', 'Observações' ],
    "cte": ["Numero_Documento","SITUACAO","Valor","NOME_EMITENTE","ChaveAcesso","Numero_Documento_CSW","Valor_CSW",
            "Cód. Par","Parâmetro","DATA_EMISSÃO","status","Alerta Comparador", "Observações"],
    "servico": ["Numero_Documento","Situação","Numero_Documento_Original","CNPJ/CPF","Nome Prestador","Valor","Numero_Documento_CSW","Valor_CSW",
            "Cód. Par","Parâmetro","ChaveAcesso","CNPJ/CPF_CSW","Data de Emissão","status","Alerta Comparador","Observações"]
}

COLUNAS_REPROCESSAMENTO = {
    "sat": ['Situacao','ChaveAcesso','NomeEmitente','Numero_Documento','Valor','DataEmissao','status','Alerta Comparador',"Observações" ],

    "cte": ["Numero_Documento","SITUACAO","Valor","NOME_EMITENTE","ChaveAcesso","DATA_EMISSÃO","status","Alerta Comparador","Observações"],

    "servico": ["Numero_Documento","Situação","CNPJ/CPF","Nome Prestador","Valor","ChaveAcesso","Data de Emissão","status","Alerta Comparador","Observações"]

}

NOMES_ABAS_NO_EXCEL = {
    "sat": "Comparação SAT vs CSW",
    "cte": "Comparação CTE vs CSW",
    "servico": "Comparacao Serviços vs CSW"
}