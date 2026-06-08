$src = "C:\Users\Thiago\OneDrive\Documentos\controle_estoque\frontend\src"

# api.js
@'
import axios from "axios";
export default axios.create({ baseURL: "http://localhost:8000" });
'@ | Set-Content "$src\api.js" -Encoding UTF8

# App.jsx
@'
import { useState } from "react";
import Dashboard from "./Dashboard";
import Chat from "./Chat";

export default function App() {
  const [aba, setAba] = useState("dashboard");
  return (
    <div style={{ minHeight: "100vh", background: "#f5f5f5", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ background: "#fff", borderBottom: "1px solid #e0e0e0", display: "flex", alignItems: "center", padding: "0 1.5rem", height: 56 }}>
        <span style={{ fontWeight: 700, fontSize: 16, color: "#1a73e8", marginRight: 32 }}>EstoqueIA</span>
        {["dashboard", "chat"].map(a => (
          <button key={a} onClick={() => setAba(a)}
            style={{
              background: "none", border: "none", padding: "0 16px", height: 56,
              fontSize: 14, cursor: "pointer", fontWeight: aba === a ? 600 : 400,
              color: aba === a ? "#1a73e8" : "#555",
              borderBottom: aba === a ? "2px solid #1a73e8" : "2px solid transparent"
            }}>
            {a === "dashboard" ? "Dashboard" : "Chat IA"}
          </button>
        ))}
        <span style={{ marginLeft: "auto", fontSize: 12, color: "#999" }}>Llama 3.2 · offline</span>
      </div>
      {aba === "dashboard" ? <Dashboard /> : <Chat />}
    </div>
  );
}
'@ | Set-Content "$src\App.jsx" -Encoding UTF8

# Dashboard.jsx
@'
import { useEffect, useState } from "react";
import api from "./api";

export default function Dashboard() {
  const [dados, setDados] = useState(null);
  useEffect(() => { api.get("/dashboard").then(r => setDados(r.data)); }, []);
  if (!dados) return <p style={{ padding: "2rem" }}>Carregando...</p>;
  return (
    <div style={{ padding: "1.5rem" }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 24 }}>
        <Card label="Total de produtos" value={dados.total_produtos} cor="#1a73e8" />
        <Card label="Produtos criticos" value={dados.produtos_criticos} cor="#d93025" />
        <Card label="Estoque baixo" value={dados.produtos_estoque_baixo} cor="#f9ab00" />
        <Card label="Valor total" value={`R$ ${dados.valor_total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`} cor="#1e8e3e" />
      </div>
      <div style={{ background: "#fff", borderRadius: 8, border: "1px solid #e0e0e0", padding: "1.25rem" }}>
        <h3 style={{ margin: "0 0 1rem", fontSize: 14, color: "#333" }}>Produtos criticos</h3>
        {dados.lista_criticos.length === 0 && <p style={{ color: "#888", fontSize: 13 }}>Nenhum produto critico.</p>}
        {dados.lista_criticos.map((p, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid #f0f0f0" }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 500 }}>{p.nome}</div>
              <div style={{ fontSize: 12, color: "#888" }}>{p.categoria} - min: {p.estoque_minimo} un</div>
            </div>
            <span style={{ background: "#fce8e6", color: "#c5221f", fontSize: 12, padding: "3px 10px", borderRadius: 20, fontWeight: 500 }}>
              {p.quantidade} un
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Card({ label, value, cor }) {
  return (
    <div style={{ background: "#f8f9fa", borderRadius: 8, padding: "1rem", borderLeft: `4px solid ${cor}` }}>
      <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 600, color: "#111" }}>{value}</div>
    </div>
  );
}
'@ | Set-Content "$src\Dashboard.jsx" -Encoding UTF8

# Chat.jsx
@'
import { useState } from "react";
import api from "./api";

const SUGESTOES = [
  "Quantas Coca-Cola 2L existem?",
  "Quais produtos precisam de reposicao?",
  "Qual o preco do Arroz Tio Joao?",
  "Quem ganhou o Brasileirao?",
];

export default function Chat() {
  const [msg, setMsg] = useState("");
  const [historico, setHistorico] = useState([
    { role: "ai", texto: "Ola! Sou seu assistente de estoque. Pergunte sobre produtos, quantidades ou relatorios." }
  ]);
  const [carregando, setCarregando] = useState(false);

  async function enviar(pergunta) {
    const texto = pergunta || msg.trim();
    if (!texto) return;
    setHistorico(h => [...h, { role: "user", texto }]);
    setMsg("");
    setCarregando(true);
    try {
      const r = await api.post("/chat", { pergunta: texto });
      const d = r.data;
      setHistorico(h => [...h, {
        role: "ai", texto: d.resposta,
        bloqueado: d.bloqueado, camada: d.camada_bloqueio, similaridade: d.similaridade
      }]);
    } catch {
      setHistorico(h => [...h, { role: "ai", texto: "Erro ao conectar com o servidor.", bloqueado: true }]);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 60px)", padding: "1.5rem" }}>
      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 12, marginBottom: 12 }}>
        {historico.map((m, i) => (
          <div key={i} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", maxWidth: "75%" }}>
            <div style={{ fontSize: 11, color: "#999", marginBottom: 3, textAlign: m.role === "user" ? "right" : "left" }}>
              {m.role === "user" ? "Voce" : "Assistente IA - Llama 3.2"}
            </div>
            <div style={{
              padding: "10px 14px", borderRadius: 12, fontSize: 13, lineHeight: 1.6,
              background: m.role === "user" ? "#e8f0fe" : "#fff",
              border: "1px solid", borderColor: m.role === "user" ? "#c5d8fb" : m.bloqueado ? "#fcd4d4" : "#e0e0e0",
              color: "#111"
            }}>
              {m.texto}
              {m.camada && (
                <div style={{ marginTop: 6, fontSize: 11, color: "#c5221f" }}>
                  Bloqueado na camada {m.camada}
                  {m.similaridade != null && ` - similaridade: ${m.similaridade}`}
                </div>
              )}
            </div>
          </div>
        ))}
        {carregando && (
          <div style={{ alignSelf: "flex-start" }}>
            <div style={{ background: "#fff", border: "1px solid #e0e0e0", borderRadius: 12, padding: "10px 14px", fontSize: 13, color: "#999" }}>
              Consultando estoque...
            </div>
          </div>
        )}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
        {SUGESTOES.map((s, i) => (
          <button key={i} onClick={() => enviar(s)}
            style={{ background: "#f1f3f4", border: "1px solid #dadce0", borderRadius: 20, padding: "5px 12px", fontSize: 12, cursor: "pointer", color: "#444" }}>
            {s}
          </button>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <input value={msg} onChange={e => setMsg(e.target.value)} onKeyDown={e => e.key === "Enter" && enviar()}
          placeholder="Digite sua pergunta sobre o estoque..."
          style={{ flex: 1, padding: "10px 14px", borderRadius: 8, border: "1px solid #dadce0", fontSize: 13, outline: "none" }} />
        <button onClick={() => enviar()}
          style={{ background: "#1a73e8", color: "#fff", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, cursor: "pointer", fontWeight: 500 }}>
          Enviar
        </button>
      </div>
    </div>
  );
}
'@ | Set-Content "$src\Chat.jsx" -Encoding UTF8

Write-Host "Todos os arquivos criados com sucesso!" -ForegroundColor Green
