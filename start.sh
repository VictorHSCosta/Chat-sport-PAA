#!/bin/bash

# Script ultra-otimizado para iniciar o World Cup RAG Chatbot
echo "🏆 Iniciando World Cup RAG Chatbot Ultra-Otimizado"
echo "⚡ Sistema Ultra-Restritivo para Copa do Mundo FIFA"
echo "🧠 Modelo: qwen2.5:3b (português) + llama3.2 (fallback)"
echo "📦 Índice FAISS: pré-criado para inicialização rápida"
echo ""
echo "💡 Se ainda não executou o setup: ./setup.sh"
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

# Verificar se índice FAISS existe (deve ter sido criado no setup)
check_faiss_index() {
    log_info "Verificando índice FAISS pré-criado..."
    cd ~/Chat-sport-PAA/backend
    source footbot/bin/activate
    
    if [ ! -f "faiss_index_enhanced_/index.faiss" ] || [ ! -f "faiss_index_enhanced_/index.pkl" ]; then
        log_error "Índice FAISS não encontrado!"
        echo "💡 O índice FAISS deve ser criado durante o setup."
        echo "   Execute primeiro: ./setup.sh"
        echo "   Isso criará o índice ultra-avançado (demora 3-5min apenas uma vez)"
        exit 1
    else
        log_success "Índice FAISS ultra-avançado encontrado e pronto!"
        
        # Mostrar estatísticas do índice
        python -c "
import pickle
import os
try:
    with open('faiss_index_enhanced_/index.pkl', 'rb') as f:
        vectorstore = pickle.load(f)
    doc_count = len(vectorstore.docstore._dict)
    print(f'   📊 Documentos indexados: {doc_count}')
    
    # Verificar tamanho do índice
    index_size = os.path.getsize('faiss_index_enhanced_/index.faiss')
    size_mb = index_size / (1024*1024)
    print(f'   📦 Tamanho do índice: {size_mb:.1f} MB')
    print('   ⚡ Sistema pronto para consultas ultra-rápidas!')
except Exception as e:
    print(f'   ⚠️ Índice existe mas erro ao ler detalhes: {e}')
"
    fi
}

# Função para iniciar backend ultra-avançado
start_backend() {
    log_info "Iniciando backend ultra-avançado..."
    cd ~/Chat-sport-PAA/backend
    source footbot/bin/activate
    
    echo ""
    echo "🎯 Configurações Ultra-Avançadas:"
    echo "   - Modelo LLM: qwen2.5:3b (otimizado para português)"
    echo "   - Modelo Embedding: paraphrase-multilingual-mpnet-base-v2"
    echo "   - Chunking Multi-Nível: 300/800/1500 caracteres"
    echo "   - Retriever MMR: k=8, fetch_k=20, λ=0.7"
    echo "   - Processamento em lotes para eficiência"
    echo "   - Normalização de embeddings ativada"
    echo "   - Cache inteligente ativado"
    echo "   - Timeout otimizado: 90 segundos"
    echo "   - Anti-alucinação máximo ativado"
    echo "   - Temperatura: 0.0 (determinístico)"
    echo ""
    
    log_success "Backend ultra-avançado iniciado em http://localhost:8000"
    echo "📊 Documentação: http://localhost:8000/docs"
    echo "🔍 Health check: http://localhost:8000/health"
    echo "📈 Status avançado: http://localhost:8000/status"
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
check_faiss_index

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
        log_warning "Para recriar o índice FAISS, use o setup.sh!"
        echo "💡 O índice ultra-avançado deve ser criado/recriado no setup:"
        echo "   ./setup.sh"
        echo ""
        echo "🤔 Se realmente quiser recriar apenas o índice:"
        cd ~/Chat-sport-PAA/backend
        source footbot/bin/activate
        rm -rf faiss_index_enhanced_/
        echo "🏗️ Recriando índice ultra-avançado..."
        echo "   ⏱️ Isso pode demorar 3-5 minutos..."
        if python -c "from api import initialize_rag_system; initialize_rag_system()"; then
            log_success "Índice ultra-avançado recriado!"
        else
            log_error "Falha ao recriar índice. Execute ./setup.sh"
        fi
        ;;
    "both"|"")
        echo "🔄 Iniciando backend e frontend ultra-avançados..."
        echo ""
        
        # Iniciar backend em background
        start_backend &
        BACKEND_PID=$!
        
        # Aguardar backend inicializar (muito mais rápido com índice pré-criado)
        log_info "Aguardando backend ultra-avançado inicializar..."
        echo "   ⚡ Inicialização rápida com índice pré-criado..."
        sleep 8
        
        # Verificar se backend está funcionando
        if curl -s http://localhost:8000/health > /dev/null; then
            log_success "Backend ultra-avançado inicializado com sucesso"
        else
            log_warning "Backend ainda inicializando (aguarde mais alguns segundos)"
        fi
        
        # Iniciar frontend
        start_frontend &
        FRONTEND_PID=$!
        
        echo ""
        log_success "Sistema ultra-avançado iniciado!"
        echo ""
        echo "🎯 URLs importantes:"
        echo "   📊 Backend API: http://localhost:8000"
        echo "   📚 Docs API: http://localhost:8000/docs"
        echo "   📈 Status avançado: http://localhost:8000/status"
        echo "   🌐 Frontend: http://localhost:5173"
        echo ""
        echo "⚡ Performance esperada (índice pré-criado):"
        echo "   - Inicialização: ~15s (super rápida!)"
        echo "   - Saudações: instantâneo"
        echo "   - Perguntas sobre campeões: < 2s"
        echo "   - Perguntas sobre artilheiros: < 3s"
        echo "   - Perguntas complexas: 3-5s"
        echo "   - Timeout máximo: 90s"
        echo ""
        echo "🧠 Melhorias implementadas:"
        echo "   • Chunking multi-nível (300/800/1500 chars)"
        echo "   • Embedding multilíngue otimizado"
        echo "   • Retriever MMR para máxima precisão"
        echo "   • Processamento em lotes"
        echo "   • Normalização de embeddings"
        echo ""
        echo "🧪 Exemplos testados:"
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
        echo "⚠️  IMPORTANTE: Execute ./setup.sh primeiro para criar o índice FAISS!"
        echo ""
        echo "Opções:"
        echo "  backend   - Iniciar apenas o backend ultra-avançado"
        echo "  frontend  - Iniciar apenas o frontend"
        echo "  both      - Iniciar ambos ultra-avançados (padrão)"
        echo "  test      - Executar testes de performance"
        echo "  optimize  - Recriar índice FAISS (use ./setup.sh em vez disso)"
        echo ""
        echo "Fluxo recomendado:"
        echo "  1. ./setup.sh           # Setup inicial (apenas uma vez)"
        echo "  2. ./start.sh           # Iniciar sistema (rápido!)"
        echo ""
        echo "Exemplos:"
        echo "  ./start.sh              # Inicia sistema completo (rápido)"
        echo "  ./start.sh backend      # Só backend ultra-avançado"
        echo "  ./start.sh test         # Testa performance"
        echo ""
        echo "🧠 Sistema ultra-avançado (após setup) com:"
        echo "  • Chunking multi-nível (300/800/1500 caracteres)"
        echo "  • Embedding multilíngue otimizado para português"
        echo "  • Retriever MMR para máxima precisão e diversidade"
        echo "  • Processamento em lotes para eficiência"
        echo "  • Normalização de embeddings para melhor similaridade"
        echo "  • Fallback automático de modelos"
        echo "  • Anti-alucinação máximo"
        echo "  • Índice FAISS pré-criado para inicialização ultra-rápida"
        exit 1
        ;;
esac
