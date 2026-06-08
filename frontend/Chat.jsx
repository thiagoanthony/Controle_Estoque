import { useState } from "react";
import api from "./api";

const SUGESTOES = [
  "Quantas Coca-Cola 2L existem?",
  "Quais produtos precisam de reposição?",
  "Qual o preço do Arroz Tio João?",
  "Quem ganhou o Brasileirão?",
];

export default function Chat() {
  const [msg, setMsg] = useState("");
  const [historico, setHistorico] = useState([
    { role: "ai", texto: "Olá! Sou seu assistente de estoque. Pergunte sobre produtos, quantidades ou relatórios." }
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
        role: "ai",
        texto: d.resposta,
        bloqueado: d.bloqueado,
        camada: d.camada_bloqueio,
        similaridade: d.similaridade
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
              {m.role === "user" ? "Você" : "Assistente IA · Llama 3.2"}
            </div>
            <div style={{
              padding: "10px 14px",
              borderRadius: 12,
              fontSize: 13,
              lineHeight: 1.6,
              background: m.role === "user" ? "#e8f0fe" : "#fff",
              border: "1px solid",
              borderColor: m.role === "user" ? "#c5d8fb" : m.bloqueado ? "#fcd4d4" : "#e0e0e0",
              color: "#111"
            }}>
              {m.texto}
              {m.camada && (
                <div style={{ marginTop: 6, fontSize: 11, color: "#c5221f" }}>
                  🔒 Bloqueado na camada {m.camada}
                  {m.similaridade !== null && m.similaridade !== undefined && ` · similaridade: ${m.similaridade}`}
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
        <input
          value={msg}
          onChange={e => setMsg(e.target.value)}
          onKeyDown={e => e.key === "Enter" && enviar()}
          placeholder="Digite sua pergunta sobre o estoque..."
          style={{ flex: 1, padding: "10px 14px", borderRadius: 8, border: "1px solid #dadce0", fontSize: 13, outline: "none" }}
        />
        <button onClick={() => enviar()}
          style={{ background: "#1a73e8", color: "#fff", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, cursor: "pointer", fontWeight: 500 }}>
          Enviar
        </button>
      </div>
    </div>
  );
}
