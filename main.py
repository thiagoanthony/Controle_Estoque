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


class PerguntaRequest(BaseModel):
    pergunta: str


# ── /chat — com persistência do histórico ─────────────────────────────────────
@app.post("/chat")
def chat(body: PerguntaRequest):
    pergunta = body.pergunta.strip()
    if not pergunta:
        raise HTTPException(status_code=400, detail="Pergunta não pode ser vazia.")

    db = SessionLocal()
    try:
        # Salva mensagem do usuário
        db.add(models.MensagemChat(role="user", texto=pergunta))
        db.commit()

        # Camada 1
        if not classificar_tema(pergunta):
            resposta_texto = ("Essa pergunta está fora do tema de estoque. "
                              "Só posso responder sobre produtos, quantidades, "
                              "categorias e relatórios de estoque.")
            db.add(models.MensagemChat(
                role="ai", texto=resposta_texto,
                bloqueado=True, camada=1))
            db.commit()
            return {"resposta": resposta_texto, "bloqueado": True,
                    "camada_bloqueio": 1, "similaridade": None}

        # Camada 2
        documentos, similaridade = buscar_contexto(pergunta)
        if not documentos:
            resposta_texto = ("Não encontrei essa informação na base disponível. "
                              f"(similaridade máxima: {similaridade:.2f})")
            db.add(models.MensagemChat(
                role="ai", texto=resposta_texto,
                bloqueado=True, camada=2,
                similaridade=round(similaridade, 4)))
            db.commit()
            return {"resposta": resposta_texto, "bloqueado": True,
                    "camada_bloqueio": 2, "similaridade": round(similaridade, 4)}

        # Camadas 3 e 4
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


# ── /historico — retorna o histórico salvo ───────────────────────────────────
@app.get("/historico")
def historico(limite: int = 50):
    db = SessionLocal()
    try:
        msgs = (db.query(models.MensagemChat)
                .order_by(models.MensagemChat.id.desc())
                .limit(limite)
                .all())
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


# ── /historico — limpar histórico ────────────────────────────────────────────
@app.delete("/historico")
def limpar_historico():
    db = SessionLocal()
    try:
        db.query(models.MensagemChat).delete()
        db.commit()
        return {"mensagem": "Histórico limpo com sucesso."}
    finally:
        db.close()


# ── CRUD de produtos ──────────────────────────────────────────────────────────
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
            raise HTTPException(status_code=404, detail="Produto não encontrado.")
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
                 f"Estoque mínimo: {novo.estoque_minimo}. "
                 f"Preço: R$ {novo.preco:.2f}.")
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
            raise HTTPException(status_code=404, detail="Produto não encontrado.")
        texto = (f"Produto: {atualizado.nome}. Categoria: {atualizado.categoria}. "
                 f"Quantidade: {atualizado.quantidade} unidades. "
                 f"Estoque mínimo: {atualizado.estoque_minimo}. "
                 f"Preço: R$ {atualizado.preco:.2f}.")
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
            raise HTTPException(status_code=404, detail="Produto não encontrado.")
        remover_produto(produto_id)
        return {"mensagem": "Produto removido com sucesso."}
    finally:
        db.close()


# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.get("/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        return crud.resumo_dashboard(db)
    finally:
        db.close()
