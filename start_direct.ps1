#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando API Direta com Ollama..." -ForegroundColor Green

# Parar processos anteriores
Write-Host "🛑 Parando processos anteriores..." -ForegroundColor Yellow
wsl -d Debian -- bash -c "pkill -f 'uvicorn\|python.*api' 2>/dev/null || true"
wsl -d Debian -- bash -c "fuser -k 8000/tcp 2>/dev/null || true"
Start-Sleep -Seconds 3

# Verificar Ollama
Write-Host "🔍 Verificando Ollama..." -ForegroundColor Yellow
$ollamaCheck = wsl -d Debian -- bash -c "pgrep ollama"
if (-not $ollamaCheck) {
    Write-Host "⚠️ Ollama não está rodando. Iniciando..." -ForegroundColor Yellow
    Start-Process -NoNewWindow -FilePath "wsl" -ArgumentList "-d", "Debian", "--", "bash", "-c", "cd /home/jpantonow && nohup ollama serve > ollama.log 2>&1 &"
    Start-Sleep -Seconds 10
}

# Ir para o backend
Write-Host "📂 Navegando para o backend..." -ForegroundColor Yellow
Set-Location "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA\backend"

# Verificar dados CSV
$csvDir = "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA\backend\wcdataset"
if (Test-Path $csvDir) {
    $csvFiles = Get-ChildItem -Path $csvDir -Filter "*.csv" | Measure-Object
    Write-Host "✅ Encontrados $($csvFiles.Count) arquivos CSV" -ForegroundColor Green
} else {
    Write-Host "❌ Dados CSV não encontrados!" -ForegroundColor Red
    exit 1
}

# Iniciar API direta
Write-Host "🚀 Iniciando API direta com Ollama..." -ForegroundColor Green
$process = Start-Process -NoNewWindow -PassThru -FilePath "wsl" -ArgumentList "-d", "Debian", "--", "bash", "-c", "cd /home/jpantonow/Chat-sport-PAA/backend && source footbot/bin/activate && python api_direct.py"

# Aguardar inicialização
Write-Host "⏰ Aguardando inicialização..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Testar
Write-Host "🧪 Testando API..." -ForegroundColor Yellow
$maxTries = 10
$tries = 0

do {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Host "✅ API está funcionando!" -ForegroundColor Green
        Write-Host "📊 Status: $($health.status)" -ForegroundColor Cyan
        break
    } catch {
        $tries++
        Write-Host "⏳ Tentativa $tries/$maxTries..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
} while ($tries -lt $maxTries)

if ($tries -eq $maxTries) {
    Write-Host "❌ API não respondeu" -ForegroundColor Red
    exit 1
}

# Teste rápido
Write-Host "`n🤖 Testando: 'quantas copas o brasil tem?'" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body '{"message": "quantas copas o brasil tem?"}' -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Resposta: $($response.answer)" -ForegroundColor White
} catch {
    Write-Host "❌ Erro no teste: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 API Direta funcionando!" -ForegroundColor Green
Write-Host "🌐 Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
