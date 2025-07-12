#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando backend do World Cup Chat..." -ForegroundColor Green

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
wsl -d Debian -- bash -c "pkill -f 'uvicorn\|python.*api' 2>/dev/null || true"
wsl -d Debian -- bash -c "fuser -k 8000/tcp 2>/dev/null || true"
Start-Sleep -Seconds 3

# Ir para o diretório do backend
Write-Host "📂 Navegando para o backend..." -ForegroundColor Yellow
Set-Location "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA\backend"

# Verificar se dados CSV existem
$csvDir = "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA\backend\wcdataset"
if (Test-Path $csvDir) {
    Write-Host "✅ Diretório wcdataset encontrado" -ForegroundColor Green
    $csvFiles = Get-ChildItem -Path $csvDir -Filter "*.csv" | Measure-Object
    Write-Host "📊 Encontrados $($csvFiles.Count) arquivos CSV" -ForegroundColor Green
} else {
    Write-Host "❌ Diretório wcdataset não encontrado!" -ForegroundColor Red
    exit 1
}

# Iniciar backend
Write-Host "🚀 Iniciando backend..." -ForegroundColor Green
Write-Host "⏳ Aguarde alguns segundos para inicialização completa..." -ForegroundColor Yellow

# Primeiro, garantir que o ambiente virtual está ativo e as dependências instaladas
Write-Host "🔧 Preparando ambiente Python..." -ForegroundColor Yellow
$setupResult = wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA/backend && source footbot/bin/activate && pip install -q pandas uvicorn fastapi langchain langchain-community sentence-transformers faiss-cpu pydantic"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao preparar ambiente Python" -ForegroundColor Red
    exit 1
}

# Verificar se os dados CSV existem
Write-Host "📊 Verificando dados CSV..." -ForegroundColor Yellow
$csvCheck = wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA/backend && find wcdataset -name '*.csv' | wc -l"
Write-Host "✅ Encontrados $csvCheck arquivos CSV" -ForegroundColor Green

# Iniciar o backend em background
Write-Host "📡 Iniciando servidor API..." -ForegroundColor Green
$process = Start-Process -NoNewWindow -PassThru -FilePath "wsl" -ArgumentList "-d", "Debian", "--", "bash", "-c", "cd /home/jpantonow/Chat-sport-PAA/backend && source footbot/bin/activate && python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload --log-level info"

# Aguardar inicialização
Write-Host "⏰ Aguardando inicialização da API..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar se a porta está sendo usada
Write-Host "🔍 Verificando porta 8000..." -ForegroundColor Yellow
$portCheck = wsl -d Debian -- bash -c "netstat -tlnp | grep :8000 || echo 'Porta não encontrada'"
Write-Host "📡 Status da porta: $portCheck" -ForegroundColor Cyan

# Testar backend
Write-Host "🧪 Testando backend..." -ForegroundColor Yellow
$maxTries = 20
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
    Write-Host "❌ Backend não respondeu após $maxTries tentativas." -ForegroundColor Red
    Write-Host "🔍 Diagnóstico:" -ForegroundColor Yellow
    
    # Verificar se o processo ainda está rodando
    $processCheck = wsl -d Debian -- bash -c "pgrep -f 'uvicorn\|python.*api' || echo 'Nenhum processo encontrado'"
    Write-Host "📋 Processos: $processCheck" -ForegroundColor Cyan
    
    # Verificar logs recentes
    Write-Host "📝 Tentando obter logs do sistema..." -ForegroundColor Yellow
    $logs = wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA/backend && journalctl --no-pager -n 10 2>/dev/null || echo 'Logs não disponíveis'"
    Write-Host "📊 Status: $logs" -ForegroundColor Cyan
    
    exit 1
}

# Testar pergunta sobre Copa do Mundo
Write-Host "`n🤖 Testando pergunta: 'quantas copas o brasil tem?'" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body '{"message": "quantas copas o brasil tem?"}' -ContentType "application/json" -TimeoutSec 60
    Write-Host "✅ Resposta recebida!" -ForegroundColor Green
    Write-Host "📝 Resposta: $($response.answer)" -ForegroundColor White
} catch {
    Write-Host "❌ Erro na pergunta: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Isso pode ser normal se o modelo estiver carregando pela primeira vez" -ForegroundColor Yellow
}

Write-Host "`n🎉 Backend rodando com sucesso!" -ForegroundColor Green
Write-Host "🌐 Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔍 Status: http://localhost:8000/status" -ForegroundColor Cyan
Write-Host "`n💡 Mantenha este terminal aberto para manter o backend rodando." -ForegroundColor Yellow
