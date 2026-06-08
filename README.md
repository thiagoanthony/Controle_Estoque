# EstoqueIA

Sistema de gestão de estoque com Inteligência Artificial local — totalmente offline, sem custo de API.

> Llama 3.2 · ChromaDB · FastAPI · React · Ollama

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Frontend | React + Vite + Axios |
| Backend | FastAPI + Python |
| Banco de dados | SQLite + SQLAlchemy |
| Banco vetorial | ChromaDB |
| LLM local | Ollama + Llama 3.2 |
| Embeddings | nomic-embed-text |

---

## Como rodar

### 1. Baixar os modelos
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 2. Backend
```bash
pip install -r requirements.txt
python seed_chroma.py
python -m uvicorn main:app --port 8080
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:5173

---

## Funcionalidades

- Dashboard com métricas em tempo real
- Chat IA com Llama 3.2 totalmente offline
- RAG com ChromaDB e nomic-embed-text
- 4 camadas de bloqueio contra perguntas fora do domínio
- Histórico do chat persistido no SQLite

---

## Disciplina

Inteligência Artificial · Ciência da Computação  
Centro Universitário do Triângulo — UNITRI  
Prof. Me. Jair de Oliveira Pereira Neto
