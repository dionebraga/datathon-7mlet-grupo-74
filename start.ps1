# =============================================================================
# start.ps1 — sobe a stack completa do Adaptive Offers em janelas separadas:
#   - API REST + Swagger   -> http://localhost:8000/docs
#   - MLflow (experimentos)-> http://localhost:5001
#   - Dashboard BI         -> http://localhost:8503
#   - Decision Console     -> http://localhost:3000   (Next.js; pulado sem Node)
#
# Uso (PowerShell, na pasta do projeto):
#   .\start.ps1
# Se bloquear por política de execução, rode uma vez:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Para encerrar tudo:  .\stop.ps1   (ou feche as janelas / CTRL+C em cada uma)
# =============================================================================

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

# Ativa o .venv automaticamente se existir (senão usa o Python/entrypoints globais).
$activate = Join-Path $root ".venv\Scripts\Activate.ps1"
$hasVenv = Test-Path $activate
if (-not $hasVenv) {
    Write-Host "[aviso] .venv nao encontrado — usando o Python global." -ForegroundColor Yellow
}

function Start-Service-Window([string]$title, [string]$cmd) {
    $prefix = if ($hasVenv) { "& '$activate'; " } else { "" }
    $full = "$prefix Set-Location '$root'; `$Host.UI.RawUI.WindowTitle = '$title'; " +
            "Write-Host '>> $title' -ForegroundColor Cyan; $cmd"
    # -EncodedCommand evita qualquer problema de aspas/escapes no caminho.
    $enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($full))
    Start-Process powershell -ArgumentList "-NoExit", "-EncodedCommand", $enc | Out-Null
}

Write-Host ""
Write-Host "  Adaptive Offers Platform — subindo a stack..." -ForegroundColor Magenta
Write-Host "  --------------------------------------------------" -ForegroundColor DarkGray

Start-Service-Window "Adaptive Offers - API (8000)"       "adaptive-offers serve"
Write-Host "  [1/4] API REST       -> http://localhost:8000/docs" -ForegroundColor Green

Start-Service-Window "Adaptive Offers - MLflow (5001)"     "`$env:MLFLOW_ALLOW_FILE_STORE='true'; mlflow ui --backend-store-uri file:./mlruns --registry-store-uri file:./mlruns --port 5001"
Write-Host "  [2/4] MLflow         -> http://localhost:5001" -ForegroundColor Green
Write-Host "        (na UI, use a aba 'Model training' — 'Overview'/'GenAI' exige backend SQL)" -ForegroundColor DarkGray

Start-Service-Window "Adaptive Offers - Dashboard (8503)"  "streamlit run dashboard\app.py --server.port 8503"
Write-Host "  [3/4] Dashboard BI   -> http://localhost:8503" -ForegroundColor Green

# O Decision Console é Next.js: precisa de Node e das dependências instaladas.
# Sem qualquer um dos dois, seguimos com as três superfícies Python em vez de
# derrubar o script inteiro.
$frontend = Join-Path $root "frontend"
$hasNode = $null -ne (Get-Command npm -ErrorAction SilentlyContinue)
if (-not $hasNode) {
    Write-Host "  [4/4] Decision Console -> PULADO (npm nao encontrado)" -ForegroundColor Yellow
} elseif (-not (Test-Path (Join-Path $frontend "node_modules"))) {
    Write-Host "  [4/4] Decision Console -> PULADO (rode 'npm install' em frontend\)" -ForegroundColor Yellow
} else {
    $enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes(
        "Set-Location '$frontend'; `$Host.UI.RawUI.WindowTitle = 'Adaptive Offers - Console (3000)'; " +
        "Write-Host '>> Decision Console (3000)' -ForegroundColor Cyan; npm run dev"))
    Start-Process powershell -ArgumentList "-NoExit", "-EncodedCommand", $enc | Out-Null
    Write-Host "  [4/4] Decision Console -> http://localhost:3000" -ForegroundColor Green
    Write-Host "        (primeira compilacao leva ~30s; a pagina so estiliza depois dela)" -ForegroundColor DarkGray
}

Write-Host "  --------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Abrindo o dashboard no navegador em alguns segundos..." -ForegroundColor DarkGray

# Dá tempo do Streamlit/MLflow iniciarem antes de abrir o navegador.
Start-Sleep -Seconds 8
Start-Process "http://localhost:8503"

Write-Host ""
Write-Host "  Pronto! Cada servico esta em sua propria janela." -ForegroundColor Magenta
Write-Host "  Para encerrar tudo:  .\stop.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Conferir as 4 portas:" -ForegroundColor DarkGray
Write-Host "    foreach (`$p in 8000,8503,5001,3000) { try { `"  :`$p -> `" + (Invoke-WebRequest `"http://localhost:`$p`" -TimeoutSec 5 -UseBasicParsing).StatusCode } catch { `"  :`$p -> FECHADA`" } }" -ForegroundColor DarkGray
Write-Host ""
