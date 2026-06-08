from sqlalchemy.orm import Session
from pydantic import BaseModel
import models


class ProdutoSchema(BaseModel):
    nome: str
    categoria: str
    quantidade: int
    estoque_minimo: int
    preco: float

    class Config:
        from_attributes = True


def listar_produtos(db: Session):
    return db.query(models.Produto).all()


def obter_produto(db: Session, produto_id: int):
    return db.query(models.Produto).filter(models.Produto.id == produto_id).first()


def criar_produto(db: Session, dados: ProdutoSchema):
    produto = models.Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def atualizar_produto(db: Session, produto_id: int, dados: ProdutoSchema):
    produto = obter_produto(db, produto_id)
    if not produto:
        return None
    for campo, valor in dados.model_dump().items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


def deletar_produto(db: Session, produto_id: int):
    produto = obter_produto(db, produto_id)
    if not produto:
        return False
    db.delete(produto)
    db.commit()
    return True


def resumo_dashboard(db: Session):
    produtos = db.query(models.Produto).all()

    total = len(produtos)
    criticos = [p for p in produtos if p.quantidade < p.estoque_minimo]
    baixos = [p for p in produtos if p.quantidade < p.estoque_minimo * 1.5]
    valor_total = sum(p.quantidade * p.preco for p in produtos)

    return {
        "total_produtos": total,
        "produtos_criticos": len(criticos),
        "produtos_estoque_baixo": len(baixos),
        "valor_total": round(valor_total, 2),
        "lista_criticos": [
            {
                "nome": p.nome,
                "categoria": p.categoria,
                "quantidade": p.quantidade,
                "estoque_minimo": p.estoque_minimo
            }
            for p in criticos
        ]
    }
