#!/bin/bash

# Script de configuração inicial do projeto
echo "🛠️ Configuração Inicial - Chat Sport RAG"
echo "⚡ Preparando ambiente para máxima performance"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar Python
log_info "Verificando Python..."
python3 --version || {
    echo "❌ Python 3 não encontrado. Instale Python 3.8+"
    exit 1
}
log_success "Python encontrado"

# 2. Criar ambiente virtual se não existir
log_info "Configurando ambiente virtual Python..."
cd ~/Chat-sport-PAA/backend

if [ ! -d "footbot" ]; then
    python3 -m venv footbot
    log_success "Ambiente virtual criado"
else
    log_success "Ambiente virtual já existe"
fi

# 3. Ativar e instalar dependências
source footbot/bin/activate
log_info "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
log_success "Dependências Python instaladas"

# 4. Verificar Node.js e gerenciador de pacotes
log_info "Verificando Node.js..."
cd ~/Chat-sport-PAA/Front/front-end

if ! command -v node &> /dev/null; then
    log_error "Node.js não encontrado! Instale Node.js 16+ primeiro."
    exit 1
fi

# Verificar qual gerenciador de pacotes usar
if command -v pnpm &> /dev/null; then
    log_info "Usando pnpm para dependências do frontend..."
    pnpm install
elif command -v yarn &> /dev/null; then
    log_info "Usando yarn para dependências do frontend..."
    yarn install
else
    log_info "Usando npm para dependências do frontend..."
    npm install
fi

log_success "Dependências do frontend instaladas"

# 5. Criar índice FAISS otimizado
log_info "Criando índice FAISS otimizado..."
cd ~/Chat-sport-PAA/backend
source footbot/bin/activate
python optimize_index.py
log_success "Índice FAISS otimizado criado"

# 6. Tornar scripts executáveis
log_info "Configurando permissões..."
chmod +x ~/Chat-sport-PAA/start.sh
chmod +x ~/Chat-sport-PAA/backend/test_performance.sh
log_success "Permissões configuradas"

# 7. Verificar Ollama
log_info "Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    log_warning "Ollama não encontrado!"
    echo ""
    echo "📥 Para instalar Ollama:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "📥 Depois execute:"
    echo "   ollama serve"
    echo "   ollama pull tinyllama"
    echo ""
else
    log_success "Ollama encontrado"
    
    # Verificar se está rodando
    if ! pgrep -x "ollama" > /dev/null; then
        log_warning "Ollama não está rodando"
        echo "💡 Para iniciar: ollama serve"
    else
        log_success "Ollama está rodando"
        
        # Baixar modelo se necessário
        if ! ollama list | grep -q "tinyllama"; then
            log_info "Baixando modelo tinyllama..."
            ollama pull tinyllama
            log_success "Modelo tinyllama baixado"
        else
            log_success "Modelo tinyllama disponível"
        fi
    fi
fi

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "🚀 Para iniciar o projeto:"
echo "   ./start.sh"
echo ""
echo "📊 Outras opções:"
echo "   ./start.sh backend    # Só backend"
echo "   ./start.sh frontend   # Só frontend"
echo "   ./start.sh test       # Testar performance"
echo "   ./start.sh optimize   # Recriar índice"
echo ""
log_success "Projeto pronto para uso ultra-rápido!"
