# ============================================================
#  EstoqueIA — Inicializador completo
#  Salve este arquivo em:
#  C:\Users\Thiago\OneDrive\Documentos\controle_estoque\
#  e execute com duplo clique ou pelo PowerShell
# ============================================================

$BASE = "C:\Users\Thiago\OneDrive\Documentos\controle_estoque"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   EstoqueIA — Iniciando o projeto...      " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Encerra processos anteriores ──────────────────────────
Write-Host "[1/4] Encerrando processos anteriores..." -ForegroundColor Yellow
Stop-Process -Name python  -Force -ErrorAction SilentlyContinue
Stop-Process -Name ollama  -Force -ErrorAction SilentlyContinue
Stop-Process -Name node    -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# ── 2. Inicia o Ollama ────────────────────────────────────────
Write-Host "[2/4] Iniciando Ollama..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 3
Write-Host "      Ollama rodando em http://localhost:11434" -ForegroundColor Green

# ── 3. Inicia o Backend (FastAPI) ─────────────────────────────
Write-Host "[3/4] Iniciando Backend FastAPI..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "python" `
    -ArgumentList "-m uvicorn main:app --port 8080" `
    -WorkingDirectory $BASE `
    -PassThru -WindowStyle Normal
Start-Sleep -Seconds 4
Write-Host "      Backend rodando em http://localhost:8080" -ForegroundColor Green

# ── 4. Inicia o Frontend (React) ──────────────────────────────
Write-Host "[4/4] Iniciando Frontend React..." -ForegroundColor Yellow
$frontend = Start-Process -FilePath "cmd" `
    -ArgumentList "/k npm run dev" `
    -WorkingDirectory "$BASE\frontend" `
    -PassThru -WindowStyle Normal
Start-Sleep -Seconds 4
Write-Host "      Frontend rodando em http://localhost:5173" -ForegroundColor Green

# ── Abre o navegador ─────────────────────────────────────────
Write-Host ""
Write-Host "Abrindo o navegador..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   EstoqueIA rodando com sucesso!           " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Frontend : http://localhost:5173" -ForegroundColor White
Write-Host "  Backend  : http://localhost:8080" -ForegroundColor White
Write-Host "  API Docs : http://localhost:8080/docs" -ForegroundColor White
Write-Host ""
Write-Host "Para encerrar, feche as janelas do backend e frontend." -ForegroundColor Gray
Write-Host ""
pause
