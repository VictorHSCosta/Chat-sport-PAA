#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando Chat Sport RAG..." -ForegroundColor Green

# Função para verificar se um processo está rodando
function Test-Process($processName) {
    return (Get-Process -Name $processName -ErrorAction SilentlyContinue) -ne $null
}

# Verificar se WSL está disponível
try {
    wsl --version | Out-Null
    Write-Host "✅ WSL está disponível" -ForegroundColor Green
} catch {
    Write-Host "❌ WSL não está disponível. Instale o WSL primeiro." -ForegroundColor Red
    exit 1
}

# Verificar se Ollama está rodando
Write-Host "🔍 Verificando Ollama..." -ForegroundColor Yellow
if (Test-Process "ollama") {
    Write-Host "✅ Ollama está rodando" -ForegroundColor Green
} else {
    Write-Host "⚠️ Ollama não está rodando!" -ForegroundColor Yellow
    Write-Host "Execute em outro terminal: ollama serve" -ForegroundColor Cyan
    Write-Host "Pressione qualquer tecla quando o Ollama estiver rodando..."
    Read-Host
}

# Navegar para o diretório correto
$projectPath = "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA"
if (Test-Path $projectPath) {
    Set-Location $projectPath
    Write-Host "✅ Diretório encontrado: $projectPath" -ForegroundColor Green
} else {
    Write-Host "❌ Diretório não encontrado: $projectPath" -ForegroundColor Red
    exit 1
}

# Iniciar backend
Write-Host "🚀 Iniciando backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA/backend && source footbot/bin/activate 2>/dev/null || true && python api.py"
}

# Aguardar um pouco para o backend inicializar
Write-Host "⏳ Aguardando backend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar se backend está respondendo
$maxTries = 10
$tries = 0
do {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Backend está rodando!" -ForegroundColor Green
        break
    } catch {
        $tries++
        Write-Host "⏳ Tentativa $tries/$maxTries - Aguardando backend..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
} while ($tries -lt $maxTries)

if ($tries -eq $maxTries) {
    Write-Host "❌ Backend não respondeu após $maxTries tentativas" -ForegroundColor Red
    Write-Host "Verifique os logs do job:" -ForegroundColor Yellow
    Receive-Job $backendJob
    exit 1
}

# Testar uma pergunta
Write-Host "🧪 Testando sistema com pergunta sobre Messi..." -ForegroundColor Yellow
try {
    $testResponse = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body '{"message": "fale sobre o lionel messi"}' -ContentType "application/json" -TimeoutSec 60
    Write-Host "✅ Teste bem-sucedido!" -ForegroundColor Green
    Write-Host "📝 Resposta: $($testResponse.answer.Substring(0, [Math]::Min(200, $testResponse.answer.Length)))..." -ForegroundColor Cyan
} catch {
    Write-Host "❌ Erro no teste: $($_.Exception.Message)" -ForegroundColor Red
}

# Iniciar frontend se solicitado
$startFrontend = Read-Host "Deseja iniciar o frontend também? (y/N)"
if ($startFrontend -eq "y" -or $startFrontend -eq "Y") {
    Write-Host "🚀 Iniciando frontend..." -ForegroundColor Yellow
    $frontendJob = Start-Job -ScriptBlock {
        wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA/Front/front-end && npm run dev"
    }
    Start-Sleep -Seconds 5
    Write-Host "🌐 Frontend iniciando em: http://localhost:5173" -ForegroundColor Green
}

Write-Host "`n🎉 Sistema iniciado com sucesso!" -ForegroundColor Green
Write-Host "🔗 URLs importantes:" -ForegroundColor Cyan
Write-Host "   - Backend: http://localhost:8000" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   - Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Status: http://localhost:8000/status" -ForegroundColor White

Write-Host "`n💡 Para parar, pressione Ctrl+C e execute:" -ForegroundColor Yellow
Write-Host "   Get-Job | Remove-Job -Force" -ForegroundColor White
