#!/bin/bash

# Script ultra-otimizado para iniciar o World Cup RAG Chatbot
echo "🏆 Iniciando World Cup RAG Chatbot Ultra-Otimizado"
echo "⚡ Sistema Ultra-Restritivo para Copa do Mundo FIFA"
echo "🧠 Modelo: qwen2.5:3b (português) + llama3.2 (fallback)"
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

# Verificar se o modelo qwen2.5:3b está disponível (modelo principal para português)
log_info "Verificando modelo qwen2.5:3b (principal)..."
qwen_available=false
if ollama list | grep -q "qwen2.5:3b"; then
    log_success "Modelo qwen2.5:3b encontrado (otimizado para português)"
    qwen_available=true
else
    log_warning "Modelo qwen2.5:3b não encontrado"
    echo "📥 Baixando modelo qwen2.5:3b (otimizado para português)..."
    if ollama pull qwen2.5:3b; then
        log_success "Modelo qwen2.5:3b baixado com sucesso"
        qwen_available=true
    else
        log_warning "Erro ao baixar qwen2.5:3b. Verificando fallback..."
    fi
fi

# Verificar llama3.2 como fallback obrigatório
log_info "Verificando modelo llama3.2 (fallback)..."
llama_available=false
if ollama list | grep -q "llama3.2"; then
    log_success "Modelo llama3.2 disponível como fallback"
    llama_available=true
else
    log_warning "Modelo llama3.2 não encontrado"
    echo "📥 Baixando modelo llama3.2 como fallback..."
    if ollama pull llama3.2; then
        log_success "Modelo llama3.2 baixado com sucesso"
        llama_available=true
    else
        log_error "Falha ao baixar modelo llama3.2"
    fi
fi

# Verificar se pelo menos um modelo está disponível
if [ "$qwen_available" = false ] && [ "$llama_available" = false ]; then
    log_error "Nenhum modelo compatível disponível!"
    exit 1
fi

# Informar qual modelo será usado
if [ "$qwen_available" = true ]; then
    log_success "Sistema usará qwen2.5:3b como modelo principal"
elif [ "$llama_available" = true ]; then
    log_warning "Sistema usará llama3.2 como fallback (qwen2.5:3b indisponível)"
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

# Otimizar índice FAISS ultra-restritivo se necessário
optimize_index() {
    log_info "Verificando índice FAISS ultra-restritivo..."
    cd ~/Chat-sport-PAA/backend
    source footbot/bin/activate
    
    if [ ! -f "faiss_index_/index.faiss" ]; then
        log_warning "Índice FAISS não encontrado"
        echo "🏗️ Criando índice FAISS ultra-restritivo para Copa do Mundo..."
        echo "   • Dados estruturados para evitar confusão sede/campeão"
        echo "   • Múltiplas variações de perguntas em português"
        echo "   • Chunks de 600 caracteres com overlap 50"
        if python -c "from api import initialize_rag_system; initialize_rag_system()"; then
            log_success "Índice FAISS ultra-restritivo criado"
        else
            log_error "Falha ao criar índice FAISS"
            exit 1
        fi
    else
        # Verificar se o índice é antigo (mais de 1 dia)
        if find "faiss_index_/index.faiss" -mtime +1 2>/dev/null | grep -q .; then
            log_warning "Índice FAISS é antigo, recriando versão ultra-restritiva..."
            rm -rf faiss_index_/
            python -c "from api import initialize_rag_system; initialize_rag_system()"
        else
            log_success "Índice FAISS ultra-restritivo está atualizado"
        fi
    fi
}

# Função para iniciar backend ultra-otimizado
start_backend() {
    log_info "Iniciando backend ultra-otimizado..."
    cd ~/Chat-sport-PAA/backend
    source footbot/bin/activate
    
    echo ""
    echo "🎯 Configurações Ultra-Restritivas:"
    echo "   - Modelo principal: qwen2.5:3b (otimizado para português)"
    echo "   - Modelo fallback: llama3.2"
    echo "   - Dados ultra-estruturados (sede ≠ campeão)"
    echo "   - Cache inteligente ativado"
    echo "   - Respostas rápidas para Copa do Mundo"
    echo "   - Timeout otimizado: 60 segundos"
    echo "   - Chunks ultra-focados: 600 caracteres"
    echo "   - Retriever: k=3, threshold=0.2"
    echo "   - Anti-alucinação máximo ativado"
    echo "   - Temperatura: 0.0 (determinístico)"
    echo ""
    
    log_success "Backend ultra-restritivo iniciado em http://localhost:8000"
    echo "📊 Documentação: http://localhost:8000/docs"
    echo "🔍 Health check: http://localhost:8000/health"
    echo "📈 Status: http://localhost:8000/status"
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
        log_info "Recriando índice FAISS ultra-restritivo..."
        cd ~/Chat-sport-PAA/backend
        source footbot/bin/activate
        rm -rf faiss_index_/
        python -c "from api import initialize_rag_system; initialize_rag_system()"
        log_success "Índice ultra-restritivo recriado!"
        ;;
    "both"|"")
        echo "🔄 Iniciando backend e frontend ultra-otimizados..."
        echo ""
        
        # Iniciar backend em background
        start_backend &
        BACKEND_PID=$!
        
        # Aguardar backend inicializar
        log_info "Aguardando backend ultra-restritivo inicializar..."
        sleep 10
        
        # Verificar se backend está funcionando
        if curl -s http://localhost:8000/health > /dev/null; then
            log_success "Backend ultra-restritivo inicializado com sucesso"
        else
            log_warning "Backend pode estar demorando para inicializar (normal na primeira vez)"
        fi
        
        # Iniciar frontend
        start_frontend &
        FRONTEND_PID=$!
        
        echo ""
        log_success "Sistema ultra-otimizado iniciado!"
        echo ""
        echo "🎯 URLs importantes:"
        echo "   📊 Backend API: http://localhost:8000"
        echo "   📚 Docs API: http://localhost:8000/docs"
        echo "   📈 Status: http://localhost:8000/status"
        echo "   🌐 Frontend: http://localhost:5173"
        echo ""
        echo "⚡ Performance esperada (sistema ultra-restritivo):"
        echo "   - Saudações: instantâneo"
        echo "   - Perguntas sobre campeões: < 1s"
        echo "   - Perguntas sobre artilheiros: < 2s"
        echo "   - Outras perguntas: 2-4s"
        echo "   - Timeout máximo: 60s"
        echo ""
        echo "🧠 Exemplos testados:"
        echo "   'Quem foi campeão em 2022?' → Argentina (não Qatar)"
        echo "   'Quem foi campeão em 2002?' → Brasil (não Japão)"
        echo "   'Onde foi a Copa de 2014?' → Brasil (sede)"
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
        echo "  backend   - Iniciar apenas o backend ultra-restritivo"
        echo "  frontend  - Iniciar apenas o frontend"
        echo "  both      - Iniciar ambos ultra-otimizados (padrão)"
        echo "  test      - Executar testes de performance"
        echo "  optimize  - Recriar índice FAISS ultra-restritivo"
        echo ""
        echo "Exemplos:"
        echo "  ./start.sh              # Inicia sistema completo"
        echo "  ./start.sh backend      # Só backend ultra-restritivo"
        echo "  ./start.sh optimize     # Recria índice ultra-restritivo"
        echo "  ./start.sh test         # Testa performance"
        echo ""
        echo "🧠 Sistema ultra-restritivo configurado para:"
        echo "  • Evitar confusão entre sede e campeão"
        echo "  • Respostas factuais sem alucinações"
        echo "  • Modelo qwen2.5:3b otimizado para português"
        echo "  • Fallback llama3.2 se necessário"
        exit 1
        ;;
esac
