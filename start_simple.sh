#!/bin/bash

# Script simples e robusto para iniciar o Chat Sport
echo "🚀 Chat Sport - Sistema RAG"
echo ""

# Verificar Ollama
echo "🔍 Verificando Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "❌ Ollama não está rodando!"
    echo "💡 Execute em outro terminal: ollama serve"
    exit 1
fi
echo "✅ Ollama OK"

# Verificar modelo
echo "🔍 Verificando modelo tinyllama..."
if ! ollama list | grep -q "tinyllama"; then
    echo "📥 Baixando tinyllama..."
    ollama pull tinyllama
fi
echo "✅ Modelo OK"

# Função para backend
start_backend() {
    echo "🐍 Iniciando backend..."
    cd ~/Chat-sport-PAA/backend || exit 1
    
    # Criar ambiente virtual se não existir
    if [ ! -d "footbot" ]; then
        echo "📦 Criando ambiente virtual..."
        python3 -m venv footbot
    fi
    
    source footbot/bin/activate
    
    # Instalar dependências se necessário
    if [ ! -f ".deps_installed" ]; then
        echo "📦 Instalando dependências..."
        pip install -r requirements.txt
        touch .deps_installed
    fi
    
    echo "✅ Backend iniciado em http://localhost:8000"
    python api.py
}

# Função para frontend
start_frontend() {
    echo "⚛️ Iniciando frontend..."
    cd ~/Chat-sport-PAA/Front/front-end || exit 1
    
    # Instalar dependências se necessário
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependências..."
        npm install
    fi
    
    echo "✅ Frontend iniciado em http://localhost:5173"
    npm run dev
}

# Menu de opções
case "$1" in
    "backend"|"b")
        start_backend
        ;;
    "frontend"|"f")
        start_frontend
        ;;
    *)
        echo "🔄 Iniciando ambos os serviços..."
        echo ""
        
        # Backend em background
        start_backend &
        BACKEND_PID=$!
        
        # Aguardar backend
        echo "⏳ Aguardando backend..."
        sleep 5
        
        # Frontend
        start_frontend &
        FRONTEND_PID=$!
        
        echo ""
        echo "✅ Serviços iniciados!"
        echo "📊 Backend: http://localhost:8000"
        echo "🌐 Frontend: http://localhost:5173"
        echo ""
        echo "Pressione Ctrl+C para parar"
        
        # Aguardar
        trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' INT
        wait $BACKEND_PID $FRONTEND_PID
        ;;
esac
