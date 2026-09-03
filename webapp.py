import os
import shutil
import tempfile
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    render_template_string,
    request,
    send_file,
    send_from_directory,
)
from werkzeug.utils import secure_filename

from processamento import LAYOUTS, processar_conferencia


PORTA_INTERNA = 5011
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/app/output"))

ARQUIVOS_POR_UNIDADE = {
    "Matriz": [
        ("arquivo_anterior", "Notas da análise anterior"),
        ("arquivo_notas_entrada", "Notas de Entrada do Consistem"),
        ("arquivo_devolucoes", "Notas de Devolução do Consistem"),
        ("arquivo_sat", "Arquivo SAT"),
        ("arquivo_cte", "Arquivo de CT-e"),
        ("arquivo_servico", "Arquivo de Notas de Serviço"),
    ],
    "Filial": [
        ("arquivo_anterior", "Notas da análise anterior"),
        ("arquivo_notas_entrada", "Notas de Entrada do Consistem"),
        ("arquivo_devolucoes", "Notas de Devolução do Consistem"),
        ("arquivo_qive_entrada", "Notas de Entrada do Qive"),
        ("arquivo_cte", "Arquivo de CT-e do Qive"),
        ("arquivo_servico", "Arquivo de Notas de Serviço do Qive"),
    ],
}

FORMULARIO = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Conferência de Notas Fiscais</title>
  <style>
    :root {
      --ink: #15313a;
      --muted: #5d7178;
      --line: #d7e1e3;
      --surface: #ffffff;
      --surface-soft: #f5f8f8;
      --accent: #0b7370;
      --accent-dark: #075653;
      --accent-soft: #e3f2f0;
      --danger: #9b1c1c;
      --danger-soft: #fde8e8;
    }

    * { box-sizing: border-box; }

    body {
      background: #edf3f3;
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.5;
      margin: 0;
    }

    .page {
      margin: 0 auto;
      max-width: 900px;
      padding: clamp(1.25rem, 4vw, 3rem) 1rem 3rem;
      width: 100%;
    }

    .cabecalho {
      align-items: center;
      display: flex;
      gap: 1.25rem;
      margin-bottom: 1.5rem;
    }

    .logo {
      display: block;
      height: auto;
      max-width: min(160px, 42vw);
      width: 160px;
    }

    .eyebrow {
      color: var(--accent-dark);
      font-size: .75rem;
      font-weight: 700;
      letter-spacing: .12em;
      margin: 0 0 .2rem;
      text-transform: uppercase;
    }

    h1 {
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(1.65rem, 4vw, 2.35rem);
      line-height: 1.1;
      margin: 0;
    }

    .painel {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      box-shadow: 0 16px 36px rgba(21, 49, 58, .08);
      padding: clamp(1.25rem, 4vw, 2.25rem);
    }

    .etapa {
      border: 0;
      margin: 0;
      min-width: 0;
      padding: 0;
    }

    .etapa + .etapa { margin-top: 2rem; }

    .etapa__titulo {
      font-size: 1.05rem;
      font-weight: 700;
      margin-bottom: .35rem;
      padding: 0;
    }

    .etapa__ajuda,
    .campo__ajuda,
    .status-form {
      color: var(--muted);
      font-size: .9rem;
    }

    .etapa__ajuda { margin: 0 0 1rem; }

    .opcoes-unidade {
      display: grid;
      gap: .85rem;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .opcao-unidade {
      background: var(--surface-soft);
      border: 1px solid var(--line);
      border-radius: 10px;
      cursor: pointer;
      display: block;
      min-width: 0;
      padding: 1rem;
      transition: border-color .15s ease, background-color .15s ease;
    }

    .opcao-unidade:hover { border-color: var(--accent); }

    .opcao-unidade:focus-within {
      outline: 3px solid rgba(11, 115, 112, .24);
      outline-offset: 2px;
    }

    .opcao-unidade input {
      height: 1px;
      opacity: 0;
      position: absolute;
      width: 1px;
    }

    .opcao-unidade input:checked + .opcao-unidade__conteudo {
      color: var(--accent-dark);
    }

    .opcao-unidade.selecionada {
      background: var(--accent-soft);
      border-color: var(--accent);
    }

    .opcao-unidade__conteudo { display: block; }

    .opcao-unidade__titulo {
      display: block;
      font-size: 1.05rem;
      font-weight: 700;
    }

    .opcao-unidade__descricao {
      color: var(--muted);
      display: block;
      font-size: .82rem;
      margin-top: .25rem;
    }

    .arquivos {
      background: var(--surface-soft);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 1rem;
    }

    .arquivos[hidden] { display: none; }

    .arquivos legend {
      font-size: 1rem;
      font-weight: 700;
      padding: 0 .35rem;
    }

    .campo {
      border-top: 1px solid var(--line);
      margin-top: .75rem;
      padding-top: .75rem;
    }

    .campo:first-of-type { border-top: 0; margin-top: 0; padding-top: 0; }

    .campo label {
      display: block;
      font-weight: 600;
      margin-bottom: .25rem;
    }

    .campo input[type=file] {
      background: var(--surface);
      border: 1px solid #bdcccf;
      border-radius: 7px;
      color: var(--ink);
      max-width: 100%;
      padding: .45rem;
      width: 100%;
    }

    .campo input[type=file]:focus {
      border-color: var(--accent);
      outline: 3px solid rgba(11, 115, 112, .2);
    }

    .campo__ajuda { display: block; margin-top: .2rem; }

    .acoes {
      align-items: center;
      border-top: 1px solid var(--line);
      display: flex;
      gap: 1rem;
      justify-content: space-between;
      margin-top: 2rem;
      padding-top: 1.25rem;
    }

    button {
      background: var(--accent);
      border: 0;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font: inherit;
      font-weight: 700;
      padding: .75rem 1.1rem;
    }

    button:hover:not(:disabled) { background: var(--accent-dark); }

    button:focus-visible { outline: 3px solid rgba(11, 115, 112, .3); outline-offset: 2px; }

    button:disabled { cursor: not-allowed; opacity: .48; }

    .status-form { margin: 0; }

    .erro {
      background: var(--danger-soft);
      border: 1px solid #f2b8b8;
      border-radius: 8px;
      color: var(--danger);
      margin: 0 0 1.25rem;
      padding: .8rem 1rem;
    }

    @media (max-width: 600px) {
      .cabecalho { align-items: flex-start; flex-direction: column; }
      .opcoes-unidade { grid-template-columns: 1fr; }
      .acoes { align-items: stretch; flex-direction: column; }
      button { width: 100%; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
    }
  </style>
</head>
<body>
  <main class="page">
    <header class="cabecalho">
      <img class="logo" src="{{ url_for('logo_topo') }}" alt="Logo Grupo Flexível">
      <div>
        <p class="eyebrow">Conferência fiscal</p>
        <h1>Conferência de Notas Fiscais</h1>
      </div>
    </header>

    <section class="painel">
      {% if erro %}<p class="erro" role="alert">{{ erro }}</p>{% endif %}
      <form id="form-conferencia" method="post" action="/process" enctype="multipart/form-data">
        <fieldset class="etapa">
          <legend class="etapa__titulo">1. Escolha a unidade</legend>
          <p class="etapa__ajuda" id="unidade-ajuda">Os campos de anexos serão liberados após a escolha.</p>
          <div class="opcoes-unidade" role="radiogroup" aria-describedby="unidade-ajuda">
            <label class="opcao-unidade" for="unidade-matriz">
              <input id="unidade-matriz" type="radio" name="unidade" value="Matriz" required aria-controls="uploads-Matriz">
              <span class="opcao-unidade__conteudo">
                <span class="opcao-unidade__titulo">Matriz</span>
                <span class="opcao-unidade__descricao">Arquivos SAT, CT-e e serviços</span>
              </span>
            </label>
            <label class="opcao-unidade" for="unidade-filial">
              <input id="unidade-filial" type="radio" name="unidade" value="Filial" required aria-controls="uploads-Filial">
              <span class="opcao-unidade__conteudo">
                <span class="opcao-unidade__titulo">Filial</span>
                <span class="opcao-unidade__descricao">Arquivos Qive, CT-e e serviços</span>
              </span>
            </label>
          </div>
        </fieldset>

        <section class="etapa" id="etapa-arquivos" aria-labelledby="arquivos-titulo" hidden>
          <h2 class="etapa__titulo" id="arquivos-titulo">2. Anexe os arquivos</h2>
          <p class="etapa__ajuda">Envie os arquivos disponíveis para a unidade selecionada.</p>
    {% for unidade, campos in arquivos_por_unidade.items() %}
    <fieldset class="arquivos" id="uploads-{{ unidade }}" data-unidade="{{ unidade }}" hidden disabled>
      <legend>{{ unidade }}</legend>
      {% for chave, titulo in campos %}
      <div class="campo">
        <label for="{{ unidade }}__{{ chave }}">{{ titulo }}</label>
        <input id="{{ unidade }}__{{ chave }}" type="file" name="{{ unidade }}__{{ chave }}" data-chave="{{ chave }}" accept=".xlsx,.xls,.html,.htm">
        <span class="campo__ajuda">Arquivo opcional; os requisitos mínimos serão verificados antes do envio.</span>
      </div>
      {% endfor %}
    </fieldset>
    {% endfor %}
        </section>

        <div class="acoes">
          <p class="status-form" id="status-form" role="status" aria-live="polite">Selecione a unidade para começar.</p>
          <button id="processar" type="submit" disabled>Processar e baixar relatório</button>
        </div>
      </form>
    </section>
  </main>

  <script>
    (() => {
      const form = document.getElementById("form-conferencia");
      const unidadeInputs = Array.from(document.querySelectorAll('input[name="unidade"]'));
      const etapaArquivos = document.getElementById("etapa-arquivos");
      const secoesArquivos = Array.from(document.querySelectorAll("[data-unidade]"));
      const botaoProcessar = document.getElementById("processar");
      const statusForm = document.getElementById("status-form");

      function unidadeSelecionada() {
        const selecionada = unidadeInputs.find((input) => input.checked);
        return selecionada ? selecionada.value : "";
      }

      function limparArquivos() {
        document.querySelectorAll('input[type="file"]').forEach((input) => {
          input.value = "";
        });
      }

      function arquivosSelecionados(unidade) {
        const secao = document.getElementById(`uploads-${unidade}`);
        return secao
          ? Array.from(secao.querySelectorAll('input[type="file"]')).filter((input) => input.files.length > 0)
          : [];
      }

      function atualizarBotao(unidade) {
        const arquivos = arquivosSelecionados(unidade);
        const temErp = arquivos.some((input) => ["arquivo_notas_entrada", "arquivo_devolucoes"].includes(input.dataset.chave));
        const temDocumento = arquivos.some((input) => ["arquivo_anterior", "arquivo_sat", "arquivo_qive_entrada", "arquivo_cte", "arquivo_servico"].includes(input.dataset.chave));
        const requisitosAtendidos = Boolean(unidade && temErp && temDocumento);

        botaoProcessar.disabled = !requisitosAtendidos;
        if (!unidade) {
          statusForm.textContent = "Selecione a unidade para começar.";
        } else if (!requisitosAtendidos) {
          statusForm.textContent = "Anexe ao menos um arquivo do ERP e um documento ou análise anterior.";
        } else {
          statusForm.textContent = "Arquivos mínimos selecionados. O processamento está disponível.";
        }
      }

      function atualizarFormulario() {
        const unidade = unidadeSelecionada();
        etapaArquivos.hidden = !unidade;
        unidadeInputs.forEach((input) => {
          const opcao = input.closest(".opcao-unidade");
          if (opcao) opcao.classList.toggle("selecionada", input.checked);
        });
        secoesArquivos.forEach((secao) => {
          const ativa = secao.dataset.unidade === unidade;
          secao.hidden = !ativa;
          secao.disabled = !ativa;
          secao.setAttribute("aria-hidden", String(!ativa));
        });
        atualizarBotao(unidade);
      }

      unidadeInputs.forEach((input) => {
        input.addEventListener("change", () => {
          limparArquivos();
          atualizarFormulario();
        });
      });

      document.querySelectorAll('input[type="file"]').forEach((input) => {
        input.addEventListener("change", () => atualizarBotao(unidadeSelecionada()));
      });

      form.addEventListener("submit", () => {
        botaoProcessar.disabled = true;
      });

      atualizarFormulario();
    })();
  </script>
</body>
</html>
"""


app = Flask(__name__)


@app.get("/logo_topo.png")
def logo_topo():
    return send_from_directory(app.root_path, "logo_topo.png")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/")
def index():
    return render_template_string(
        FORMULARIO, arquivos_por_unidade=ARQUIVOS_POR_UNIDADE, erro=None
    )


@app.post("/process")
def processar():
    unidade = request.form.get("unidade", "")
    if unidade not in LAYOUTS:
        return render_template_string(
            FORMULARIO,
            arquivos_por_unidade=ARQUIVOS_POR_UNIDADE,
            erro="Selecione uma unidade válida.",
        ), 400

    diretorio_temporario = Path(tempfile.mkdtemp(prefix="conferencia_nf_"))
    try:
        arquivos = {}
        for chave, _ in ARQUIVOS_POR_UNIDADE[unidade]:
            arquivo = request.files.get(f"{unidade}__{chave}")
            if not arquivo or not arquivo.filename:
                continue

            nome_seguro = secure_filename(arquivo.filename)
            if not nome_seguro:
                return render_template_string(
                    FORMULARIO,
                    arquivos_por_unidade=ARQUIVOS_POR_UNIDADE,
                    erro=f"Nome de arquivo inválido para {chave}.",
                ), 400

            caminho = diretorio_temporario / f"{chave}_{nome_seguro}"
            arquivo.save(caminho)
            arquivos[chave] = str(caminho)

        layout = LAYOUTS[unidade]()
        caminho_saida = OUTPUT_DIR / layout.arquivo_saida
        processar_conferencia(layout, arquivos, caminho_saida)
        return send_file(
            caminho_saida,
            as_attachment=True,
            download_name=layout.arquivo_saida,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except ValueError as erro:
        return render_template_string(
            FORMULARIO,
            arquivos_por_unidade=ARQUIVOS_POR_UNIDADE,
            erro=str(erro),
        ), 400
    except Exception:
        app.logger.exception("Falha ao processar conferência via HTTP")
        return render_template_string(
            FORMULARIO,
            arquivos_por_unidade=ARQUIVOS_POR_UNIDADE,
            erro="Ocorreu um erro durante o processamento. Consulte os logs do serviço.",
        ), 500
    finally:
        shutil.rmtree(diretorio_temporario, ignore_errors=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORTA_INTERNA)
