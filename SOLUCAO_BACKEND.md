# 🚀 Solução Rápida - Backend Não Está Rodando

## ❌ Problema
```
Erro de conexão: Failed to fetch. Verifique se o servidor está rodando em http://localhost:8000
```

## ✅ Solução em 3 Passos

### 1. Iniciar Ollama (OBRIGATÓRIO)
```powershell
# Em um PowerShell separado:
ollama serve
```

### 2. Iniciar Backend (Escolha uma opção)

#### Opção A: Script PowerShell (RECOMENDADO)
```powershell
cd "\\wsl.localhost\Debian\home\jpantonow\Chat-sport-PAA"
.\start_backend.ps1
```

#### Opção B: Manual via WSL
```powershell
wsl -d Debian
cd /home/jpantonow/Chat-sport-PAA/backend
source footbot/bin/activate
python api.py
```

#### Opção C: Script Bash
```powershell
wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA && ./start_simple.sh backend"
```

### 3. Testar Sistema
Aguarde 20-30 segundos e acesse:
- http://localhost:8000/health
- http://localhost:8000/status

## 🧪 Teste a Pergunta
Após o backend estar rodando, teste no frontend:
```
fale sobre o lionel messi
```

## 🔧 Troubleshooting

### "Ollama não encontrado"
```powershell
# Instalar Ollama:
# 1. Baixe de https://ollama.ai
# 2. Execute: ollama serve
# 3. Execute: ollama pull tinyllama
```

### "Backend não inicia"
```powershell
# Verificar logs:
wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA/backend && python api.py"
```

### "Dependências faltando"
```powershell
# Reinstalar dependências:
wsl -d Debian -- bash -c "cd /home/jpantonow/Chat-sport-PAA/backend && pip install -r requirements.txt"
```

### "Timeout ainda ocorrendo"
- ✅ Sistema configurado para 150s de timeout
- ✅ Aguarde mais tempo para respostas complexas
- ✅ Use perguntas mais simples para testar primeiro

## 📊 Status Esperado
Quando tudo estiver funcionando:
- ✅ Ollama: Rodando em background
- ✅ Backend: http://localhost:8000/health retorna "healthy"
- ✅ Frontend: Conecta sem erro "Failed to fetch"
- ✅ Respostas: Chegam em 5-30 segundos

## 🎯 URLs Importantes
- **Backend Health**: http://localhost:8000/health
- **Backend Status**: http://localhost:8000/status  
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
