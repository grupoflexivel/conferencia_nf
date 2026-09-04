<div align="center">

<img src="logo_topo.png" alt="Grupo Flexível" width="220"/>

# 📊 Conferência de Notas Fiscais — ERP × Documentos Fiscais

**Comparador automático de notas fiscais que cruza os lançamentos do ERP com os documentos fiscais reais e aponta, nota a nota, o que ainda não foi lançado.**

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Engine-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-HTTP%20API-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-FF6F00?style=for-the-badge)
![Excel](https://img.shields.io/badge/Excel-Relatórios-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)

![Status](https://img.shields.io/badge/status-em%20produção-success?style=flat-square)
![Platform](https://img.shields.io/badge/plataforma-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/licença-Proprietária-lightgrey?style=flat-square)

</div>

---

## 📌 Descrição do Projeto

A conferência manual de notas fiscais é lenta, repetitiva e sujeita a falhas: o analista precisa abrir o relatório do ERP, abrir os relatórios de documentos fiscais e cruzar **linha por linha** para descobrir o que ainda não foi lançado.

Esta aplicação **automatiza esse cruzamento**. Ela recebe o relatório de notas lançadas no ERP (**Consistem/CSW**) e os relatórios externos de documentos fiscais — **Notas de Entrada, Notas de Serviço e CT-e (Conhecimento de Transporte Eletrônico)** — e gera um relatório Excel consolidado que responde à pergunta central da conferência:

> ✅ **Este documento fiscal foi ou não foi lançado no ERP?**

Além de identificar o que falta lançar, o comparador também **destaca divergências de valores**, sinaliza **notas canceladas/recusadas** e mantém a **continuidade entre meses**, reprocessando automaticamente as pendências do período anterior.

## ✨ Funcionalidades

- ✅ **Cruzamento automático ERP × documentos externos** Preferencialmente pela chave de acesso, ou número do documento e CNPJ/CPF para as notas de serviço.
- ✅ **Identificação de notas não lançadas** — aponta com clareza cada documento fiscal ausente no ERP.
- ✅ **Detecção de divergências de valores** entre o valor do documento e o valor lançado no ERP.
- ✅ **Suporte a múltiplos tipos de documento** — Notas de Entrada, Notas de Serviço e CT-e.
- ✅ **Múltiplas unidades / layouts** — Matriz (SAT) e Filial MG (Qive), cada uma com seu formato de relatório.
- ✅ **Reprocessamento mês a mês** — as pendências do período anterior são reincorporadas automaticamente na análise atual.
- ✅ **Gestão de notas recusadas** — o operador marca a nota como *Recusada* e ela é suprimida das análises futuras, com um registro que se limpa sozinho.
- ✅ **Tratamento de notas canceladas** — reconhece situações de cancelamento e ajusta o status da conferência.
- ✅ **Interface gráfica simples** — seleção de unidade e de arquivos via janelas (Tkinter), sem necessidade de terminal.
- ✅ **Relatório Excel formatado** — uma aba por tipo de documento, mais as abas *Notas Somente no ERP* e *Notas Recusadas*.

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia |
|-----------|------------|
| **Linguagem** | Python 3.14 |
| **Processamento de dados** | pandas · numpy |
| **Leitura de Excel** | openpyxl |
| **Geração de Excel** | XlsxWriter |
| **Parsing de relatórios HTML (CT-e)** | html5lib · lxml |
| **Interface gráfica** | Tkinter (biblioteca padrão) |
| **Empacotamento (.exe)** | PyInstaller |
| **Servidor HTTP** | Flask · Gunicorn |

---

## 📋 Pré-requisitos

Para executar a aplicação são necessários os seguintes requisitos:

- 🐍 **Python 3.14** (ou superior) instalado — [python.org/downloads](https://www.python.org/downloads/)
- 📦 **pip** disponível no `PATH` (já incluso no instalador oficial do Python)
- 🪟 **Windows** — a interface e o empacotamento são pensados para o ambiente Windows
- 🧾 **Relatórios de origem** exportados do ERP e dos sistemas de documentos fiscais (arquivos `.xlsx` / `.xls` / relatório HTML de CT-e)

> 💡 O `Tkinter` já acompanha a instalação padrão do Python no Windows — não é necessário instalá-lo à parte.

---

## 🚀 Como Executar o Projeto

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/grupoflexivel/conferencia-notas-fiscais.git
cd conferencia-notas-fiscais
```

### 2️⃣ Criar e ativar um ambiente virtual

```bash
# Criação
python -m venv venv

# Ativação (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ativação (Windows CMD)
venv\Scripts\activate.bat
```

### 3️⃣ Instalar as dependências

```bash
pip install pandas numpy openpyxl xlsxwriter html5lib lxml
```

> 📌 Recomendado congelar o ambiente em um `requirements.txt` para reprodutibilidade:
> ```bash
> pip freeze > requirements.txt
> # e, futuramente:
> pip install -r requirements.txt
> ```

### 4️⃣ Executar a aplicação

```bash
python main.py
```

Ao rodar, a aplicação abre uma janela para você:

1. **Selecionar a unidade** — `Matriz` ou `Filial MG`.
2. **Selecionar os arquivos** de origem (ERP, documentos externos e, opcionalmente, a análise do mês anterior).
3. **Aguardar o processamento** — ao final, o relatório `comparacao_notas.xlsx` (Matriz) ou `comparacao_notas_filial.xlsx` (Filial) é gerado na pasta de execução.

> ⚙️ A execução desktop não depende de arquivo `.env`; a execução via Docker usa apenas `OUTPUT_DIR` para definir o diretório persistente dos relatórios. A configuração de colunas, abas e chaves de comparação está centralizada em [`configs.py`](configs.py).

### 5️⃣ Executar via Docker

Para executar a interface HTTP em um servidor Linux com Docker Compose:

```bash
docker compose build
docker compose up -d
docker compose ps
```

A aplicação escuta em `0.0.0.0:5011` dentro do container e publica a porta `5011` do Docker Host. O acesso deve usar o endereço real do servidor:

```text
http://IP_DO_SERVIDOR:5011
```

O IP do servidor não é configurado no código, na imagem ou no Compose. Os relatórios são persistidos no volume nomeado `conferencia_nf_output`. Para acompanhar os logs ou parar o serviço:

```bash
docker compose logs
docker compose down
```

O endpoint `http://IP_DO_SERVIDOR:5011/health` retorna o estado técnico do serviço.

A interface web utiliza `logo_flexivel.ico` como ícone do navegador, servido pela rota `/logo_flexivel.ico`.

---

### 📦 (Opcional) Gerar o executável `.exe`

Para distribuir a ferramenta a usuários sem Python instalado:

```bash
pip install pyinstaller
pyinstaller --onefile --icon=logo.ico --add-data "logo.ico;." --add-data "logo_topo.png;." --name "ConferenciaNotas" main.py
```

O executável final é gerado na pasta `dist/`.

---

## 📂 Estrutura de Pastas

```
.
├── main.py                  # Ponto de entrada: orquestra todo o fluxo de conferência
├── processamento.py         # Pipeline reutilizável pela GUI e pela interface HTTP
├── webapp.py                # Interface HTTP Flask para execução em servidor
├── motor.py                 # Motor de comparação (merge ERP × documentos, análises)
├── configs.py               # Configuração central: colunas, abas e chaves de comparação
├── comparacao.py            # Regras de status, divergências e cancelamentos
├── limpeza.py               # Normalização de CNPJ, chaves, valores e números
├── relatorios_csw.py        # Consolidação dos relatórios do ERP (Consistem/CSW)
├── arquivos.py              # Reprocessamento das pendências do mês anterior
├── recusadas.py             # Coleta, supressão e registro de notas recusadas
├── excel_utils.py           # Formatação das planilhas de saída
├── seletor_unidade.py       # Interface gráfica (Tkinter): unidade e seleção de arquivos
├── Dockerfile                # Imagem Linux do serviço HTTP
├── compose.yaml              # Serviço, porta 5011, volume e healthcheck
├── requirements-docker.txt   # Dependências de runtime do container
├── .dockerignore             # Exclusões do contexto de build
├── layouts/                 # Layouts específicos por unidade
│   ├── base.py              #   → Classe base compartilhada
│   ├── matriz.py            #   → Matriz (SAT, CT-e, Serviços)
│   └── filial_mg.py         #   → Filial MG (Qive, CT-e, Serviços)
├── logo_topo.png            # Identidade visual
├── logo_flexivel.ico        # Favicon da interface web
└── README.md
```

---
## 👥 Autores / Contribuidores

| Autor | Contato |
|-------|---------|
| **Equipe de TI — Grupo Flexível** | 📧 [sistemas@grupoflexivel.com.br](mailto:sistemas@grupoflexivel.com.br) |
---

## 📄 Licença

Projeto **proprietário** — desenvolvido para uso interno do **Grupo Flexível**. Todos os direitos reservados.

Feito com 🐍 e ☕ pelo time de **TI do Grupo Flexível**
</div>
