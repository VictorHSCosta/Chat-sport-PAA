#!/bin/bash

# Setup essencial para Chat-sport-PAA - LlamaIndex + Groq
echo "🏆 Setup Essencial - World Cup RAG Chatbot"
echo "⚡ LlamaIndex + Groq (llama3-70b-8192)"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# 1. Verificar Python
log_info "Verificando Python..."
python3 --version || {
    log_error "Python 3 não encontrado. Instale Python 3.8+"
    exit 1
}
log_success "Python encontrado"

# 2. Verificar Node.js para frontend
log_info "Verificando Node.js..."
node --version || {
    log_error "Node.js não encontrado. Instale Node.js 18+"
    exit 1
}
log_success "Node.js encontrado"

# 3. Verificar/criar ambiente virtual Python
log_info "Configurando ambiente virtual Python..."
cd backend
if [ ! -d "footbot" ]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv footbot
fi

# 4. Ativar ambiente virtual e instalar dependências
log_info "Ativando ambiente virtual e instalando dependências..."
source footbot/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

log_success "Dependências Python instaladas"

# 5. Validar datasets essenciais
log_info "Validando datasets..."
if [ ! -f "wcdataset/world_cup.csv" ]; then
    log_error "Dataset world_cup.csv não encontrado!"
    exit 1
fi

if [ ! -f "wcdataset/matches_1930_2022.csv" ]; then
    log_error "Dataset matches_1930_2022.csv não encontrado!"
    exit 1
fi

log_success "Datasets validados"

# 6. Configurar frontend
log_info "Configurando frontend..."
cd ../Front/front-end

# Usar npm (mais estável que pnpm)
if [ ! -d "node_modules" ]; then
    log_info "Instalando dependências do frontend..."
    npm install
fi

log_success "Frontend configurado"

# 7. Verificar API Key do Groq
cd ../../
if [ -z "$GROQ_API_KEY" ]; then
    log_warning "GROQ_API_KEY não configurada. Usando chave padrão."
    log_info "Para configurar: export GROQ_API_KEY=sua_chave_aqui"
else
    log_success "GROQ_API_KEY configurada"
fi

echo ""
log_success "Setup concluído com sucesso!"
log_info "Para iniciar o sistema, execute: ./start.sh"
echo ""
