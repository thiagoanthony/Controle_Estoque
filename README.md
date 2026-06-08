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

## Arquitetura
React (localhost:5173)
│
▼
FastAPI (localhost:8001)
│
┌────┼────────┐
▼    ▼        ▼
SQLite ChromaDB Ollama
│
Llama 3.2

### As 4 Camadas de Bloqueio

| Camada | Nome | Ação |
|--------|------|------|
| 1 | Classificador de tema | Bloqueia perguntas fora do domínio |
| 2 | Limiar de similaridade | Bloqueia se similaridade < 0.70 |
| 3 | Prompt de restrição | LLM instruído a não inventar |
| 4 | Validação da resposta | Detecta alucinações na resposta |

---

## Como rodar

### 1. Instalar o Ollama
Acesse [ollama.com](https://ollama.com/download) e instale.

### 2. Baixar os modelos
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 3. Instalar dependências do backend
```bash
cd backend
pip install -r requirements.txt
```

### 4. Popular o banco de dados
```bash
python seed_chroma.py
```

### 5. Instalar dependências do frontend
```bash
cd frontend
npm install
```

### 6. Iniciar o projeto
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\iniciar_estoque.ps1
```

Acesse: http://localhost:5173

---

## Funcionalidades

- Dashboard com métricas em tempo real
- Chat IA com Llama 3.2 totalmente offline
- RAG com ChromaDB e nomic-embed-text
- 4 camadas de bloqueio contra perguntas fora do domínio
- Histórico do chat persistido no SQLite
- Alertas de produtos críticos

---

## Exemplos de uso
Você: Quantas Coca-Cola 2L existem?
IA:   Existem 8 unidades de Coca-Cola 2L em estoque.
Você: Quais produtos precisam de reposição?
IA:   Monster Mango (4 un, mín: 20), Coca-Cola 2L (8 un, mín: 50)...
Você: Quem ganhou o Brasileirão?
IA:   Essa pergunta está fora do tema de estoque. [Bloqueado - Camada 1]

---

## Disciplina

Inteligência Artificial · Ciência da Computação  
Centro Universitário do Triângulo — UNITRI  
Prof. Me. Jair de Oliveira Pereira Neto
Alunos. Thiago Anthony. Emerson Cardoso
