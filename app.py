import os
import re
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai import types

load_dotenv()  # lê a chave do arquivo .env

app = Flask(__name__, static_folder="static", static_url_path="/static")

cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
 
MODELO = "gemini-3.5-flash-lite"
MAX_QUESTOES = 20
PESOS = {"correta": 1.0, "parcial": 0.5, "incorreta": 0.0}  # valor de cada resposta na nota
MARCA = re.compile(r"\[\[\s*(correta|parcial|incorreta)\s*\]\]", re.I)
sessoes = {}  # id da sessão -> estado do teste
 
 
def prompt_sistema(tema):
    return f"""
Você é um tutor acadêmico especialista no tema: '{tema}'.
Sua missão é testar o conhecimento do aluno de forma interativa.
 
Regras de comportamento:
1. Faça APENAS UMA pergunta por vez.
2. Aguarde a resposta do aluno.
3. Quando o aluno responder:
   - Diga se a resposta está Correta, Parcialmente Correta ou Incorreta.
   - Forneça uma breve explicação do motivo.
   - Em seguida, faça a PRÓXIMA pergunta.
4. Mantenha as explicações diretas e objetivas (máximo de 3 a 4 parágrafos por resposta).
5. No FINAL de cada correção (nunca na primeira pergunta), escreva em uma linha separada
   exatamente uma destas marcas: [[Correta]], [[Parcial]] ou [[Incorreta]].
"""
 
 
@app.get("/")
def index():
    return send_from_directory("static", "index.html")
 
 
@app.post("/api/iniciar")
def iniciar():
    tema = (request.json.get("tema") or "").strip()
    if not tema:
        return jsonify(erro="Digite um tema para começar."), 400
 
    sessao = uuid.uuid4().hex
    sessoes[sessao] = {"tema": tema, "etapa": "quantidade"}
    texto = f"Legal! Vamos estudar **{tema}**. Quantas questões você quer responder? (de 1 a {MAX_QUESTOES})"
    return jsonify(sessao=sessao, texto=texto, etapa="quantidade", finalizado=False)
 
 
@app.post("/api/responder")
def responder():
    dados = request.json
    sessao = dados.get("sessao")
    estado = sessoes.get(sessao)
    resposta = (dados.get("resposta") or "").strip()
    if not estado:
        return jsonify(erro="Sessão não encontrada. Clique em Novo Chat."), 404
    if not resposta:
        return jsonify(erro="Digite sua resposta."), 400
 
    # Etapa 1: o usuário informa quantas questões quer
    if estado["etapa"] == "quantidade":
        numero = re.search(r"\d+", resposta)
        total = int(numero.group()) if numero else 0
        if not 1 <= total <= MAX_QUESTOES:
            return jsonify(texto=f"Digite um número de 1 a {MAX_QUESTOES}.", etapa="quantidade", finalizado=False)
        try:
            chat = cliente.chats.create(
                model=MODELO,
                config=types.GenerateContentConfig(system_instruction=prompt_sistema(estado["tema"])),
            )
            primeira = chat.send_message("Gere a pergunta 1.")
        except Exception as e:
            return jsonify(erro=f"Falha ao falar com o Gemini: {e}"), 502
        estado.update(
            etapa="teste", chat=chat, total=total, respondidas=0,
            contagem={"correta": 0, "parcial": 0, "incorreta": 0},
        )
        return jsonify(texto=primeira.text, etapa="teste", rodada=1, total=total, finalizado=False)
 
    # Etapa 2: perguntas e respostas
    n = estado["respondidas"] + 1
    total = estado["total"]
    fim = n >= total
    if fim:
        mensagem = (
            f"Resposta {n}: {resposta}. Teste finalizado. Corrija esta última resposta, "
            "NÃO faça nova pergunta e feche com 2 ou 3 frases sobre o desempenho geral do aluno."
        )
    else:
        mensagem = f"Resposta {n}: {resposta}"
    try:
        retorno = estado["chat"].send_message(mensagem)
    except Exception as e:
        return jsonify(erro=f"Falha ao falar com o Gemini: {e}"), 502
 
    texto = retorno.text
    marca = MARCA.search(texto)
    if marca:
        estado["contagem"][marca.group(1).lower()] += 1
    texto = MARCA.sub("", texto).strip()
    estado["respondidas"] = n
 
    resultado = {"etapa": "teste", "rodada": min(n + 1, total), "total": total, "finalizado": fim}
    if fim:
        c = estado["contagem"]
        nota = round(sum(PESOS[k] * v for k, v in c.items()) / total * 10, 1)
        texto += (
            f"\n\n**Nota final: {str(nota).replace('.', ',')}/10** "
            f"({c['correta']} corretas, {c['parcial']} parciais, {c['incorreta']} incorretas)"
        )
        resultado["nota"] = nota
        del sessoes[sessao]
    resultado["texto"] = texto
    return jsonify(resultado)
 
 
if __name__ == "__main__":
    app.run(debug=True)
 