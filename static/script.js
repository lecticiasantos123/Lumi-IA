const principal = document.getElementById("principal");
const mensagens = document.getElementById("mensagens");
const form = document.getElementById("form");
const entrada = document.getElementById("entrada");
const botao = form.querySelector("button");
 
const PLACEHOLDER_INICIAL = "O que vamos estudar hoje?";
let sessao = null;
let finalizado = false;
let ocupado = false;
 
// Escapa HTML e converte **negrito** e parágrafos do Gemini
const escapar = (t) =>
  t.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
 
const formatar = (t) =>
  escapar(t)
    .split(/\n{2,}/)
    .map((p) => `<p>${p.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\n/g, "<br>")}</p>`)
    .join("");
 
// Transforma fórmulas em LaTeX ($...$) em matemática formatada
function renderizarMatematica(el) {
  if (!window.renderMathInElement) return;
  renderMathInElement(el, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true },
    ],
  });
}
 
function criarBolha(classe, html) {
  const bolha = document.createElement("div");
  bolha.className = `bolha ${classe}`;
  bolha.innerHTML = html;
  mensagens.appendChild(bolha);
  mensagens.scrollTop = mensagens.scrollHeight;
  return bolha;
}
 
async function chamarApi(url, corpo) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  const dados = await r.json();
  if (!r.ok) throw new Error(dados.erro || "Erro no servidor.");
  return dados;
}
 
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const texto = entrada.value.trim();
  if (!texto || ocupado || finalizado) return;
 
  const primeira = !sessao;
  ocupado = true;
  botao.disabled = true;
  entrada.value = "";
 
  if (primeira) {
    principal.className = "chat"; // muda para a tela de conversa
  }
 
  criarBolha("usuario", formatar(texto));
  const espera = criarBolha("ia", '<span class="digitando">...</span>');
 
  try {
    const dados = primeira
      ? await chamarApi("/api/iniciar", { tema: texto })
      : await chamarApi("/api/responder", { sessao, resposta: texto });
 
    sessao = dados.sessao || sessao;
    espera.innerHTML = formatar(dados.texto);
    renderizarMatematica(espera);
 
    if (dados.finalizado) {
      finalizado = true;
      entrada.disabled = true;
      entrada.placeholder = "Teste finalizado. Clique em Novo Chat para recomeçar.";
    } else if (dados.etapa === "quantidade") {
      entrada.placeholder = "Digite o número de questões (ex.: 5)";
    } else {
      entrada.placeholder = `Sua resposta (${dados.rodada}/${dados.total})`;
    }
  } catch (erro) {
    espera.classList.add("erro");
    espera.textContent = erro.message;
  } finally {
    ocupado = false;
    botao.disabled = false;
    if (!finalizado) entrada.focus();
    mensagens.scrollTop = mensagens.scrollHeight;
  }
});
 
function novoChat() {
  sessao = null;
  finalizado = false;
  mensagens.innerHTML = "";
  principal.className = "inicio";
  entrada.disabled = false;
  entrada.placeholder = PLACEHOLDER_INICIAL;
  entrada.focus();
}
 
document.getElementById("btn-novo").addEventListener("click", novoChat);
document.querySelectorAll("[data-em-breve]").forEach((b) =>
  b.addEventListener("click", () => alert("Esta função ainda vem por aí!"))
);
 