import chromadb  # type: ignore[reportMissingImports]

client = chromadb.PersistentClient(path="./chroma")

collection = client.get_or_create_collection(
    name="estoque",
    metadata={"hnsw:space": "cosine"}
)

SIMILARIDADE_MINIMA = 0.70

PALAVRAS_BLOQUEIO = [
    # Esportes
    "futebol", "brasileirao", "campeonato", "jogo", "gol",
    "time", "placar", "esporte", "olimpiadas", "nba", "formula",

    # Entretenimento
    "filme", "serie", "netflix", "youtube", "musica", "banda",
    "novela", "ator", "atriz", "cinema", "show", "concert",

    # Politica
    "politica", "presidente", "eleicao", "governo", "partido",
    "vereador", "senador", "congresso", "ministerio",

    # Clima e geografia
    "clima", "tempo", "chuva", "temperatura", "previsao",
    "pais", "cidade", "viagem", "turismo",

    # Tecnologia geral
    "bitcoin", "cripto", "investimento", "bolsa", "acoes",
    "celular", "iphone", "computador", "videogame",

    # Relacionamentos e pessoal
    "namorada", "namorado", "amor", "briga", "familia",
    "amigo", "festa", "aniversario",

    # Academico
    "matematica", "historia", "geografia", "ingles", "prova",
    "vestibular", "enem", "faculdade",

    # Culinaria (fora do contexto de produto)
    "receita", "cozinhar", "tempero", "bolo", "sobremesa",
]

def classificar_tema(pergunta: str) -> bool:
    pergunta_lower = pergunta.lower()
    for palavra in PALAVRAS_BLOQUEIO:
        if palavra in pergunta_lower:
            return False
    return True

def buscar_contexto(pergunta: str) -> tuple:
    resultado = collection.query(
        query_texts=[pergunta],
        n_results=3,
        include=["documents", "distances"]
    )
    documentos = resultado["documents"][0] if resultado["documents"] else []
    distancias = resultado["distances"][0] if resultado["distances"] else [1.0]
    similaridades = [1 - (d / 2) for d in distancias]
    melhor_similaridade = max(similaridades) if similaridades else 0.0
    if melhor_similaridade < SIMILARIDADE_MINIMA:
        return [], melhor_similaridade
    return documentos, melhor_similaridade

def indexar_produto(produto_id: int, texto: str):
    collection.upsert(ids=[str(produto_id)], documents=[texto])

def remover_produto(produto_id: int):
    collection.delete(ids=[str(produto_id)])