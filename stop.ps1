# =============================================================================
# stop.ps1 — encerra a stack do Adaptive Offers (API 8000, MLflow 5001, BI 8503,
#            Decision Console 3000) e qualquer sobra em portas vizinhas.
# Uso:  .\stop.ps1
# =============================================================================
# Inclui 8501/8504 (portas em que um Streamlit pode ter subido manualmente) e
# 3000 (Decision Console), para nao sobrar processo preso antes da gravacao.
$ports = 8000, 5000, 5001, 5050, 8501, 8503, 8504, 3000
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        $conns.OwningProcess | Select-Object -Unique | ForEach-Object {
            try { Stop-Process -Id $_ -Force -ErrorAction Stop; Write-Host "  porta $p (pid $_) encerrada" -ForegroundColor Green }
            catch { }
        }
    } else {
        Write-Host "  porta ${p}: nada rodando" -ForegroundColor DarkGray
    }
}
Write-Host "Stack encerrada." -ForegroundColor Magenta
