import { useState, useEffect, useRef } from "react";
import api from "./api";

const SUGESTOES = [
  "Quantas Coca-Cola 2L existem?",
  "Quais produtos precisam de reposicao?",
  "Qual o preco do Arroz Tio Joao?",
  "Quem ganhou o Brasileirao?",
];

export default function Chat() {
  const [msg, setMsg] = useState("");
  const [historico, setHistorico] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [loadingHist, setLoadingHist] = useState(true);
  const bottomRef = useRef(null);

  useEffect(() => {
    api.get("/historico?limite=100")
      .then(r => {
        setHistorico(r.data.length === 0
          ? [{ role: "ai", texto: "Ola! Sou seu assistente de estoque.", criado_em: null }]
          : r.data);
      })
      .catch(() => setHistorico([{ role: "ai", texto: "Ola! Sou seu assistente de estoque.", criado_em: null }]))
      .finally(() => setLoadingHist(false));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [historico, carregando]);

  async function enviar(pergunta) {
    const texto = pergunta || msg.trim();
    if (!texto || carregando) return;
    setHistorico(h => [...h, { role: "user", texto, criado_em: null }]);
    setMsg("");
    setCarregando(true);
    try {
      const r = await api.post("/chat", { pergunta: texto });
      const d = r.data;
      setHistorico(h => [...h, {
        role: "ai", texto: d.resposta,
        bloqueado: d.bloqueado, camada: d.camada_bloqueio,
        similaridade: d.similaridade, criado_em: null
      }]);
    } catch {
      setHistorico(h => [...h, { role: "ai", texto: "Erro ao conectar com o servidor.", bloqueado: true, criado_em: null }]);
    } finally {
      setCarregando(false);
    }
  }

  async function limpar() {
    if (!confirm("Deseja limpar todo o historico?")) return;
    await api.delete("/historico");
    setHistorico([{ role: "ai", texto: "Historico limpo. Como posso ajudar?", criado_em: null }]);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 56px)" }}>
      <div style={{ padding: "8px 1.5rem", background: "#fff", borderBottom: "1px solid #e0e0e0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: 12, color: "#999" }}>
          {loadingHist ? "Carregando historico..." : `${historico.length} mensagens salvas`}
        </span>
        <button onClick={limpar} style={{ background: "none", border: "1px solid #dadce0", borderRadius: 6, padding: "4px 12px", fontSize: 12, color: "#d93025", cursor: "pointer" }}>
          Limpar historico
        </button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "1.25rem 1.5rem", display: "flex", flexDirection: "column", gap: 12 }}>
        {historico.map((m, i) => (
          <div key={i} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", maxWidth: "75%" }}>
            <div style={{ fontSize: 11, color: "#aaa", marginBottom: 3, textAlign: m.role === "user" ? "right" : "left", display: "flex", gap: 8, justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
              <span>{m.role === "user" ? "Voce" : "Assistente IA - Llama 3.2"}</span>
              {m.criado_em && <span>- {m.criado_em}</span>}
            </div>
            <div style={{ padding: "10px 14px", borderRadius: 12, fontSize: 13, lineHeight: 1.6, background: m.role === "user" ? "#e8f0fe" : "#fff", border: "1px solid", borderColor: m.role === "user" ? "#c5d8fb" : m.bloqueado ? "#fcd4d4" : "#e0e0e0", color: "#111" }}>
              {m.texto}
              {m.camada && (
                <div style={{ marginTop: 6, fontSize: 11, color: "#c5221f" }}>
                  Bloqueado na camada {m.camada}{m.similaridade != null && ` - similaridade: ${m.similaridade}`}
                </div>
              )}
            </div>
          </div>
        ))}
        {carregando && (
          <div style={{ alignSelf: "flex-start" }}>
            <div style={{ fontSize: 11, color: "#aaa", marginBottom: 3 }}>Assistente IA - Llama 3.2</div>
            <div style={{ background: "#fff", border: "1px solid #e0e0e0", borderRadius: 12, padding: "10px 14px", display: "flex", gap: 5, alignItems: "center" }}>
              {[0,1,2].map(i => <div key={i} style={{ width: 7, height: 7, borderRadius: "50%", background: "#bbb", animation: `pulse 1s ${i*0.2}s infinite` }} />)}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={{ padding: "0 1.5rem 8px", display: "flex", gap: 8, flexWrap: "wrap" }}>
        {SUGESTOES.map((s, i) => (
          <button key={i} onClick={() => enviar(s)} style={{ background: "#f1f3f4", border: "1px solid #dadce0", borderRadius: 20, padding: "5px 12px", fontSize: 12, cursor: "pointer", color: "#444" }}>{s}</button>
        ))}
      </div>

      <div style={{ padding: "8px 1.5rem 1rem", display: "flex", gap: 8, borderTop: "1px solid #e0e0e0", background: "#fff" }}>
        <input value={msg} onChange={e => setMsg(e.target.value)} onKeyDown={e => e.key === "Enter" && enviar()}
          placeholder="Digite sua pergunta sobre o estoque..."
          style={{ flex: 1, padding: "10px 14px", borderRadius: 8, border: "1px solid #dadce0", fontSize: 13, outline: "none" }} />
        <button onClick={() => enviar()} disabled={carregando} style={{ background: carregando ? "#bbb" : "#1a73e8", color: "#fff", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, cursor: carregando ? "not-allowed" : "pointer", fontWeight: 500 }}>
          {carregando ? "..." : "Enviar"}
        </button>
      </div>

      <style>{`@keyframes pulse { 0%,100%{opacity:.3;transform:scale(.8)} 50%{opacity:1;transform:scale(1)} }`}</style>
    </div>
  );
}
