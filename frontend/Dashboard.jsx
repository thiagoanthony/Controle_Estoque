import { useEffect, useState } from "react";
import api from "./api";

export default function Dashboard() {
  const [dados, setDados] = useState(null);

  useEffect(() => {
    api.get("/dashboard").then(r => setDados(r.data));
  }, []);

  if (!dados) return <p style={{ padding: "2rem" }}>Carregando...</p>;

  return (
    <div style={{ padding: "1.5rem" }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 24 }}>
        <Card label="Total de produtos" value={dados.total_produtos} cor="#1a73e8" />
        <Card label="Produtos críticos" value={dados.produtos_criticos} cor="#d93025" />
        <Card label="Estoque baixo" value={dados.produtos_estoque_baixo} cor="#f9ab00" />
        <Card label="Valor total" value={`R$ ${dados.valor_total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`} cor="#1e8e3e" />
      </div>

      <div style={{ background: "#fff", borderRadius: 8, border: "1px solid #e0e0e0", padding: "1.25rem" }}>
        <h3 style={{ margin: "0 0 1rem", fontSize: 14, color: "#333" }}>⚠️ Produtos críticos</h3>
        {dados.lista_criticos.length === 0 && <p style={{ color: "#888", fontSize: 13 }}>Nenhum produto crítico.</p>}
        {dados.lista_criticos.map((p, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid #f0f0f0" }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 500 }}>{p.nome}</div>
              <div style={{ fontSize: 12, color: "#888" }}>{p.categoria} · mín: {p.estoque_minimo} un</div>
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
