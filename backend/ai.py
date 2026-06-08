import ollama

# ─── Camada 3: prompt de restrição ────────────────────────────────────────────
SYSTEM_PROMPT = """
Você é um assistente especializado exclusivamente no controle de estoque desta empresa.

Contexto disponível:
{contexto}

Regras obrigatórias:
- Responda SOMENTE com base no contexto acima.
- Se a resposta não estiver no contexto, diga exatamente: "Não encontrei essa informação na base disponível."
- Não invente informações, quantidades ou preços.
- Não responda perguntas fora do tema de estoque.
- Seja objetivo e direto.
"""

# ─── Camada 4: termos que indicam resposta inválida ──────────────────────────
TERMOS_ALUCINACAO = [
    "como assistente de ia",
    "como um assistente",
    "não tenho acesso",
    "não posso acessar",
    "meu conhecimento",
    "minha base de treinamento",
    "internet",
    "pesquisa",
    "não fui treinado",
]


def validar_resposta(resposta: str, contexto: list[str]) -> tuple[bool, str]:
    """
    Camada 4 — Validação da resposta gerada pelo LLM.
    Retorna (valida, motivo_da_invalidade).
    """
    if not resposta or len(resposta.strip()) < 5:
        return False, "resposta_vazia"

    resposta_lower = resposta.lower()

    for termo in TERMOS_ALUCINACAO:
        if termo in resposta_lower:
            return False, f"possivel_alucinacao: '{termo}'"

    if not contexto and "não encontrei" not in resposta_lower:
        return False, "resposta_sem_contexto"

    return True, "ok"


def perguntar_llm(pergunta: str, contexto: list[str]) -> dict:
    """
    Envia a pergunta ao LLM com o contexto recuperado pelo RAG.
    Aplica Camadas 3 (prompt de restrição) e 4 (validação da resposta).
    Retorna dicionário com 'resposta', 'valida' e 'similaridade_usada'.
    """
    contexto_texto = "\n\n".join(contexto) if contexto else "(nenhum contexto encontrado)"

    resposta_raw = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(contexto=contexto_texto)
            },
            {
                "role": "user",
                "content": pergunta
            }
        ]
    )

    texto = resposta_raw["message"]["content"]

    # Camada 4 — valida a resposta antes de retornar
    valida, motivo = validar_resposta(texto, contexto)

    if not valida:
        return {
            "resposta": "Não encontrei essa informação na base disponível.",
            "valida": False,
            "motivo_bloqueio": motivo
        }

    return {
        "resposta": texto,
        "valida": True,
        "motivo_bloqueio": None
    }
