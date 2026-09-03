const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

class Element {
  constructor(id, dataset = {}) {
    this.id = id;
    this.dataset = dataset;
    this.checked = false;
    this.hidden = false;
    this.disabled = false;
    this._value = "";
    this.files = [];
    this.listeners = {};
    this.children = [];
    this.parent = null;
    this.textContent = "";
    this.attributes = {};
    this.classList = {
      values: new Set(),
      toggle: (name, force) => {
        const enabled = force === undefined ? !this.classList.values.has(name) : force;
        if (enabled) this.classList.values.add(name);
        else this.classList.values.delete(name);
      },
    };
  }

  addEventListener(event, callback) { this.listeners[event] = callback; }
  get value() { return this._value; }
  set value(value) {
    this._value = value;
    if (value === "") this.files = [];
  }
  setAttribute(name, value) { this.attributes[name] = value; }
  closest(selector) { return selector === ".opcao-unidade" ? this.parent : null; }
  querySelectorAll(selector) {
    return selector === 'input[type="file"]' ? this.children : [];
  }
  fire(event) { this.listeners[event](); }
}

const form = new Element("form-conferencia");
const etapaArquivos = new Element("etapa-arquivos");
const botao = new Element("processar");
const status = new Element("status-form");
const matrizLabel = new Element("matriz-label");
const filialLabel = new Element("filial-label");
const matrizRadio = new Element("unidade-matriz");
const filialRadio = new Element("unidade-filial");
matrizRadio.value = "Matriz";
filialRadio.value = "Filial";
matrizRadio.parent = matrizLabel;
filialRadio.parent = filialLabel;
const matriz = new Element("uploads-Matriz", {unidade: "Matriz"});
const filial = new Element("uploads-Filial", {unidade: "Filial"});
const matrizErp = new Element("Matriz__arquivo_notas_entrada", {chave: "arquivo_notas_entrada"});
const matrizSat = new Element("Matriz__arquivo_sat", {chave: "arquivo_sat"});
const filialErp = new Element("Filial__arquivo_notas_entrada", {chave: "arquivo_notas_entrada"});
const filialQive = new Element("Filial__arquivo_qive_entrada", {chave: "arquivo_qive_entrada"});
matriz.children = [matrizErp, matrizSat];
filial.children = [filialErp, filialQive];
const allFiles = matriz.children.concat(filial.children);
const elements = new Map([
  ["form-conferencia", form], ["etapa-arquivos", etapaArquivos], ["processar", botao],
  ["status-form", status], ["unidade-matriz", matrizRadio], ["unidade-filial", filialRadio],
  ["uploads-Matriz", matriz], ["uploads-Filial", filial],
]);

globalThis.document = {
  getElementById: (id) => elements.get(id),
  querySelectorAll: (selector) => {
    if (selector === 'input[name="unidade"]') return [matrizRadio, filialRadio];
    if (selector === "[data-unidade]") return [matriz, filial];
    if (selector === 'input[type="file"]') return allFiles;
    return [];
  },
};

const source = fs.readFileSync(path.join(__dirname, "..", "webapp.py"), "utf8");
const script = source.match(/<script>\s*([\s\S]*?)\s*<\/script>/)[1];
vm.runInThisContext(script);

const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};

assert(etapaArquivos.hidden, "a etapa de arquivos deve iniciar oculta");
assert(matriz.hidden && matriz.disabled && filial.hidden && filial.disabled, "uploads devem iniciar bloqueados");
assert(botao.disabled, "o botao deve iniciar bloqueado");

matrizRadio.checked = true;
matrizRadio.fire("change");
assert(!matriz.hidden && !matriz.disabled, "uploads da Matriz devem ser liberados");
assert(filial.hidden && filial.disabled, "uploads da Filial devem permanecer bloqueados");
assert(matrizLabel.classList.values.has("selecionada"), "Matriz deve ter indicacao visual");

matrizErp.files = [{name: "erp.xlsx"}];
matrizSat.files = [{name: "sat.xlsx"}];
matrizSat.fire("change");
assert(!botao.disabled, "o botao deve liberar os requisitos da Matriz");

matrizRadio.checked = false;
filialRadio.checked = true;
filialRadio.fire("change");
assert(matriz.hidden && matriz.disabled, "uploads da Matriz devem ser ocultados na troca");
assert(!filial.hidden && !filial.disabled, "uploads da Filial devem ser liberados na troca");
assert(!matrizLabel.classList.values.has("selecionada"), "Matriz nao deve permanecer selecionada");
assert(filialLabel.classList.values.has("selecionada"), "Filial deve ter indicacao visual");
assert(matrizErp.files.length === 0 && matrizSat.files.length === 0, "a troca deve limpar arquivos");
assert(botao.disabled, "o botao deve ser bloqueado apos a troca");

console.log("frontend-flow: OK");
