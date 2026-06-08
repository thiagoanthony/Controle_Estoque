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

```
React (localhost:5173)
       │
       ▼
FastAPI (localhost:8080)
       │
  ┌────┼────────┐
  ▼    ▼        ▼
SQLite ChromaDB Ollama
                  │
              Llama 3.2
```

### As 4 Camadas de Bloqueio

| Camada | Nome | Ação |
|--------|------|------|
| 1 | Classificador de tema | Bloqueia perguntas fora do domínio |
| 2 | Limiar de similaridade | Bloqueia se similaridade < 0.70 |
| 3 | Prompt de restrição | LLM instruído a não inventar |
| 4 | Validação da resposta | Detecta alucinações na resposta |

---

## Instalação

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com/download) instalado

### 1. Baixar os modelos

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 2. Instalar dependências do backend

```bash
pip install -r requirements.txt
```

### 3. Popular o banco de dados

```bash
python seed_chroma.py
```

### 4. Instalar dependências do frontend

```bash
cd frontend
npm install
npm install axios
```

---

## Como rodar

### Opção 1 — Script automático (recomendado)

Salve o arquivo `iniciar_estoque.ps1` na pasta raiz do projeto e execute no PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\iniciar_estoque.ps1
```

O script inicia o Ollama, o backend e o frontend automaticamente e abre o navegador.

### Opção 2 — Manual (3 terminais)

**Terminal 1 — Ollama:**
```bash
ollama serve
```

**Terminal 2 — Backend:**
```bash
python -m uvicorn main:app --port 8080
```

**Terminal 3 — Frontend:**
```bash
cd frontend
npm run dev
```

Acesse: [http://localhost:5173](http://localhost:5173)

---

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /dashboard | Métricas do estoque |
| POST | /chat | Chat com o LLM |
| GET | /produtos | Listar produtos |
| POST | /produtos | Criar produto |
| PUT | /produtos/{id} | Atualizar produto |
| DELETE | /produtos/{id} | Remover produto |

Documentação interativa: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## Estrutura do projeto

```
controle_estoque/
├── main.py            # API FastAPI + endpoints
├── rag.py             # ChromaDB + 4 camadas de bloqueio
├── ai.py              # Integração com Ollama/Llama 3.2
├── crud.py            # Operações no SQLite
├── database.py        # Configuração do SQLAlchemy
├── models.py          # Modelo da tabela produtos
├── seed_chroma.py     # Popula SQLite + ChromaDB
├── requirements.txt
├── iniciar_estoque.ps1
└── frontend/
    └── src/
        ├── App.jsx
        ├── Dashboard.jsx
        ├── Chat.jsx
        └── api.js
```

---

## Exemplos de uso

```
Você: Quantas Coca-Cola 2L existem?
IA:   Existem 8 unidades de Coca-Cola 2L em estoque.

Você: Quais produtos precisam de reposição?
IA:   Monster Mango (4 un, mín: 20), Coca-Cola 2L (8 un, mín: 50)...

Você: Quem ganhou o Brasileirão?
IA:   Essa pergunta está fora do tema de estoque. [Bloqueado - Camada 1]
```

---


