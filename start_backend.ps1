#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando backend do Chat Sport..." -ForegroundColor Green

# Verificar se Ollama está rodando
Write-Host "🔍 Verificando Ollama..." -ForegroundColor Yellow
try {
    $ollamaTest = wsl -d Debian -- bash -c "pgrep ollama"
    if ($ollamaTest) {
        Write-Host "✅ Ollama está rodando" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Ollama não detectado. Iniciando..." -ForegroundColor Yellow
        Start-Process -NoNewWindow -FilePath "wsl" -ArgumentList "-d", "Debian", "--", "bash", "-c", "cd /home/jpantonow && nohup ollama serve > ollama.log 2>&1 &"
        Start-Sleep -Seconds 5
    }
} catch {
    Write-Host "⚠️ Erro ao verificar Ollama. Continuando..." -ForegroundColor Yellow
}

# Parar processos anteriores do backend
Write-Host "🛑 Parando processos anteriores..." -ForegroundColor Yellow
wsl -d Debian -- bash -c "pkill -f 'python.*api.py' 2>/dev/null || true"
Start-Sleep -Seconds 2

# Ir para o diretório do backend
Write-Host "📂 Navegando para o backend..." -ForegroundColor Yellow
Set-Location "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA\backend"

# Verificar se data.txt existe
$dataFile = "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA\backend\data.txt"
if (Test-Path $dataFile) {
    $dataSize = (Get-Item $dataFile).Length
    Write-Host "✅ data.txt encontrado ($dataSize bytes)" -ForegroundColor Green
} else {
    Write-Host "❌ data.txt não encontrado!" -ForegroundColor Red
    exit 1
}

# Iniciar backend
Write-Host "🚀 Iniciando backend..." -ForegroundColor Green
Write-Host "⏳ Aguarde alguns segundos para inicialização completa..." -ForegroundColor Yellow

# Usar wsl para iniciar o backend
$process = Start-Process -NoNewWindow -PassThru -FilePath "wsl" -ArgumentList "-d", "Debian", "--", "bash", "-c", "cd /home/jpantonow/Chat-sport-PAA/backend && source footbot/bin/activate 2>/dev/null || python3 -m venv footbot && source footbot/bin/activate && pip install -q -r requirements.txt && python api.py"

# Aguardar inicialização
Start-Sleep -Seconds 20

# Testar backend
Write-Host "🧪 Testando backend..." -ForegroundColor Yellow
$maxTries = 15
$tries = 0
do {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Host "✅ Backend está saudável!" -ForegroundColor Green
        Write-Host "📊 Status: $($health.status)" -ForegroundColor Cyan
        break
    } catch {
        $tries++
        Write-Host "⏳ Tentativa $tries/$maxTries..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
} while ($tries -lt $maxTries)

if ($tries -eq $maxTries) {
    Write-Host "❌ Backend não respondeu. Verifique os logs." -ForegroundColor Red
    exit 1
}

# Testar pergunta sobre Messi
Write-Host "`n🤖 Testando pergunta: 'fale sobre o lionel messi'" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body '{"message": "fale sobre o lionel messi"}' -ContentType "application/json" -TimeoutSec 180
    Write-Host "✅ Resposta recebida!" -ForegroundColor Green
    Write-Host "📝 Início da resposta: $($response.answer.Substring(0, [Math]::Min(150, $response.answer.Length)))..." -ForegroundColor White
} catch {
    Write-Host "❌ Erro na pergunta: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Backend rodando com sucesso!" -ForegroundColor Green
Write-Host "🌐 Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔍 Status: http://localhost:8000/status" -ForegroundColor Cyan
Write-Host "`n💡 Mantenha este terminal aberto para manter o backend rodando." -ForegroundColor Yellow
