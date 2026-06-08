$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Iniciando EstoqueIA..." -ForegroundColor Cyan

Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Stop-Process -Name node   -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "Iniciando Ollama..." -ForegroundColor Yellow
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 3

Write-Host "Iniciando Backend..." -ForegroundColor Yellow
Start-Process "python" -ArgumentList "-m uvicorn main:app --port 8001" -WorkingDirectory "$BASE\backend" -WindowStyle Normal
Start-Sleep -Seconds 4

Write-Host "Iniciando Frontend..." -ForegroundColor Yellow
Start-Process "cmd" -ArgumentList "/k npm run dev" -WorkingDirectory "$BASE\frontend" -WindowStyle Normal
Start-Sleep -Seconds 4

Start-Process "http://localhost:5173"
Write-Host "Pronto! http://localhost:5173" -ForegroundColor Green
pause
