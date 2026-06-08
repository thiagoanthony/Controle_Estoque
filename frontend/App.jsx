import { useState } from "react";
import Dashboard from "./Dashboard";
import Chat from "./Chat";
import "./index.css";

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
