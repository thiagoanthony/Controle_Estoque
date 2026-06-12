from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import SessionLocal, engine
import models
import crud
from rag import classificar_tema, buscar_contexto, indexar_produto, remover_produto
from ai import perguntar_llm

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EstoqueIA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Palavras que indicam pergunta sobre totais gerais do estoque
PALAVRAS_TOTAL = [
    "quantos produtos", "total de produtos", "quantos itens",
    "total do estoque", "quantos tem no estoque", "quantidade total",
    "quantos produtos tem", "total de itens", "quantos sao",
    "quantos estao", "valor total", "valor do estoque",
    "resumo do estoque", "relatorio do estoque", "quantos criticos",
    "produtos criticos", "estoque critico",
]

class PerguntaRequest(BaseModel):
    pergunta: str


@app.post("/chat")
def chat(body: PerguntaRequest):
    pergunta = body.pergunta.strip()

    if not pergunta:
        raise HTTPException(status_code=400, detail="Pergunta nao pode ser vazia.")

    db = SessionLocal()
    try:
        # Salva mensagem do usuario
        db.add(models.MensagemChat(role="user", texto=pergunta))
        db.commit()

        # ── Rota direta: perguntas sobre totais gerais ────────────────────────
        pergunta_lower = pergunta.lower()
        if any(p in pergunta_lower for p in PALAVRAS_TOTAL):
            resumo = crud.resumo_dashboard(db)
            criticos = resumo["lista_criticos"]
            nomes_criticos = ", ".join([c["nome"] for c in criticos]) if criticos else "nenhum"

            resposta_texto = (
                f"O estoque possui {resumo['total_produtos']} produtos cadastrados no total. "
                f"Desses, {resumo['produtos_criticos']} estao abaixo do estoque minimo: {nomes_criticos}. "
                f"O valor total em estoque e R$ {resumo['valor_total']:,.2f}."
            )
            db.add(models.MensagemChat(role="ai", texto=resposta_texto, bloqueado=False))
            db.commit()
            return {
                "resposta": resposta_texto,
                "bloqueado": False,
                "camada_bloqueio": None,
                "similaridade": None
            }

        # ── Camada 1: Classificador de tema ───────────────────────────────────
        if not classificar_tema(pergunta):
            resposta_texto = ("Essa pergunta esta fora do tema de estoque. "
                              "So posso responder sobre produtos, quantidades, "
                              "categorias e relatorios de estoque.")
            db.add(models.MensagemChat(role="ai", texto=resposta_texto,
                                       bloqueado=True, camada=1))
            db.commit()
            return {"resposta": resposta_texto, "bloqueado": True,
                    "camada_bloqueio": 1, "similaridade": None}

        # ── Camada 2: Busca no banco vetorial ─────────────────────────────────
        documentos, similaridade = buscar_contexto(pergunta)
        if not documentos:
            resposta_texto = ("Nao encontrei essa informacao na base disponivel. "
                              f"(similaridade maxima: {similaridade:.2f})")
            db.add(models.MensagemChat(role="ai", texto=resposta_texto,
                                       bloqueado=True, camada=2,
                                       similaridade=round(similaridade, 4)))
            db.commit()
            return {"resposta": resposta_texto, "bloqueado": True,
                    "camada_bloqueio": 2, "similaridade": round(similaridade, 4)}

        # ── Camadas 3 e 4: LLM ────────────────────────────────────────────────
        resultado = perguntar_llm(pergunta, documentos)
        db.add(models.MensagemChat(
            role="ai",
            texto=resultado["resposta"],
            bloqueado=not resultado["valida"],
            camada=4 if not resultado["valida"] else None,
            similaridade=round(similaridade, 4)))
        db.commit()

        return {
            "resposta": resultado["resposta"],
            "bloqueado": not resultado["valida"],
            "camada_bloqueio": 4 if not resultado["valida"] else None,
            "similaridade": round(similaridade, 4)
        }
    finally:
        db.close()


@app.get("/historico")
def historico(limite: int = 100):
    db = SessionLocal()
    try:
        msgs = (db.query(models.MensagemChat)
                .order_by(models.MensagemChat.id.desc())
                .limit(limite).all())
        msgs.reverse()
        return [
            {
                "id": m.id,
                "role": m.role,
                "texto": m.texto,
                "bloqueado": m.bloqueado,
                "camada": m.camada,
                "similaridade": m.similaridade,
                "criado_em": m.criado_em.strftime("%d/%m/%Y %H:%M") if m.criado_em else None
            }
            for m in msgs
        ]
    finally:
        db.close()


@app.delete("/historico")
def limpar_historico():
    db = SessionLocal()
    try:
        db.query(models.MensagemChat).delete()
        db.commit()
        return {"mensagem": "Historico limpo com sucesso."}
    finally:
        db.close()


@app.get("/produtos")
def listar_produtos():
    db = SessionLocal()
    try:
        return crud.listar_produtos(db)
    finally:
        db.close()


@app.get("/produtos/{produto_id}")
def obter_produto(produto_id: int):
    db = SessionLocal()
    try:
        produto = crud.obter_produto(db, produto_id)
        if not produto:
            raise HTTPException(status_code=404, detail="Produto nao encontrado.")
        return produto
    finally:
        db.close()


@app.post("/produtos")
def criar_produto(produto: crud.ProdutoSchema):
    db = SessionLocal()
    try:
        novo = crud.criar_produto(db, produto)
        texto = (f"Produto: {novo.nome}. Categoria: {novo.categoria}. "
                 f"Quantidade: {novo.quantidade} unidades. "
                 f"Estoque minimo: {novo.estoque_minimo}. "
                 f"Preco: R$ {novo.preco:.2f}.")
        indexar_produto(novo.id, texto)
        return novo
    finally:
        db.close()


@app.put("/produtos/{produto_id}")
def atualizar_produto(produto_id: int, produto: crud.ProdutoSchema):
    db = SessionLocal()
    try:
        atualizado = crud.atualizar_produto(db, produto_id, produto)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Produto nao encontrado.")
        texto = (f"Produto: {atualizado.nome}. Categoria: {atualizado.categoria}. "
                 f"Quantidade: {atualizado.quantidade} unidades. "
                 f"Estoque minimo: {atualizado.estoque_minimo}. "
                 f"Preco: R$ {atualizado.preco:.2f}.")
        indexar_produto(atualizado.id, texto)
        return atualizado
    finally:
        db.close()


@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int):
    db = SessionLocal()
    try:
        ok = crud.deletar_produto(db, produto_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Produto nao encontrado.")
        remover_produto(produto_id)
        return {"mensagem": "Produto removido com sucesso."}
    finally:
        db.close()


@app.get("/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        return crud.resumo_dashboard(db)
    finally:
        db.close()