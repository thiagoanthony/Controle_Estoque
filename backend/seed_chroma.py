"""
seed_chroma.py — popula o ChromaDB com os produtos do SQLite.
Execute uma vez após criar o banco:
    python seed_chroma.py
"""
from database import SessionLocal, engine
import models
from rag import indexar_produto

models.Base.metadata.create_all(bind=engine)

PRODUTOS_INICIAIS = [
    {"nome": "Coca-Cola 2L",        "categoria": "Bebidas",   "quantidade": 8,   "estoque_minimo": 50,  "preco": 8.99},
    {"nome": "Monster Mango",       "categoria": "Bebidas",   "quantidade": 4,   "estoque_minimo": 20,  "preco": 12.50},
    {"nome": "Água Crystal 500ml",  "categoria": "Bebidas",   "quantidade": 11,  "estoque_minimo": 30,  "preco": 2.50},
    {"nome": "Red Bull 250ml",      "categoria": "Bebidas",   "quantidade": 6,   "estoque_minimo": 40,  "preco": 9.99},
    {"nome": "Suco Del Valle 1L",   "categoria": "Bebidas",   "quantidade": 85,  "estoque_minimo": 20,  "preco": 6.90},
    {"nome": "Guaraná Antarctica 2L","categoria": "Bebidas",  "quantidade": 120, "estoque_minimo": 30,  "preco": 7.50},
    {"nome": "Arroz Tio João 5kg",  "categoria": "Alimentos", "quantidade": 210, "estoque_minimo": 50,  "preco": 22.90},
    {"nome": "Feijão Carioca 1kg",  "categoria": "Alimentos", "quantidade": 180, "estoque_minimo": 40,  "preco": 8.50},
    {"nome": "Macarrão Barilla 500g","categoria": "Alimentos","quantidade": 95,  "estoque_minimo": 30,  "preco": 5.90},
    {"nome": "Detergente Ypê 500ml","categoria": "Limpeza",   "quantidade": 67,  "estoque_minimo": 25,  "preco": 3.20},
]

db = SessionLocal()

for dados in PRODUTOS_INICIAIS:
    existente = db.query(models.Produto).filter(
        models.Produto.nome == dados["nome"]
    ).first()

    if not existente:
        produto = models.Produto(**dados)
        db.add(produto)
        db.commit()
        db.refresh(produto)
        existente = produto

    texto = (
        f"Produto: {existente.nome}. Categoria: {existente.categoria}. "
        f"Quantidade em estoque: {existente.quantidade} unidades. "
        f"Estoque mínimo: {existente.estoque_minimo} unidades. "
        f"Preço unitário: R$ {existente.preco:.2f}."
    )
    indexar_produto(existente.id, texto)
    print(f"✓ Indexado: {existente.nome}")

db.close()
print("\nSeed concluído! ChromaDB populado com sucesso.")
