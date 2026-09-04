# Contexto do Projeto — Comparador de Notas Fiscais

> Documento vivo. O código-fonte é a fonte primária da verdade; este arquivo consolida o entendimento técnico disponível em cada análise e deve ser atualizado junto com alterações relevantes.

## 1. Objetivo do Projeto

Aplicação desktop em Python para conferir documentos fiscais externos contra lançamentos do ERP Consistem/CSW. O sistema lê relatórios de entrada/devolução do ERP e relatórios de documentos fiscais, cruza os registros por chaves de identificação, aponta documentos não lançados, alerta divergências de valores e exporta um relatório Excel para acompanhamento.

O código implementa dois layouts de unidade:

- Matriz: SAT, CT-e em relatório HTML e Notas de Serviço.
- Filial: relatórios Qive de entrada, CT-e do Qive e Notas de Serviço.

Também existe um fluxo de continuidade mensal: pendências do arquivo anterior podem ser reincorporadas, e notas marcadas como recusadas podem ser suprimidas das análises seguintes.

## 2. Estado Atual

**Estado identificado:** aplicação com execução desktop preservada e interface HTTP containerizada; validação técnica Docker concluída e homologação fiscal pendente.

Fatos observados:

- O ponto de entrada é `main.py`.
- A execução principal é gráfica, usando Tkinter.
- O fluxo central está implementado para Matriz e Filial.
- O projeto contém testes automatizados mínimos para a camada HTTP em `tests/test_webapp.py`, mas não possui arquivos reais de entrada/saída para uma validação ponta a ponta.
- A sintaxe dos 17 arquivos Python atualmente presentes, incluindo testes, foi validada por AST; os módulos principais puderam ser importados sem executar a interface.
- O auxiliar experimental `selector.py` foi removido nesta tarefa por não ser necessário ao fluxo principal.
- A execução HTTP foi adicionada com Flask/Gunicorn; o serviço Docker foi validado como saudável na porta publicada `5011`.
- A tela HTTP agora usa logo, seleção inicial de unidade e liberação progressiva dos anexos por JavaScript.
- O README afirma status “em produção”, mas essa afirmação não foi verificada funcionalmente nesta análise.

Pendências de investigação:

- Validar o processamento com arquivos reais representativos de cada layout.
- Confirmar os contratos de colunas, nomes de abas e formatos exportados pelos sistemas Consistem/CSW, SAT e Qive.
- Confirmar com usuários as regras de normalização de números de serviços, tolerâncias monetárias e tratamento de cancelamentos.

## 3. Stack Tecnológica

- Linguagem: Python. O README declara Python 3.14 ou superior.
- Processamento tabular: `pandas==3.0.3` e `numpy==2.4.6`.
- Leitura de Excel: `openpyxl==3.1.5`, com `xlrd==2.0.2` disponível para formatos suportados.
- Escrita/formatação de Excel: `xlsxwriter==3.2.9`.
- Parsing de relatório HTML de CT-e: `html5lib==1.1`, `beautifulsoup4==4.15.0`, `lxml==6.1.1` e `webencodings==0.5.1`.
- Interface gráfica: Tkinter, biblioteca da instalação Python; não aparece como dependência do `requirements.txt`.
- Interface HTTP: Flask `3.1.3` e Gunicorn `26.2.0`, declarados em `requirements-docker.txt`.
- Empacotamento: `pyinstaller==6.21.0`, `altgraph`, `pefile`, `pyinstaller-hooks-contrib` e dependências auxiliares.
- Utilitários declarados: `python-dateutil`, `tzdata`, `packaging`, `setuptools`, `six`, `soupsieve`, `typing_extensions`, `et_xmlfile` e `pywin32-ctypes`.

O arquivo `requirements.txt` contém as dependências desktop/build existentes, está codificado em UTF-16 little-endian com terminadores CRLF e inclui ferramentas de empacotamento. `requirements-docker.txt` contém o subconjunto de runtime necessário ao serviço HTTP, acrescido de Flask/Gunicorn. Não há `pyproject.toml`, `setup.py`, `Pipfile` ou arquivo `.env.example`.

## 4. Estrutura do Projeto

```text
conferencia_nf/
├── main.py
├── motor.py
├── configs.py
├── comparacao.py
├── limpeza.py
├── relatorios_csw.py
├── arquivos.py
├── recusadas.py
├── excel_utils.py
├── seletor_unidade.py
├── processamento.py
├── webapp.py
├── Dockerfile
├── compose.yaml
├── requirements-docker.txt
├── .dockerignore
├── tests/
│   ├── test_webapp.py
│   └── test_frontend_flow.js
├── requirements.txt
├── README.md
├── logo.ico
├── logo_topo.png
├── favicon.ico
└── layouts/
    ├── __init__.py
    ├── base.py
    ├── matriz.py
    └── filial_mg.py
```

Também foram observados `venv/`, `__pycache__/` e `layouts/__pycache__/`; são artefatos locais/gerados e não fazem parte do fluxo funcional documentado. O Git já possuía alterações nesses bytecodes antes desta tarefa; elas foram preservadas.

Responsabilidade dos componentes:

| Componente | Responsabilidade observada |
|---|---|
| `main.py` | Entrada, seleção de unidade/arquivos, orquestração do pipeline, tratamento global de erro e exportação. |
| `configs.py` | Nomes de colunas de entrada/saída, nomes de abas, chaves de deduplicação e valores vazios. |
| `layouts/base.py` | Contrato comum dos layouts, carregamento do ERP, limpeza comum e comparação encadeada. |
| `layouts/matriz.py` | Leitura e mapeamento dos relatórios SAT, CT-e HTML e Serviço da Matriz. |
| `layouts/filial_mg.py` | Leitura e mapeamento dos relatórios Qive, CT-e Qive e Serviço da Filial. |
| `relatorios_csw.py` | Leitura, padronização e concatenação dos relatórios do ERP. |
| `motor.py` | Merge ERP × documento, cálculo de status, alertas, cancelamentos e preparação para exportação. |
| `comparacao.py` | Funções de regra para status, divergência monetária, cancelamentos e deduplicação no reprocessamento. |
| `limpeza.py` | Normalização de documentos, chaves, valores, datas e ordenação. |
| `arquivos.py` | Leitura de pendências do mês anterior, concatenação e deduplicação. |
| `recusadas.py` | Coleta, persistência temporária, supressão e montagem da aba de notas recusadas. |
| `excel_utils.py` | Congelamento, larguras, filtros, proteção e formatos das abas exportadas. |
| `seletor_unidade.py` | Janelas Tkinter para seleção de unidade e arquivos; resolução de recursos para Python/PyInstaller. |
| `processamento.py` | Pipeline compartilhado de validação, carregamento, reprocessamento, comparação e exportação. |
| `webapp.py` | Interface HTTP Flask, formulário progressivo, entrega da logo, upload temporário, healthcheck e download do relatório. |
| `Dockerfile` | Imagem Linux do serviço HTTP, dependências, usuário não-root e comando Gunicorn. |
| `compose.yaml` | Publicação da porta 5011, volume de saída, restart policy e healthcheck. |
| `requirements-docker.txt` | Dependências Python de runtime para o container. |
| `.dockerignore` | Arquivos excluídos do contexto de build. |
| `tests/test_webapp.py` | Testes mínimos da interface HTTP e do contrato de upload, sem validação semântica de Excel. |
| `tests/test_frontend_flow.js` | Teste Node do JavaScript real embutido em `webapp.py`, usando DOM mínimo simulado. |

## 5. Arquitetura e Fluxo Geral

A arquitetura atual é procedural/orquestrada por um pipeline compartilhado em `processamento.py`. `main.py` mantém a entrada desktop/Tkinter, enquanto `webapp.py` fornece a entrada HTTP para execução em servidor. A classe de motor e as subclasses de layout continuam responsáveis pelas regras e formatos existentes.

```text
main.py
├── seletor_unidade.py
└── processamento.py
    ├── layouts.matriz / layouts.filial_mg
    │   ├── layouts.base
    │   ├── relatorios_csw.py
    │   └── limpeza.py
    ├── arquivos.py
    │   └── comparacao.py
    ├── recusadas.py
    ├── motor.py
    │   ├── comparacao.py
    │   └── limpeza.py
    └── excel_utils.py

webapp.py
├── processamento.py
└── Flask/Gunicorn
```

Fluxo de execução:

1. Na execução desktop, `selecionar_unidade()` abre a janela e retorna `Matriz`, `Filial` ou `None`.
2. Na execução HTTP, a tela inicial exibe `logo_topo.png` e permite escolher `Matriz` ou `Filial` antes de mostrar os anexos.
3. Após a escolha, JavaScript exibe e habilita somente o conjunto de campos da unidade selecionada; os campos da outra unidade permanecem ocultos e desabilitados.
4. Na execução HTTP, `webapp.py` recebe a unidade e os uploads multipart em `POST /process`.
5. `main.py` ou `webapp.py` instancia o layout e chama `processar_conferencia()`.
6. Pelo menos um relatório ERP — entrada ou devolução — é exigido.
7. O layout carrega e normaliza os documentos externos selecionados.
8. Se houver arquivo anterior, cada tipo da ordem do layout é analisado para reincorporar pendências.
9. Notas recusadas são coletadas do arquivo anterior, registradas e removidas antes dos merges.
10. Os tipos presentes são comparados sequencialmente contra o restante do ERP.
11. O restante do ERP é exportado como `Notas Somente no ERP`.
12. O relatório é escrito no diretório de execução com `xlsxwriter` e formatado/protegido.
13. Na execução HTTP, o relatório é disponibilizado como download e também permanece no volume de saída.

O processamento é síncrono. A interface HTTP não usa banco de dados, serviço externo ou IP fixo; usa apenas diretório temporário para uploads e volume para saída. A configuração `OUTPUT_DIR` pode apontar para o diretório de relatórios do container.

## 6. Fluxo de Dados

### 6.1 Entrada e seleção

- **Arquivo:** `seletor_unidade.py`.
- **Funções:** `selecionar_unidade()` e `selecionar_arquivos()`.
- **Recebe:** interação do usuário.
- **Retorna:** nome da unidade e dicionário com caminhos, incluindo `None` para campos não selecionados.
- **Falhas possíveis:** indisponibilidade de display/Tkinter; seleção de arquivo com formato incompatível; fechamento da janela.

Todos os campos exibidos na GUI são opcionais no nível do seletor. A obrigatoriedade do ERP é verificada depois em `main.py`; o restante do fluxo exige pelo menos um documento externo novo ou uma pendência anterior.

### 6.1a Entrada HTTP

- **Arquivo:** `webapp.py`.
- **Rotas:** `GET /`, `POST /process`, `GET /health`, `GET /logo_topo.png` e `GET /favicon.ico`.
- **Recebe:** formulário `multipart/form-data` com `unidade` e arquivos nomeados por unidade, por exemplo `Matriz__arquivo_sat` ou `Filial__arquivo_qive_entrada`.
- **Interface:** começa mostrando a logo e as opções `Matriz`/`Filial`; após a seleção, mostra somente os campos correspondentes. Ao trocar a unidade, o JavaScript limpa todos os arquivos escolhidos antes de atualizar os campos.
- **Validação de interface:** o botão fica desabilitado até haver unidade, ao menos um arquivo ERP (`arquivo_notas_entrada` ou `arquivo_devolucoes`) e ao menos um documento/arquivo anterior.
- **Transforma:** grava os uploads em diretório temporário, aplica `secure_filename()` e passa os caminhos ao mesmo pipeline usado pela GUI.
- **Retorna:** formulário HTML com referência ao favicon, JSON de saúde, recursos visuais, mensagem HTTP de erro ou download do `.xlsx`.
- **Falhas possíveis:** unidade inválida, nome de arquivo inválido, ausência de ERP/documentos, erro de leitura, erro do pipeline ou impossibilidade de gravar no volume de saída.

### 6.2 Leitura do ERP

- **Arquivo:** `layouts/base.py` chama `relatorios_csw.py`.
- **Funções:** `LayoutBase.carregar_dados()`, `concatenar_relatorios_erp()`, `carregar_relatorio_csw()` e `padronizar_colunas_csw()`.
- **Recebe:** caminho de entrada e/ou devolução do Consistem.
- **Transforma:** lê as colunas configuradas em `COLUNAS_IMPORTADAS["erp"]`, ignora a última linha com `skipfooter=1`, força documento/CNPJ/chave para texto, concatena entrada e devolução, renomeia para o modelo interno e normaliza documento, chave, CNPJ/CPF e valor.
- **Retorna:** `df_erp` padronizado.
- **Falhas possíveis:** nenhum arquivo ERP; arquivo inexistente; aba/coluna divergente; relatório com rodapé diferente; valores incompatíveis.

### 6.3 Leitura dos documentos externos

- **Arquivos:** `layouts/matriz.py` e `layouts/filial_mg.py`.
- **Funções:** loaders específicos, `carregar_documentos()` e `LayoutBase._carregar_se_presente()`.
- **Recebe:** caminhos selecionados.
- **Transforma:** lê as colunas específicas de cada fornecedor, renomeia para o modelo interno (`Numero_Documento`, `ChaveAcesso`, `Valor`, `Nome_Emitente`, `Data_Emissao`, `Situacao` etc.), converte valores monetários quando aplicável e aplica a limpeza comum.
- **Retorna:** dicionário somente com os tipos cujo arquivo foi fornecido.
- **Falhas possíveis:** colunas faltantes, planilha/aba incorreta, parsing HTML sem tabela esperada, codificação/formato não reconhecido e valores não conversíveis.

### 6.4 Reprocessamento de pendências

- **Arquivo:** `arquivos.py`, chamado por `main.py`.
- **Funções:** `adicionar_pendentes_mes_anterior()` e `carregar_notas_pendentes_mes_anterior()`.
- **Recebe:** DataFrame atual, arquivo Excel anterior e tipo documental.
- **Transforma:** encontra a aba pelo mapeamento de `NOMES_ABAS_NO_EXCEL`, lê somente `COLUNAS_REPROCESSAMENTO`, força texto, filtra exatamente `status == "Não lançada no CSW"`, concatena com dados atuais, remove duplicidades e converte `Valor` para numérico.
- **Retorna:** DataFrame unificado; se a aba anterior não existir, retorna a base atual.
- **Falhas possíveis:** arquivo anterior ilegível, colunas salvas incompatíveis, tipo desconhecido, chave ausente ou valor monetário não conversível.

### 6.5 Tratamento de recusadas

- **Arquivo:** `recusadas.py`, chamado por `main.py` antes da comparação.
- **Funções:** `coletar_recusadas()`, `construir_aba_recusadas()` e `suprimir_recusadas()`.
- **Recebe:** arquivo anterior, tipos ativos e bases atuais.
- **Transforma:** coleta status com variações de “Recusada/Recusado”, combina essas chaves com as herdadas da aba `Notas Recusadas`, monta o ledger a partir das bases atuais e remove as chaves recusadas da análise.
- **Retorna:** conjuntos de chaves por tipo, DataFrame do ledger e bases filtradas.
- **Falhas possíveis:** estrutura do ledger incompleta, colunas-chave ausentes ou divergência entre a chave salva e a chave normalizada atual.

### 6.6 Comparação

- **Arquivo:** `motor.py`, com regras de `comparacao.py` e `limpeza.py`.
- **Funções:** `LayoutBase.comparar()`, `realizar_merge()`, `comparar_sat_ou_qive_csw()`, `comparar_cte_matriz_csw()` e `comparar_servicos_csw()`.
- **Recebe:** documento externo padronizado e o DataFrame ERP restante.
- **Transforma:** faz `merge` à esquerda com `indicator=True`, cria status, verifica valores, aplica regra especial de CT-e quando necessário, trata cancelamentos e calcula o restante do ERP para a próxima comparação.
- **Retorna:** comparação do tipo e ERP restante.
- **Falhas possíveis:** chave ausente, colisões/duplicidades que multipliquem linhas no merge, coluna de valor ausente, tipo incompatível ou situação inesperada.

### 6.7 Preparação e exportação

- **Arquivos:** `motor.py`, `main.py` e `excel_utils.py`.
- **Funções:** `formatar_e_limpar_colunas_para_exportar()`, `exportar_relatorio()` e `formatar_planilha_excel()`.
- **Recebe:** comparações, ERP restante e ledger de recusadas.
- **Transforma:** limpa colunas ERP auxiliares quando não há alerta, ordena por data de emissão, garante `Observações`, escreve as colunas configuradas e aplica formatação/proteção.
- **Retorna:** arquivo `.xlsx` no diretório de trabalho atual.
- **Falhas possíveis:** coluna configurada não existir no DataFrame, arquivo de saída bloqueado, permissão de escrita ou problema no engine `xlsxwriter`.

## 7. Arquivos de Entrada

Não existem arquivos de entrada Excel/HTML de exemplo no repositório. Os formatos abaixo são inferidos diretamente dos `usecols`, renomeações e chamadas de leitura.

### ERP Consistem/CSW

- **Seleção:** `arquivo_notas_entrada` e/ou `arquivo_devolucoes`.
- **Leitura:** `relatorios_csw.carregar_relatorio_csw()`.
- **Colunas esperadas:** `Documento`, `Valor`, `Chave Nf-e`, `Cód. Par`, `Parâmetro`, `©CNPJ/CPF/CEI`, `Data Emissão`; o código também renomeia `Fornecedor`, embora essa coluna não esteja listada explicitamente em `COLUNAS_IMPORTADAS["erp"]`.
- **Regras:** ao menos um dos dois arquivos deve ser informado; os dois são concatenados quando presentes.
- **Aba:** não fixada pelo código; usa a aba padrão do primeiro `read_excel`.

### SAT — Matriz

- **Seleção:** `arquivo_sat`.
- **Leitura:** `LayoutMatriz.carregar_relatorio_sat_matriz()`.
- **Colunas esperadas:** `NumeroDocumento`, `Situacao`, `ValorTotalNota`, `NomeEmitente`, `ChaveAcesso`, `DataEmissao`.
- **Modelo interno:** `Numero_Documento`, `Valor`, `Nome_Emitente`, `Data_Emissao`, mantendo `Situacao` e `ChaveAcesso`.
- **Aba:** não fixada.

### CT-e — Matriz

- **Seleção:** `arquivo_cte`.
- **Leitura:** `LayoutMatriz.carregar_relatorio_cte_matriz()` com `open(..., "rb")` e `pandas.read_html(..., flavor="html5lib")`.
- **Colunas esperadas:** `NÚMERO_CTE`, `SITUACAO`, `VALOR_TOTAL_PREST`, `NOME_EMITENTE`, `CHAVE_DE_ACESSO`, `DATA_EMISSÃO`.
- **Modelo interno:** `Numero_Documento`, `Situacao`, `Valor`, `Nome_Emitente`, `ChaveAcesso`, `Data_Emissao`.
- **Aba/formato:** o código usa a primeira tabela HTML encontrada; o seletor permite qualquer arquivo apesar do rótulo visual mencionar Excel.

### Notas de Serviço — Matriz ou Filial

- **Seleção:** `arquivo_servico`.
- **Leitura:** `carregar_relatorio_servico_matriz()` ou `carregar_relatorio_servico_filial()`.
- **Colunas esperadas:** `Número`, `Data de Cancelamento`, `CPF/CNPJ - Prestador`, `Valor Serviços`, `Prestador - Nome/Razão Social`, `Data de Emissão`.
- **Modelo interno:** `Numero_Documento`, `Numero_Documento_Original`, `CNPJ/CPF`, `Valor`, `Nome_Emitente`, `Data_Emissao` e `Data de Cancelamento`.
- **Tratamento:** o número original é preservado; `Numero_Documento` é normalizado por `limpar_numero_documento_servicos()`.

### Qive — Filial

- **Seleção:** `arquivo_qive_entrada`.
- **Leitura:** `LayoutFilialMG.carregar_relatorio_qive_filial()`.
- **Aba:** exige `sheet_name="relatorio"`.
- **Colunas esperadas:** `Número`, `Status`, `Valor Total da Nota`, `Nome PJ Emitente`, `Chave de Acesso`, `Data Emissão`.
- **Modelo interno:** `Numero_Documento`, `Situacao`, `Valor`, `Nome_Emitente`, `ChaveAcesso`, `Data_Emissao`.

### CT-e — Filial

- **Seleção:** `arquivo_cte`.
- **Leitura:** `LayoutFilialMG.carregar_relatorio_cte_filial()` com `read_excel` e aba padrão.
- **Colunas esperadas:** `Número`, `Status`, `Valor`, `Emitente`, `Chave de Acesso`, `Emissão`.
- **Modelo interno:** `Numero_Documento`, `Situacao`, `Valor`, `Nome_Emitente`, `ChaveAcesso`, `Data_Emissao`.

### Arquivo anterior

- **Seleção:** `arquivo_anterior`, opcional.
- **Finalidade:** reprocessar pendências e identificar recusadas.
- **Abas utilizadas:** nomes de comparação definidos em `NOMES_ABAS_NO_EXCEL` e `Notas Recusadas`.
- **Critério de pendência:** status textual exatamente igual a `Não lançada no CSW`.

### Uploads HTTP

- Os arquivos enviados pela interface web são temporários e removidos ao final da requisição.
- O upload não altera os arquivos do host nem exige paths absolutos do Windows.
- O nome final do relatório segue o layout e é gravado em `OUTPUT_DIR`, por padrão `/app/output` dentro do container.

## 8. Arquivos de Saída

O arquivo é criado no diretório de execução com nome fixo:

- Matriz: `comparacao_notas.xlsx`.
- Filial: `comparacao_notas_filial.xlsx`.

Abas de comparação possíveis:

| Tipo | Nome da aba |
|---|---|
| SAT | `Comparação SAT vs CSW` |
| CT-e Matriz | `Comparação CTE vs CSW` |
| Serviço | `Comparacao Serviços vs CSW` |
| Qive Filial | `Comparação QIVE vs CSW` |
| CT-e Filial | `Comparação CTE-QIVE vs CSW` |

Além das abas de tipos efetivamente presentes, o arquivo sempre tenta gerar:

- `Notas Somente no ERP`: registros restantes do DataFrame ERP após o consumo sequencial pelas comparações.
- `Notas Recusadas`: ledger das notas recusadas que ainda existem na base atual.

As colunas das abas de comparação são restringidas por `COLUNAS_SALVAS`. A exportação usa `xlsxwriter`, congela a primeira linha, configura filtros, largura padrão 28 e protege a aba deixando as células de dados editáveis e o cabeçalho bloqueado. Não há senha de proteção configurada.

Na interface HTTP, o arquivo gerado é retornado como download na mesma requisição. Uma cópia também fica no volume `conferencia_nf_output`, montado em `/app/output`.

## 9. Regras de Negócio Confirmadas

Somente regras observáveis diretamente no código:

1. A unidade selecionável é `Matriz` ou `Filial`.
2. O ERP exige pelo menos um arquivo entre notas de entrada e devoluções; os dois podem ser usados simultaneamente.
3. Os documentos externos são opcionais individualmente, mas deve existir ao menos um tipo novo ou uma pendência anterior para haver comparação.
4. A ordem de comparação é `sat → cte → servico` na Matriz e `qive-filial → cte-filial → servico` na Filial.
5. Após cada tipo, o ERP usado naquele tipo é removido do DataFrame restante; o restante é passado ao próximo tipo.
6. SAT, CT-e, Qive e CT-e Filial usam `ChaveAcesso` como chave de merge e deduplicação.
7. Serviços usam `Numero_Documento` + `CNPJ/CPF`; no merge a chave é construída como `Numero_Documento-CNPJ/CPF`, enquanto deduplicação/recusadas usam a combinação com separador `|` internamente.
8. Um registro com correspondência no merge recebe `Lançada no CSW`; um registro somente no documento externo recebe `Não lançada no CSW`.
9. Divergência monetária é marcada somente para linhas `both` quando `np.isclose(Valor, Valor_CSW, atol=0.01)` for falso.
10. Para CT-e da Matriz, antes da comparação de valores, o valor externo é dividido por 100 se equivaler ao valor ERP multiplicado por 100, ou por 10 se equivaler ao valor ERP multiplicado por 10, ambos com tolerância absoluta de 0,1. Caso contrário, permanece inalterado.
11. Situações contendo variações de `cancelado`, `cancelada`, `cancelados` ou `canceladas` são reconhecidas sem diferenciação de maiúsculas/minúsculas.
12. Se uma nota estiver cancelada e lançada no CSW, recebe o alerta `Documento Lançado no ERP com status Cancelado`; se estiver cancelada e não lançada, o status recebe a situação do documento.
13. Para Serviços, a presença de qualquer valor não nulo em `Data de Cancelamento` define `Situacao` como `Cancelado`; bases reprocessadas sem essa coluna preservam a situação já existente.
14. A limpeza comum remove pontuação de CNPJ/CPF, remove apóstrofo/ponto de chave de acesso e remove zeros à esquerda do número genérico do documento.
15. Números de serviços mantêm `Numero_Documento_Original`, filtram caracteres não numéricos, removem zeros à esquerda e removem os quatro primeiros caracteres quando o valor começa com prefixos derivados do ano atual/anterior e tem mais de nove dígitos.
16. O reprocessamento importa somente linhas com status exatamente `Não lançada no CSW`, deduplica pelas chaves do tipo e converte `Valor` para numérico.
17. A coleta de recusadas combina linhas recusadas das abas de comparação com linhas do ledger `Notas Recusadas`; a supressão ocorre antes dos merges.
18. O ledger de recusadas é reconstruído usando apenas recusadas que ainda aparecem na base atual, portanto o código pretende que o registro se limpe quando a nota deixa de existir na base.
19. A ordenação final converte datas nos formatos `%d/%m/%Y`, `%d/%m/%Y %H:%M:%S`, `%Y-%m-%d` e `%Y-%m-%d %H:%M:%S`; datas não interpretadas ficam por último.
20. A interface HTTP inicia com os uploads ocultos e desabilitados; somente a escolha de `Matriz` ou `Filial` libera o conjunto de campos correspondente.
21. A interface mantém os nomes de campos prefixados esperados pelo backend, como `Matriz__arquivo_sat` e `Filial__arquivo_qive_entrada`.
22. A interface bloqueia o botão de processamento até haver unidade, pelo menos um arquivo ERP e pelo menos um documento ou arquivo anterior selecionado; a validação do backend continua sendo executada.
23. Ao trocar a unidade na interface HTTP, os valores de todos os inputs de arquivo são limpos antes da nova unidade ser habilitada.
24. `logo_topo.png`, armazenada na raiz do repositório, é entregue por uma rota dedicada e referenciada no template com `url_for()`.

## 10. Hipóteses / Pontos que Precisam de Validação

- **Hipótese — requer validação:** os relatórios ERP sempre têm a última linha a ser descartada por `skipfooter=1`.
- **Hipótese — requer validação:** a coluna `Fornecedor` está presente no relatório ERP, embora não esteja em `COLUNAS_IMPORTADAS["erp"]`; caso contrário, o rename não terá efeito.
- **Hipótese — requer validação:** chaves de acesso são sempre suficientes e únicas para SAT/CT-e/Qive.
- **Hipótese — requer validação:** o prefixo temporal removido dos números de serviço deve sempre ser de quatro caracteres, inclusive nos prefixos de dois dígitos.
- **Hipótese — requer validação:** qualquer data preenchida em `Data de Cancelamento`, inclusive datas inválidas que o pandas mantenha como valor, deve significar cancelamento.
- **Hipótese — requer validação:** divergência de valores com `NaN` deve ser tratada como divergência; o código atual tende a marcar como divergente quando a linha está `both`.
- **Não determinado pela análise atual:** se diferenças de CNPJ/CPF, nome, data, situação ou parâmetros do ERP devem gerar alertas próprios; o código compara explicitamente chaves e valores, mas não cria validação para todos esses campos.
- **Não determinado pela análise atual:** se documentos duplicados nos arquivos atuais devem ser mantidos, agregados ou rejeitados. A deduplicação explícita está concentrada no reprocessamento e no ledger.
- **Não determinado pela análise atual:** se a saída deve ser sobrescrita sem confirmação. O código usa nomes fixos e abre o ExcelWriter diretamente.

## 11. Funções e Componentes Principais

### Orquestração

- `main.py:main()`: controla seleção, validação mínima, carregamento, reprocessamento, recusadas, comparação, formatação e exportação.
- `main.py:exportar_relatorio()`: cria o workbook e escreve abas/colunas.
- `main.py:tratar_erro_global()`: imprime traceback, tenta mostrar mensagem Tkinter e aguarda Enter.

### Layouts

- `LayoutBase.carregar_dados()`: combina carregamento ERP e documentos.
- `LayoutBase.comparar()`: percorre `ORDEM_COMPARACAO` e encadeia o ERP restante.
- `LayoutBase.aplicar_limpeza_dados()`: aplica limpadores comuns se as colunas existirem.
- `LayoutMatriz` e `LayoutFilialMG`: definem seleção de arquivos, loaders e estratégia por tipo.

### ERP e arquivos anteriores

- `relatorios_csw.carregar_relatorio_csw()`: lê uma fonte ERP.
- `relatorios_csw.padronizar_colunas_csw()`: renomeia e normaliza o DataFrame ERP.
- `relatorios_csw.concatenar_relatorios_erp()`: exige entrada ou devolução e concatena as fontes.
- `arquivos.carregar_notas_pendentes_mes_anterior()`: lê e filtra pendências de uma aba.
- `arquivos.adicionar_pendentes_mes_anterior()`: concatena atual/anterior e deduplica.

### Motor e regras

- `ConferenciaNotaFiscal.realizar_merge()`: merge left com sufixo `_CSW` e indicador `_merge`.
- `ConferenciaNotaFiscal.realizar_analises_colunas()`: encadeia status, valores e cancelamentos.
- `ConferenciaNotaFiscal.remover_notas_ja_lancadas()`: calcula ERP não consumido por presença da chave.
- `ConferenciaNotaFiscal.formatar_e_limpar_colunas_para_exportar()`: limpa colunas auxiliares e ordena.
- `comparacao.mapear_coluna_status()`: mapeia `_merge` para status textual.
- `comparacao.analisar_diferenca_entre_valores_lançados()`: cria `Alerta Comparador` para diferença monetária.
- `comparacao.verificar_situacao_notas_canceladas()`: aplica regras de situação/status para cancelados.
- `comparacao.verificar_cancelamentos()`: deriva situação de serviço pela data de cancelamento.
- `comparacao.remover_documentos_duplicados_reprocessamento()`: preserva observações e usa `drop_duplicates(keep="last")`.

### Recusadas e Excel

- `recusadas.coletar_recusadas()`: retorna conjuntos de chaves por tipo.
- `recusadas.suprimir_recusadas()`: remove linhas por chave.
- `recusadas.construir_aba_recusadas()`: materializa o ledger atual.
- `excel_utils.formatar_planilha_excel()`: configura edição, filtro, congelamento e proteção.

## 12. Tratamento de Dados

### Normalização de identificadores

- `limpar_cnpj_cpf()` remove `.`, `/` e `-`; nulos viram string vazia.
- `limpar_numero_documento()` converte para texto, aplica `strip()`, remove toda ocorrência do texto `.0` e remove zeros à esquerda.
- `limpar_chave_acesso()` remove apóstrofo, pontos e espaços; nulos viram `np.nan`.
- `limpar_numero_documento_servicos()` retém somente dígitos, aplica a regra de prefixos de ano e remove zeros à esquerda.

### Valores

- SAT Matriz não chama explicitamente o conversor monetário na carga.
- Qive e Serviços convertem valores usando `converter_valor_monetario_brasileiro()` e depois `pd.to_numeric(errors="coerce")`.
- CT-e Filial faz o mesmo para a coluna `Valor`.
- O conversor tenta primeiro conversão numérica direta; para falhas, remove `R$`, espaços e pontos e troca vírgula por ponto.
- Valores não convertíveis tornam-se `NaN`.

### Merges e filtros

- O merge é `left`, preservando todas as linhas do documento externo.
- `_merge == "both"` indica correspondência e `_merge == "left_only"` indica ausência no ERP.
- Não há `validate=` no merge para impor cardinalidade.
- O restante do ERP é filtrado por `isin()` da chave do documento atual.
- Serviços criam `ChaveComparadora` em ambos os DataFrames como `Numero_Documento-CNPJ/CPF`.

### Duplicidades

- No reprocessamento, deduplicação usa as chaves de `CHAVES_DEDUPLICACAO` e mantém a última linha.
- Quando existe `Observações`, valores preenchidos são propagados no grupo via `ffill()`/`bfill()` antes do `drop_duplicates()`.
- Não há validação explícita de duplicidades nos arquivos recém-carregados nem no ERP.

### Datas

- A data não é convertida para comparação de negócio.
- Ela é convertida somente para ordenação final através de `converter_data_mista()`.
- Valores sem formato reconhecido são ordenados depois dos valores válidos.

## 13. Tratamento de Erros e Exceções

- `main.py` possui `try/except` global no bloco de execução e chama `tratar_erro_global()`.
- O tratamento global imprime traceback completo, mostra uma mensagem genérica ao usuário e tenta `input()` para aguardar encerramento.
- Falhas de ícone/logo são ignoradas em `seletor_unidade.py` para permitir execução sem os recursos visuais.
- `_ler_aba()` em `recusadas.py` converte ausência de aba em DataFrame vazio.
- A ausência de aba anterior de um tipo é tratada em `adicionar_pendentes_mes_anterior()`.
- Funções de análise levantam `ValueError` quando colunas obrigatórias ou valores válidos de `_merge` estão ausentes.

Fragilidades observadas:

- Não há logging estruturado, níveis de severidade, arquivo de log ou identificação do arquivo/etapa que falhou.
- A maior parte das leituras depende de exceções nativas do pandas/openpyxl sem mensagens específicas de contrato de entrada.
- O tratamento global não substitui validação de schema antes do processamento.
- `input()` pode ser inadequado em uma distribuição sem console.
- Erros durante uma janela de seleção ou durante escrita podem chegar ao tratamento global sem contexto operacional suficiente.
- A camada web registra exceções inesperadas no log do Gunicorn/Flask e retorna HTTP 500 sem expor o traceback ao usuário.
- O processamento HTTP usa um único worker Gunicorn por decisão operacional para evitar concorrência desnecessária em processamento pesado; requisições simultâneas aguardam na fila.

## 14. Bugs Conhecidos

### BUG-001 — `selector.py` executava leitura de arquivo no import

**Status:** Corrigido

**Descrição:** O auxiliar `selector.py` executava `pd.read_excel("NotaServico.xlsx")` no nível do módulo. O arquivo não existe na raiz atual e o auxiliar não era usado pelo fluxo principal.

**Comportamento esperado:** Importar ou executar o auxiliar deveria exigir um arquivo somente quando uma função/rotina de leitura fosse explicitamente chamada, ou deveria informar claramente o arquivo necessário.

**Comportamento atual:** `selector.py` não faz mais parte do projeto. Os módulos do fluxo principal importam sem depender dele.

**Causa raiz:** Leitura e `print(df.dtypes)` foram deixados como efeitos colaterais no corpo do módulo.

**Arquivos envolvidos:** `selector.py` (removido); arquivo ausente `NotaServico.xlsx`.

**Correção aplicada:** `selector.py` foi removido do repositório, conforme autorização, eliminando o efeito colateral de importação e impedindo que o auxiliar seja incluído em futuros commits.

**Como validar:** Confirmar `test ! -e selector.py` e importar os 13 módulos principais; ambos foram executados nesta tarefa.

**Data da identificação:** 2026-09-03

**Data da correção:** 2026-09-03

### BUG-002 — Referência de logo inexistente no README

**Status:** Corrigido

**Descrição:** O `README.md` referenciava `logo.png`, mas esse arquivo não existe no repositório. O recurso existente usado pela GUI é `logo_topo.png`.

**Comportamento esperado:** A imagem indicada na documentação deveria existir ou a referência deveria apontar para o recurso correto.

**Comportamento atual:** As referências do README apontam para `logo_topo.png`, que está presente no repositório.

**Causa raiz:** Divergência entre o nome usado na documentação e o nome do arquivo visual mantido no projeto.

**Arquivos envolvidos:** `README.md`, `logo_topo.png` e ausência de `logo.png`.

**Correção aplicada:** As duas referências a `logo.png` no README foram alteradas para `logo_topo.png`: imagem do cabeçalho e árvore de arquivos.

**Como validar:** Confirmar que `README.md` não contém `logo.png`, contém `logo_topo.png` e que `logo_topo.png` existe.

**Data da identificação:** 2026-09-03

**Data da correção:** 2026-09-03

Não foram registrados outros bugs funcionais como confirmados sem arquivos de entrada reais ou uma especificação externa que permita comprovar o comportamento esperado.

## 15. Dívida Técnica

### Alta

- Ainda não há testes automatizados para o pipeline fiscal nem fixtures Excel/HTML; existem somente testes mínimos da camada HTTP.
- Os contratos de entrada estão espalhados entre `configs.py` e loaders, sem validação de schema e sem mensagens específicas por coluna/arquivo.
- O merge não declara cardinalidade; duplicidades podem produzir múltiplas linhas sem uma decisão explícita de negócio.
- O arquivo de saída tem nome fixo e é aberto diretamente, sem confirmação, versionamento ou backup.

### Média

- `main.py` concentra muitas responsabilidades: UI, regras de fluxo, persistência Excel e tratamento de erros.
- Loaders de Matriz e Filial repetem a estrutura de leitura, renomeação e conversão.
- Regras de negócio e strings de status estão distribuídas entre `main.py`, `motor.py`, `comparacao.py`, `arquivos.py` e `configs.py`.
- `requirements.txt` inclui ferramentas de empacotamento junto com dependências de runtime e usa UTF-16, o que dificulta inspeção manual e interoperabilidade.
- O template HTTP, o CSS e o JavaScript permanecem embutidos em `webapp.py`; há teste do fluxo JavaScript em DOM simulado, mas ainda não há teste de integração executado em um navegador real.
- Há imports aparentemente não utilizados (`numpy` em `arquivos.py`, `StringIO` em `layouts/filial_mg.py`, entre outros); não foram removidos por não fazerem parte do escopo.

### Baixa

- README e implementação ainda usam terminologia diferente de Filial/Filial MG em alguns pontos.
- Não há metadados de versão da aplicação, changelog formal ou convenção registrada para nomes de arquivos de entrada.
- Não há documentação de amostras de colunas em arquivos reais.

### Crítica

- Nenhuma dívida classificada como crítica foi comprovada nesta análise.

## 16. Melhorias Identificadas

Estas são oportunidades documentadas, não implementadas nesta tarefa:

- Criar fixtures mínimos e testes unitários para normalização, chaves, merge, tolerâncias, cancelamentos, recusadas e reprocessamento.
- Criar teste de integração que produza e reabra o workbook de saída para validar abas, colunas e proteção.
- Centralizar/validar schemas de entrada antes das transformações.
- Definir política para duplicidades, chaves vazias e valores nulos antes de alterar o merge.
- Extrair contratos e regras de comparação do orquestrador para componentes menores sem mudar o comportamento sem autorização.
- Tornar o caminho do arquivo de saída configurável e evitar sobrescrita silenciosa.
- Separar dependências de runtime das dependências de build e normalizar a codificação do `requirements.txt`, após validar o processo de instalação usado pela equipe.
- Adicionar logging estruturado e mensagens de erro associadas à etapa/arquivo/coluna que falhou.
- Adicionar validação automatizada da interface em navegador real para seleção de unidade, troca de cenário, acessibilidade e responsividade.

## 17. Sprints / Trabalhos em Andamento

### SPRINT-001 — Análise inicial e consolidação do contexto

**Objetivo:** Registrar a arquitetura, o fluxo de dados, as regras comprovadas, os riscos e as pendências do estado atual.

**Status:**
- Concluído

**Tarefas:**
- [x] Inspecionar estrutura, fontes, recursos e dependências.
- [x] Identificar ponto de entrada e componentes.
- [x] Mapear entradas, transformações, comparações e saídas.
- [x] Separar regras confirmadas de hipóteses.
- [x] Registrar bugs comprováveis e dívida técnica.
- [x] Criar `CONTEXTO.md`.
- [x] Validar que somente `CONTEXTO.md` foi criado nesta tarefa; alterações pré-existentes em bytecode foram preservadas.

**Dependências:** acesso ao código-fonte local.

**Bloqueios:** ausência de arquivos reais de entrada/saída impede validação ponta a ponta.

**Critérios de conclusão:** documento criado na raiz e consistente com o código analisado.

### SPRINT-002 — Validação funcional com amostras reais

**Objetivo:** Confirmar o comportamento da aplicação com arquivos reais de Matriz e Filial.

**Status:**
- Não iniciado

**Tarefas:**
- [ ] Obter amostras autorizadas de ERP, SAT, CT-e, Qive, Serviços e arquivo anterior.
- [ ] Executar um cenário por layout com documentos lançados e não lançados.
- [ ] Validar divergência de valores, cancelamento, recusada e reprocessamento.
- [ ] Comparar abas/colunas geradas com a expectativa operacional.

**Dependências:** arquivos de entrada reais e critérios de negócio confirmados.

**Bloqueios:** nenhum arquivo de amostra está versionado no repositório.

**Critérios de conclusão:** cenários reproduzíveis documentados e resultados revisados pelo responsável funcional.

### SPRINT-003 — Dockerização HTTP

**Objetivo:** Disponibilizar a aplicação por HTTP em container Linux, mantendo a lógica fiscal existente e publicando a porta 5011 sem IP fixo.

**Status:**
- Concluído

**Tarefas:**
- [x] Criar camada Flask/Gunicorn reutilizando o pipeline existente.
- [x] Separar o pipeline comum em `processamento.py` para uso desktop e HTTP.
- [x] Criar `Dockerfile` com Python 3.14 slim e usuário não-root.
- [x] Criar `compose.yaml` com `5011:5011`, volume de saída, restart policy e healthcheck.
- [x] Criar `.dockerignore` e dependências de runtime do container.
- [x] Validar build, startup, logs, healthcheck, publicação e reinício.

**Dependências:** Docker Engine/Compose e acesso à rede para baixar imagem base e pacotes durante o build.

**Bloqueios:** a homologação funcional do conteúdo dos Excel permanece sob responsabilidade do usuário.

**Critérios de conclusão:** imagem construída, container saudável, aplicação escutando em `0.0.0.0:5011`, acesso HTTP local e pelo IP real de teste validados.

### SPRINT-004 — Fluxo progressivo da interface web

**Objetivo:** Organizar a tela HTTP para iniciar pela seleção de unidade e liberar somente os anexos aplicáveis, preservando o contrato atual do Flask.

**Status:**
- Concluído

**Tarefas:**
- [x] Exibir `logo_topo.png` no cabeçalho por rota dedicada e `url_for()`.
- [x] Exibir `Matriz` e `Filial` como seleção inicial com os valores atuais do backend.
- [x] Ocultar e desabilitar os conjuntos de upload no estado inicial.
- [x] Exibir/habilitar somente os campos da unidade selecionada.
- [x] Limpar uploads ao alternar entre Matriz e Filial.
- [x] Manter o botão bloqueado até os requisitos mínimos de interface serem atendidos.
- [x] Atualizar testes HTTP, persistir o teste de interação JavaScript e registrar a alteração no contexto técnico.

**Dependências:** JavaScript habilitado no navegador; contrato de campos existente em `webapp.py`; Node.js para executar o teste persistente do frontend.

**Bloqueios:** validação visual em navegador real e homologação funcional dos arquivos Excel ainda não foram executadas.

**Critérios de conclusão:** estado inicial, seleção de cada unidade, limpeza na troca, habilitação do botão, rota da logo e compatibilidade dos nomes de campos validados tecnicamente.

## 18. Roadmap

### Curto prazo

- Confirmar com usuários e arquivos reais que as correções dos dois bugs não alteram o fluxo operacional esperado.
- Validar a interface web em navegador real, incluindo telas menores, foco por teclado e troca entre unidades.
- Criar cobertura automatizada para as funções puras de limpeza e comparação.
- Validar os contratos dos arquivos reais e registrar exemplos de entrada não sensíveis.

### Médio prazo

- Adicionar validação de schema e mensagens de erro por arquivo/coluna.
- Definir e testar a política de duplicidades, chaves vazias, valores nulos e sobrescrita do relatório.
- Realizar refatoração incremental do orquestrador e dos loaders somente após preservar o comportamento em testes.

### Longo prazo

- Não determinado pela análise atual. Não há requisito funcional adicional formalizado no código ou no README além da evolução técnica listada acima.

## 19. Histórico de Alterações

### 2026-09-03 — Criação do contexto técnico inicial

**Objetivo:** Consolidar o funcionamento atual do Comparador de Notas Fiscais para continuidade entre sessões.

**Arquivos modificados:** `CONTEXTO.md` criado.

**Alterações realizadas:** Documentados estrutura, módulos, dependências, fluxo de dados, regras confirmadas, hipóteses, bugs, dívida técnica, roadmap e instruções de execução/validação.

**Impactos:** Nenhuma alteração funcional na aplicação. Bytecodes que já estavam modificados no Git não foram tocados.

**Validações executadas:** Inventário estrutural; leitura dos módulos; análise AST dos 15 fontes Python; importação dos módulos principais; teste sintético das regras centrais; verificação de recursos ausentes e status do Git.

**Resultado:** Documento vivo criado; validação ponta a ponta permanece pendente por ausência de arquivos de entrada reais.

### 2026-09-03 — Correção dos BUG-001 e BUG-002

**Objetivo:** Remover o auxiliar obsoleto que falhava no import e corrigir a referência de recurso visual na documentação.

**Arquivos modificados:** `selector.py` removido; `README.md` atualizado; `CONTEXTO.md` atualizado.

**Alterações realizadas:** Remoção de `selector.py`; substituição das referências `logo.png` por `logo_topo.png` no README; atualização dos estados dos bugs, estrutura, roadmap e histórico.

**Impactos:** Nenhuma alteração no fluxo funcional da aplicação; o auxiliar removido não era importado por nenhum módulo principal.

**Validações executadas:** `selector.py` ausente; 13 módulos principais importados; busca sem referências a `logo.png` no README; `logo_topo.png` presente.

**Resultado:** BUG-001 e BUG-002 corrigidos e documentados como corrigidos.

### 2026-09-03 — Dockerização da aplicação para acesso HTTP

**Objetivo:** Adaptar a aplicação desktop para execução em servidor Linux através de Docker, com acesso pela porta TCP 5011.

**Arquivos modificados:** `main.py`, `seletor_unidade.py`, `README.md` e `CONTEXTO.md`.

**Arquivos criados:** `processamento.py`, `webapp.py`, `Dockerfile`, `compose.yaml`, `.dockerignore`, `requirements-docker.txt` e `tests/test_webapp.py`.

**Alterações realizadas:** extração do pipeline comum para `processamento.py`; criação de formulário HTTP Flask com `/`, `/process` e `/health`; uploads temporários; download do relatório; importação tardia de Tkinter para permitir execução headless; container Python 3.14 slim com Gunicorn, usuário não-root, volume nomeado de saída e publicação `5011:5011`.

**Impactos:** regras de comparação e formato dos dados não foram alterados intencionalmente. A execução desktop continua disponível por `python main.py`; a execução containerizada usa a interface HTTP.

**Validações executadas:** testes HTTP unitários (`3` testes OK); `docker compose config`; build da imagem; container `healthy`; logs de Gunicorn sem erro crítico; publicação `0.0.0.0:5011->5011/tcp`; HTTP 200 em localhost e no IP real de teste `172.17.55.165`; reinício com retorno a `healthy`.

**Resultado:** dockerização técnica concluída. A validação funcional dos arquivos Excel resultantes permanece pendente e será executada manualmente pelo responsável pelo projeto.

### 2026-09-03 — Interface web com seleção progressiva de unidade

**Objetivo:** Melhorar o fluxo visual da tela Flask, apresentando a escolha entre Matriz e Filial antes dos anexos e incorporando a logo existente.

**Arquivos modificados:** `webapp.py`, `tests/test_webapp.py`, `tests/test_frontend_flow.js` e `CONTEXTO.md`.

**Alterações realizadas:** criada a rota `GET /logo_topo.png`; o template passou a referenciar a imagem com `url_for()`; a seleção de unidade passou a usar radios com os valores existentes; os uploads são ocultados/desabilitados inicialmente e somente o conjunto selecionado é liberado; a troca de unidade limpa os inputs de arquivo; o botão verifica os requisitos mínimos de interface antes de permitir o envio; CSS responsivo e estados de foco foram adicionados inline; a indicação visual da opção selecionada usa classe JavaScript, sem depender de `:has`; o teste de interação frontend foi persistido.

**Impactos:** nenhuma regra de comparação, leitura de arquivos, processamento Pandas, contrato de nomes de campos ou rota `POST /process` foi alterado. O uso da interface depende de JavaScript habilitado.

**Validações executadas:** suíte HTTP com 5 testes OK; compilação Python; `node tests/test_frontend_flow.js` executando o JavaScript real para estado inicial, seleção de Matriz/Filial, liberação, limpeza na troca, indicação visual e bloqueio do envio; validação da rota da logo e revisão de paths/contratos.

**Resultado:** fluxo progressivo implementado; validação funcional do conteúdo dos Excel permanece pendente e será executada manualmente pelo responsável pelo projeto.

### 2026-09-04 — Implementação do favicon da interface web

**Objetivo:** Derivar um favicon da identidade visual existente e disponibilizá-lo na interface HTTP.

**Arquivos modificados:** `webapp.py`, `tests/test_webapp.py`, `README.md` e `CONTEXTO.md`.

**Arquivo criado:** `favicon.png`.

**Alterações realizadas:** criada uma versão quadrada RGBA da `logo_topo.png`; adicionada a rota `GET /favicon.png`; incluída a referência `<link rel="icon">` no cabeçalho HTML; adicionados testes para a rota e para a referência renderizada.

**Impactos:** nenhuma regra fiscal ou contrato de upload foi alterado. O favicon é usado pela interface HTTP e é incluído automaticamente no contexto Docker pela cópia da raiz do projeto.

**Validações executadas:** suíte HTTP com 6 testes OK; `node tests/test_frontend_flow.js`; compilação Python; inspeção técnica do arquivo como PNG 256×256 RGBA.

**Resultado:** favicon implementado e servido pela aplicação web.

### 2026-09-04 — Substituição do favicon pelo ícone X

**Objetivo:** Substituir o favicon baseado no wordmark por um ícone X mais legível em tamanhos reduzidos.

**Arquivos modificados:** `webapp.py`, `tests/test_webapp.py`, `README.md` e `CONTEXTO.md`.

**Arquivo removido:** `favicon.png`.

**Arquivo criado:** `favicon.ico`.

**Alterações realizadas:** o ícone X anexado foi preparado como favicon com os tamanhos 16, 32, 48 e 256 px; a rota e a referência HTML foram alteradas de PNG para ICO; os testes foram ajustados ao novo contrato.

**Impactos:** nenhuma regra fiscal ou contrato de upload foi alterado. O favicon anterior foi removido conforme solicitado.

**Validações executadas:** suíte HTTP, teste frontend, compilação Python e inspeção do cabeçalho ICO e dos quatro recursos PNG embutidos.

**Resultado:** favicon X implementado na interface web.

### Histórico anterior observado

O Git registra, entre outros, os seguintes marcos anteriores:

- `2026-08-03` — ajustes visuais e troca de menções de Filial MG para Filiais.
- `2026-08-03` — limpeza de números de serviço considerando ano vigente e anterior.
- `2026-07-20` — conversão de chaves para texto no merge.
- `2026-07-14` — correções para comparações sem relatórios e configuração de relatórios opcionais.
- `2026-07-09` — atualização de `requirements.txt` e criação do README.
- `2026-07-07` — criação da lógica de notas recusadas e da interface visual de múltipla seleção.

## 20. Decisões Técnicas

### DEC-001 — Manter layouts separados por unidade

**Contexto:** Matriz e Filial possuem fontes externas e nomes de colunas diferentes.

**Decisão:** Usar `LayoutMatriz` e `LayoutFilialMG`, compartilhando `LayoutBase` para o contrato comum.

**Motivo:** Permitir loaders e ordem de comparação específicos sem duplicar o fluxo global de `main.py`.

**Alternativas consideradas:** Não determinado pela análise atual; não há registro explícito de alternativas no projeto.

**Impactos:** O código compartilha o motor, mas mantém duplicação entre loaders de formatos parecidos.

### DEC-002 — Consumir o ERP sequencialmente

**Contexto:** O mesmo DataFrame ERP precisa ser confrontado com mais de um tipo de documento.

**Decisão:** A ordem configurada em `ORDEM_COMPARACAO` define qual comparação consome o ERP primeiro; o restante segue para a próxima.

**Motivo:** Implementar o comportamento documentado em `LayoutBase` e produzir `Notas Somente no ERP` com o que não foi consumido.

**Alternativas consideradas:** Não determinado pela análise atual.

**Impactos:** A ordem pode influenciar o resultado quando chaves ou registros se sobrepõem entre tipos; isso requer validação funcional.

### DEC-003 — Persistir recusadas dentro do workbook mensal

**Contexto:** Não existe banco de dados ou outra persistência externa.

**Decisão:** Usar a aba `Notas Recusadas` e os status das abas de comparação anteriores como fonte de chaves recusadas.

**Motivo:** Reaplicar a supressão no próximo processamento mantendo o fluxo baseado em arquivos.

**Alternativas consideradas:** Não determinado pela análise atual.

**Impactos:** A continuidade depende da preservação das abas, dos nomes e das colunas do workbook anterior.

### DEC-004 — Não modificar o código na análise inicial

**Contexto:** O escopo desta tarefa exige compreensão e documentação, proibindo correções automáticas.

**Decisão:** Criar/atualizar somente `CONTEXTO.md` e registrar problemas para trabalhos futuros.

**Motivo:** Preservar o comportamento existente e evitar mudanças fora da autorização.

**Alternativas consideradas:** Corrigir imediatamente os problemas encontrados; descartada nesta tarefa por restrição explícita de escopo.

**Impactos:** Nenhum impacto funcional identificado; os dois bugs tratados nesta decisão estão corrigidos.

### DEC-005 — Adicionar camada HTTP separada e manter a GUI

**Contexto:** O código original usa Tkinter e não possui servidor HTTP, mas o requisito de Docker exige acesso por `http://IP_DO_SERVIDOR:5011`.

**Decisão:** Criar `webapp.py` com Flask/Gunicorn e extrair o pipeline para `processamento.py`; manter `main.py` como entrada desktop.

**Motivo:** Atender ao acesso HTTP sem executar Tkinter no container e sem duplicar as regras de negócio entre interfaces.

**Alternativas consideradas:** Executar Tkinter com ambiente gráfico virtual não atenderia naturalmente ao acesso HTTP; criar outro serviço de comparação duplicaria o pipeline existente. Ambas foram descartadas para esta implementação.

**Impactos:** O container usa upload HTTP e download do resultado; o processamento continua síncrono e usa um worker Gunicorn. A GUI permanece dependente de ambiente desktop.

### DEC-006 — Publicar a porta sem amarrar IP do host

**Contexto:** O endereço do Docker Host varia entre ambientes.

**Decisão:** Usar `ports: ["5011:5011"]` no Compose e bind Gunicorn em `0.0.0.0:5011`.

**Motivo:** Deixar o Docker publicar em todas as interfaces do host, permitindo `http://IP_DO_SERVIDOR:5011` sem hardcode de endereço.

**Alternativas consideradas:** Binding em `127.0.0.1` ou em IP fixo do host; não utilizadas porque restringiriam ou tornariam a configuração dependente do ambiente.

**Impactos:** Firewall, ACL, VLAN, roteamento e NAT continuam fora do escopo e podem bloquear acesso remoto mesmo com a publicação correta.

### DEC-007 — Usar volume nomeado somente para saída

**Contexto:** Uploads HTTP são temporários e o relatório gerado deve sobreviver à recriação do container.

**Decisão:** Montar `conferencia_nf_output` em `/app/output`; manter uploads em diretório temporário removido ao final da requisição.

**Motivo:** Persistir somente o artefato de saída necessário, sem persistir dados de entrada temporários.

**Alternativas consideradas:** Não persistir saída ou montar diretórios amplos do host; não adotadas para evitar perda do relatório ou exposição desnecessária de paths.

**Impactos:** O volume precisa ser mantido pelo operador; `docker compose down -v` remove o volume e os relatórios nele armazenados.

### DEC-008 — Servir a logo raiz por rota dedicada

**Contexto:** `logo_topo.png` existe na raiz do projeto e não há diretório `static/` ou template separado.

**Decisão:** Servir somente esse arquivo por `GET /logo_topo.png` usando `send_from_directory()` e referenciá-lo no template com `url_for()`.

**Motivo:** Preservar a localização existente da imagem sem expor a raiz inteira do repositório como diretório estático.

**Alternativas consideradas:** Mover/copiá-la para `static/` ou configurar a raiz do projeto como diretório estático; não adotadas por introduzirem movimentação, duplicação ou exposição desnecessária.

**Impactos:** `webapp.py` passou a possuir uma rota de recurso visual; não houve alteração no processamento.

### DEC-009 — Preservar o contrato HTTP e controlar a unidade no cliente

**Contexto:** O backend procura `unidade` e arquivos com prefixos como `Matriz__arquivo_sat` e `Filial__arquivo_qive_entrada`.

**Decisão:** Implementar a seleção progressiva somente no template/JavaScript, mantendo os valores, nomes dos inputs e a rota `POST /process` existentes.

**Motivo:** Alterar a experiência de uso sem alterar regras fiscais, parsing de arquivos ou contratos do servidor.

**Alternativas consideradas:** Criar endpoints distintos por unidade ou alterar o payload para nomes sem prefixo; não adotadas por ampliarem o escopo e quebrarem compatibilidade.

**Impactos:** A interface requer JavaScript habilitado; o backend continua responsável pela validação definitiva.

## 21. Riscos Conhecidos

- Um arquivo com nome de coluna, aba ou formato diferente pode falhar somente durante a leitura ou exportação.
- Chaves vazias ou não únicas podem gerar correspondências incorretas ou múltiplas linhas no merge.
- A comparação sequencial pode atribuir um registro ERP ao primeiro tipo da ordem quando houver sobreposição de chaves.
- Valores monetários em formato diferente do padrão brasileiro podem ser convertidos de forma inadequada ou virar `NaN`.
- O parser de CT-e da Matriz usa a primeira tabela HTML e depende das colunas exatas e de `html5lib`.
- O número de serviço depende do ano corrente do sistema para reconhecer prefixos; a mudança de ano pode alterar a normalização.
- O reprocessamento depende dos nomes exatos das abas e do texto exato do status.
- O workbook de saída pode sobrescrever um arquivo existente com o mesmo nome e não há confirmação documentada.
- A aplicação depende de Tkinter e foi projetada/documentada para Windows; a execução em ambientes sem GUI não foi validada.
- Recursos visuais podem não aparecer se não forem empacotados corretamente no PyInstaller.
- O acesso pelo IP real pode ser bloqueado por firewall do host ou por camadas corporativas externas ao Docker; nenhuma política de firewall foi alterada.
- O formulário web permite enviar arquivos de entrada, mas a validação semântica dos dados fiscais continua fora desta tarefa.
- Se o JavaScript estiver desabilitado, a interface progressiva manterá os anexos ocultos e o usuário não conseguirá iniciar o processamento pela tela web.
- A seleção progressiva foi validada com testes HTTP e execução controlada do JavaScript persistida em `tests/test_frontend_flow.js`; a renderização visual em navegadores e tamanhos de tela reais ainda requer validação operacional.

## 22. Como Executar o Projeto

### Preparação

1. Usar Windows com Python compatível com o declarado no README, atualmente Python 3.14 ou superior.
2. Criar ambiente virtual: `python -m venv venv`.
3. Ativar o ambiente conforme o sistema operacional.
4. Instalar dependências com `pip install -r requirements.txt` ou com a lista explícita no README. A leitura/instalação do arquivo UTF-16 deve ser validada no ambiente alvo.

### Execução

```bash
python main.py
```

O operador seleciona a unidade, os arquivos ERP/documentos e, opcionalmente, o arquivo da análise anterior. Pelo menos um relatório ERP e um documento externo novo ou pendente anterior precisam existir.

### Saídas

O arquivo é gravado no diretório corrente como `comparacao_notas.xlsx` para Matriz ou `comparacao_notas_filial.xlsx` para Filial. O processo não recebe argumentos de linha de comando e não usa `.env`.

### Execução via Docker

Arquivos usados: `Dockerfile`, `compose.yaml`, `.dockerignore` e `requirements-docker.txt`.

Imagem base: `python:3.14-slim`.

Processo: Gunicorn executando `webapp:app` com um worker, timeout de 300 segundos e bind em `0.0.0.0:5011`.

Interface HTTP:

1. Acessar `http://IP_DO_SERVIDOR:5011/`.
2. Selecionar `Matriz` ou `Filial`.
3. Anexar os arquivos da unidade exibida; os nomes enviados preservam o formato prefixado usado pelo backend.
4. Confirmar que o botão é liberado após um arquivo ERP e um documento/arquivo anterior serem selecionados.
5. Acionar `Processar e baixar relatório`.

O recurso visual `logo_topo.png` é servido por `GET /logo_topo.png`. Os uploads da unidade não selecionada permanecem ocultos, desabilitados e não são enviados; ao trocar a unidade, os arquivos escolhidos são limpos.

Build:

```bash
docker compose build
```

Inicialização:

```bash
docker compose up -d
```

Parada:

```bash
docker compose down
```

Diagnóstico:

```bash
docker compose ps
docker compose logs
docker compose config
```

Portas:

- Porta externa no Docker Host: `5011`.
- Porta interna do container: `5011`.
- Publicação: `5011:5011`, sem endereço IP fixo.
- URL conceitual: `http://IP_DO_SERVIDOR:5011`.

Volumes:

- `conferencia_nf_output` → `/app/output`: persistente, usado para relatórios gerados.
- Uploads: diretório temporário interno, removido ao final de cada requisição.

Variáveis de ambiente:

- `OUTPUT_DIR`: diretório de saída da aplicação; padrão `/app/output`.
- Não há variável para o IP do Docker Host.

### Empacotamento declarado no README

```bash
pip install pyinstaller
pyinstaller --onefile --icon=logo.ico --add-data "logo.ico;." --add-data "logo_topo.png;." --name "ConferenciaNotas" main.py
```

Esse comando foi documentado no README, mas a geração do executável não foi executada nesta análise.

## 23. Como Validar o Funcionamento

### Validações estáticas já executadas

- Analisar AST de todos os 17 arquivos Python atuais, incluindo testes, para confirmar sintaxe.
- Importar os módulos principais sem iniciar a GUI.
- Verificar presença dos recursos `logo.ico` e `logo_topo.png` e ausência de `logo.png`/`NotaServico.xlsx`.
- Executar cenários sintéticos do motor para status lançado/não lançado, cancelamento, chave de serviço e restante ERP.

### Validações técnicas Docker já executadas

- `python -B -m unittest discover -s tests -v`: 5 testes HTTP aprovados.
- `docker compose config`: configuração válida, com `5011` publicado para `5011`.
- `docker compose build`: imagem construída com sucesso.
- `docker compose up -d`: container iniciado.
- `docker compose ps`: container `healthy`, executando como `appuser`.
- `docker compose logs`: Gunicorn ouvindo em `0.0.0.0:5011`, sem erro crítico de inicialização.
- `docker port`: `5011/tcp -> 0.0.0.0:5011` e IPv6 equivalente.
- `curl http://localhost:5011/health`: HTTP 200.
- `curl http://localhost:5011/`: HTTP 200.
- `curl http://172.17.55.165:5011/health`: HTTP 200; `172.17.55.165` foi usado somente no ambiente de teste.
- Reinício via `docker compose restart`: container retornou a `healthy` e `/health` voltou HTTP 200.
- `GET /` foi validado com a logo referenciada, radios de `Matriz`/`Filial`, seções de upload inicialmente ocultas/desabilitadas e botão inicialmente desabilitado.
- `GET /logo_topo.png` foi validado com HTTP 200 e `Content-Type` PNG.
- `GET /favicon.ico` foi validado com HTTP 200 e cabeçalho ICO válido; o arquivo contém recursos PNG nos tamanhos 16, 32, 48 e 256 px, derivados do ícone X anexado.
- O JavaScript real embutido no template foi executado em harness Node: seleção de Matriz e Filial, exibição/habilitação do conjunto correto, limpeza dos arquivos na troca, bloqueio/liberação do botão e bloqueio durante o envio.
- `node tests/test_frontend_flow.js`: teste persistente do fluxo JavaScript aprovado.
- `python3 -m py_compile webapp.py tests/test_webapp.py` foi executado com sucesso.
- A validação funcional dos arquivos Excel resultantes não foi realizada e permanece sob responsabilidade do usuário.

Não foi executado teste visual em navegador real, pois não há navegador headless ou Playwright/Selenium disponível no ambiente desta análise; a responsividade foi implementada por CSS com viewport, grid adaptável e media query para telas menores.

### Validação funcional recomendada

Com amostras autorizadas:

1. Executar Matriz com ERP + SAT, verificando aba, status, chave e valor.
2. Executar Matriz com CT-e HTML, incluindo um valor com escala sem separador decimal.
3. Executar Matriz ou Filial com Serviços, verificando combinação número/CNPJ e data de cancelamento.
4. Executar Filial com Qive e CT-e Qive.
5. Reexecutar usando o workbook anterior, verificando que apenas `Não lançada no CSW` é reincorporado.
6. Marcar uma pendência como recusada, reexecutar com a nota ainda presente e verificar a supressão e a aba `Notas Recusadas`.
7. Remover a nota da base posterior e verificar a limpeza do ledger.
8. Reabrir o `.xlsx` com pandas/openpyxl e confirmar nomes de abas, colunas, filtros, congelamento e dados exportados.

Esses cenários ainda não foram executados de ponta a ponta porque não existem arquivos de amostra no repositório.

## 24. Última Análise do Projeto

- **Data:** 2026-09-04.
- **Objetivo:** Substituir o favicon da interface HTTP por um ícone X mais legível, preservando o fluxo progressivo de seleção de unidade.
- **Arquivos analisados:** `CONTEXTO.md`, `webapp.py`, `tests/test_webapp.py`, `tests/test_frontend_flow.js`, `processamento.py`, `layouts/base.py`, `layouts/matriz.py`, `layouts/filial_mg.py`, `main.py`, `Dockerfile`, `compose.yaml`, `.dockerignore`, `requirements-docker.txt`, `README.md`, `logo_topo.png` e `favicon.ico`; os contratos de campos e rotas foram conferidos nos módulos relacionados.
- **Estado identificado:** interface HTTP com logo e favicon servidos por rotas dedicadas; seleção inicial por radios; uploads por unidade ocultos/desabilitados até a escolha; limpeza segura na troca; botão controlado por requisitos mínimos de interface; backend, Docker e nomes de campos preservados.
- **Pendências:** validação visual em navegador real e telas físicas; homologação funcional do conteúdo dos arquivos Excel; validação com arquivos reais de entrada; avaliação futura de concorrência, limites de upload e política operacional do volume.
