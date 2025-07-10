#!/bin/bash

# Script otimizado para iniciar o Chat Sport - Sistema RAG Ultra-Rápido
echo "🚀 Iniciando Chat Sport - Sistema RAG Ultra-Performático"
echo "⚡ Versão Otimizada com Cache Inteligente e Respostas Rápidas"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Ollama está rodando
log_info "Verificando Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    log_error "Ollama não está rodando!"
    echo "💡 Para iniciar o Ollama:"
    echo "   - Abra um novo terminal"
    echo "   - Execute: ollama serve"
    echo "   - Deixe rodando em background"
    exit 1
fi

log_success "Ollama está rodando"

# Verificar se o modelo tinyllama está disponível
log_info "Verificando modelo tinyllama..."
if ! ollama list | grep -q "tinyllama"; then
    log_warning "Modelo tinyllama não encontrado"
    echo "📥 Baixando modelo tinyllama (pode demorar alguns minutos)..."
    ollama pull tinyllama
    if [ $? -eq 0 ]; then
        log_success "Modelo tinyllama baixado com sucesso"
    else
        log_error "Falha ao baixar modelo tinyllama"
        exit 1
    fi
else
    log_success "Modelo tinyllama disponível"
fi

# Verificar dependências do Python
check_python_deps() {
    log_info "Verificando dependências Python..."
    cd ~/Chat-sport-PAA/backend
    
    if [ ! -d "footbot" ]; then
        log_error "Ambiente virtual 'footbot' não encontrado"
        echo "💡 Execute primeiro: python -m venv footbot"
        exit 1
    fi
    
    source footbot/bin/activate
    
    # Verificar se as principais dependências estão instaladas
    python -c "import fastapi, uvicorn, langchain, faiss" 2>/dev/null
    if [ $? -ne 0 ]; then
        log_warning "Dependências Python não estão completas"
        echo "📦 Instalando/atualizando dependências..."
        pip install -r requirements.txt
    fi
    
    log_success "Dependências Python verificadas"
}

# Otimizar índice FAISS se necessário
optimize_index() {
    log_info "Verificando índice FAISS..."
    cd ~/Chat-sport-PAA/backend
    source footbot/bin/activate
    
    if [ ! -f "faiss_index_/index.faiss" ]; then
        log_warning "Índice FAISS não encontrado"
        echo "🏗️ Criando índice FAISS otimizado..."
        python optimize_index.py
        if [ $? -eq 0 ]; then
            log_success "Índice FAISS otimizado criado"
        else
            log_error "Falha ao criar índice FAISS"
            exit 1
        fi
    else
        # Verificar se o índice é antigo (mais de 1 dia)
        if find "faiss_index_/index.faiss" -mtime +1 2>/dev/null | grep -q .; then
            log_warning "Índice FAISS é antigo, recriando versão otimizada..."
            python optimize_index.py
        else
            log_success "Índice FAISS otimizado está atualizado"
        fi
    fi
}

# Função para iniciar backend otimizado
start_backend() {
    log_info "Iniciando backend otimizado..."
    cd ~/Chat-sport-PAA/backend
    source footbot/bin/activate
    
    echo ""
    echo "🎯 Configurações de Performance:"
    echo "   - Cache inteligente ativado"
    echo "   - Respostas rápidas para Pelé, Messi, Copa do Mundo"
    echo "   - Timeout otimizado: 3 segundos"
    echo "   - Chunks mini: 300 caracteres"
    echo "   - LLM limitado: 30 tokens"
    echo ""
    
    log_success "Backend iniciado em http://localhost:8000"
    echo "📊 Documentação: http://localhost:8000/docs"
    echo "🔍 Health check: http://localhost:8000/health"
    echo ""
    
    python api.py
}

# Função para iniciar frontend
start_frontend() {
    log_info "Iniciando frontend..."
    cd ~/Chat-sport-PAA/Front/front-end
    
    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        log_warning "Dependências frontend não encontradas"
        echo "📦 Instalando dependências..."
        
        # Verificar qual gerenciador de pacotes usar
        if command -v pnpm &> /dev/null; then
            pnpm install
        elif command -v yarn &> /dev/null; then
            yarn install
        else
            npm install
        fi
    fi
    
    log_success "Frontend iniciado em http://localhost:5173"
    echo "🌐 Interface do chat disponível"
    echo ""
    
    # Usar o gerenciador de pacotes disponível
    if command -v pnpm &> /dev/null; then
        pnpm run dev
    elif command -v yarn &> /dev/null; then
        yarn dev
    else
        npm run dev
    fi
}

# Verificar dependências
check_python_deps
optimize_index

# Verificar argumentos
case "$1" in
    "backend")
        start_backend
        ;;
    "frontend")
        start_frontend
        ;;
    "test")
        log_info "Executando testes de performance..."
        cd ~/Chat-sport-PAA/backend
        source footbot/bin/activate
        chmod +x test_performance.sh
        ./test_performance.sh
        ;;
    "optimize")
        log_info "Recriando índice FAISS otimizado..."
        cd ~/Chat-sport-PAA/backend
        source footbot/bin/activate
        python optimize_index.py
        log_success "Otimização concluída!"
        ;;
    "both"|"")
        echo "🔄 Iniciando backend e frontend otimizados..."
        echo ""
        
        # Iniciar backend em background
        start_backend &
        BACKEND_PID=$!
        
        # Aguardar backend inicializar
        log_info "Aguardando backend inicializar..."
        sleep 8
        
        # Verificar se backend está funcionando
        if curl -s http://localhost:8000/health > /dev/null; then
            log_success "Backend inicializado com sucesso"
        else
            log_warning "Backend pode estar demorando para inicializar"
        fi
        
        # Iniciar frontend
        start_frontend &
        FRONTEND_PID=$!
        
        echo ""
        log_success "Ambos os serviços foram iniciados!"
        echo ""
        echo "🎯 URLs importantes:"
        echo "   📊 Backend API: http://localhost:8000"
        echo "   📚 Docs API: http://localhost:8000/docs"
        echo "   🌐 Frontend: http://localhost:5173"
        echo ""
        echo "⚡ Performance esperada:"
        echo "   - Perguntas sobre Pelé: < 0.5s"
        echo "   - Outras perguntas: 1-3s"
        echo "   - Timeout máximo: 3s"
        echo ""
        echo "Para parar os serviços, pressione Ctrl+C"
        
        # Aguardar interrupção
        trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' INT
        wait $BACKEND_PID $FRONTEND_PID
        ;;
    *)
        echo "Uso: $0 [opção]"
        echo ""
        echo "Opções:"
        echo "  backend   - Iniciar apenas o backend otimizado"
        echo "  frontend  - Iniciar apenas o frontend"
        echo "  both      - Iniciar ambos (padrão)"
        echo "  test      - Executar testes de performance"
        echo "  optimize  - Recriar índice FAISS otimizado"
        echo ""
        echo "Exemplos:"
        echo "  ./start.sh              # Inicia tudo"
        echo "  ./start.sh backend      # Só backend"
        echo "  ./start.sh optimize     # Otimiza índice"
        echo "  ./start.sh test         # Testa performance"
        exit 1
        ;;
esac
