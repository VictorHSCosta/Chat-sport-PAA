#!/bin/bash

# Start essencial para Chat-sport-PAA - LlamaIndex + Groq
echo "🚀 Chat-sport-PAA - LlamaIndex + Groq"
echo "⚡ Iniciando sistema essencial"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_highlight() { echo -e "${PURPLE}🎯 $1${NC}"; }

# Função para limpar processos ao sair
cleanup() {
    log_info "Finalizando processos..."
    pkill -f "uvicorn.*api" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    exit 0
}

# Capturar sinais para limpeza
trap cleanup SIGINT SIGTERM

# Função para aguardar backend estar pronto
wait_for_backend() {
    local max_attempts=30
    local attempt=1
    
    log_info "Aguardando backend inicializar..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    echo ""
    return 1
}

# 1. Iniciar Backend
log_highlight "=== INICIANDO BACKEND ==="

cd backend

# Verificar ambiente virtual
if [ ! -d "footbot" ]; then
    log_error "Ambiente virtual não encontrado. Execute ./setup.sh primeiro"
    exit 1
fi

# Ativar ambiente virtual
source footbot/bin/activate

# Verificar se API existe
if [ ! -f "api.py" ]; then
    log_error "api.py não encontrado!"
    exit 1
fi

# Iniciar backend
log_info "Iniciando servidor backend..."
uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Aguardar backend estar pronto
if wait_for_backend; then
    log_success "Backend iniciado na porta 8000!"
else
    log_error "Falha ao iniciar backend"
    exit 1
fi

# Testar API rapidamente
log_info "Testando API..."
API_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
if echo "$API_RESPONSE" | grep -q "healthy"; then
    log_success "API respondendo corretamente!"
else
    log_warning "API pode não estar totalmente pronta"
fi

# 2. Iniciar Frontend
log_highlight "=== INICIANDO FRONTEND ==="

cd ../Front/front-end

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    log_error "Dependências do frontend não instaladas. Execute ./setup.sh primeiro"
    exit 1
fi

log_info "Iniciando servidor frontend..."
npm run dev &
FRONTEND_PID=$!

sleep 3
log_success "Frontend iniciado na porta 5173!"

# 3. Status final
echo ""
log_highlight "=== SISTEMA PRONTO ==="
log_success "Backend: http://localhost:8000"
log_success "Frontend: http://localhost:5173"
log_success "API Docs: http://localhost:8000/docs"
echo ""
log_info "Pressione Ctrl+C para parar o sistema"
echo ""

# Aguardar input do usuário
wait
