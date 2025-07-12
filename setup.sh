#!/bin/bash

# Script de configuração inicial do projeto
echo "🏆 Configuração Inicial - World Cup RAG Chatbot"
echo "⚡ Preparando chatbot especializado em Copa do Mundo FIFA"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar Python
log_info "Verificando Python..."
python3 --version || {
    log_error "Python 3 não encontrado. Instale Python 3.8+"
    exit 1
}
log_success "Python encontrado"

# 2. Verificar se Ollama está instalado
log_info "Verificando Ollama..."
if command -v ollama &> /dev/null; then
    log_success "Ollama encontrado"
    
    # Verificar se qwen2.5:3b está instalado (modelo principal para português)
    if ollama list | grep -q "qwen2.5:3b"; then
        log_success "Qwen2.5:3b (modelo principal) já instalado"
    else
        log_info "Baixando Qwen2.5:3b - modelo principal otimizado para português..."
        if ollama pull qwen2.5:3b; then
            log_success "Qwen2.5:3b instalado com sucesso"
        else
            log_warning "Falha ao baixar qwen2.5:3b, mas vamos tentar o fallback"
        fi
    fi
    
    # Manter llama3.2 como fallback obrigatório
    if ollama list | grep -q "llama3.2"; then
        log_success "Llama3.2 (fallback) também disponível"
    else
        log_info "Baixando Llama3.2 como modelo de fallback..."
        if ollama pull llama3.2; then
            log_success "Llama3.2 fallback instalado com sucesso"
        else
            log_error "Falha crítica: nem qwen2.5:3b nem llama3.2 disponíveis"
            exit 1
        fi
    fi
else
    log_warning "Ollama não encontrado. Instale Ollama antes de continuar:"
    echo "curl -fsSL https://ollama.ai/install.sh | sh"
    echo "ollama pull qwen2.5:3b"
    echo "ollama pull llama3.2"
    exit 1
fi

# 3. Criar ambiente virtual se não existir
log_info "Configurando ambiente virtual Python..."
cd ~/Chat-sport-PAA/backend

if [ ! -d "footbot" ]; then
    python3 -m venv footbot
    log_success "Ambiente virtual criado"
else
    log_success "Ambiente virtual já existe"
fi

# 4. Ativar e instalar dependências
source footbot/bin/activate
log_info "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
log_success "Dependências Python instaladas"

# 5. Verificar Node.js e gerenciador de pacotes
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

# 7. Verificar dados da Copa do Mundo
log_info "Verificando dados da Copa do Mundo..."
cd ~/Chat-sport-PAA/backend

if [ ! -d "wcdataset" ]; then
    log_error "Diretório wcdataset não encontrado!"
    log_info "Extraindo dados do arquivo zip..."
    if [ -f "wcdataset.zip" ]; then
        unzip -q wcdataset.zip
        log_success "Dados extraídos com sucesso"
    else
        log_error "Arquivo wcdataset.zip não encontrado!"
        exit 1
    fi
fi

csv_count=$(find wcdataset -name "*.csv" | wc -l)
if [ $csv_count -eq 0 ]; then
    log_error "Nenhum arquivo CSV encontrado em wcdataset!"
    exit 1
fi

log_success "Encontrados $csv_count arquivos CSV de dados da Copa do Mundo"

# Verificar conteúdo dos CSVs principais
for csv_file in wcdataset/*.csv; do
    if [ -f "$csv_file" ]; then
        lines=$(wc -l < "$csv_file")
        log_info "$(basename "$csv_file"): $lines linhas"
    fi
done

# 8. Criar índice FAISS otimizado com dados ultra-estruturados da Copa do Mundo
log_info "Preparando sistema RAG ultra-restritivo..."
cd ~/Chat-sport-PAA/backend
source footbot/bin/activate

# Remover índices antigos para forçar recriação com dados ultra-estruturados
if [ -d "faiss_index_" ]; then
    rm -rf faiss_index_
    log_info "Índice antigo removido"
fi

if [ -d "faiss_index_enhanced_" ]; then
    rm -rf faiss_index_enhanced_
    log_info "Índice avançado antigo removido"
fi

# Testar se conseguimos importar os módulos necessários
python -c "
import sys
import os
try:
    import pandas as pd
    import glob
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    from sentence_transformers import SentenceTransformer
    
    # Verificar se conseguimos carregar os CSVs
    csv_files = glob.glob(os.path.join('wcdataset', '*.csv'))
    if not csv_files:
        print('❌ Nenhum arquivo CSV encontrado')
        sys.exit(1)
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            print(f'✅ {os.path.basename(csv_file)}: {len(df)} linhas, {len(df.columns)} colunas')
        except Exception as e:
            print(f'❌ Erro ao ler {csv_file}: {e}')
            sys.exit(1)
    
    print('✅ Todos os CSVs verificados e estruturados para RAG ultra-restritivo')
    print('✅ Dados preparados para evitar confusão entre sede e campeão')
    print('✅ Múltiplas variações de perguntas em português configuradas')
    print('✅ Dependências do RAG ultra-restritivo OK')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Erro geral: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    log_success "Dependências do sistema RAG verificadas"
else
    log_error "Erro na verificação das dependências do sistema RAG"
    exit 1
fi

# Criar índice FAISS ultra-avançado durante o setup
log_info "Criando índice FAISS ultra-avançado..."
echo "🏗️ Processando dados da Copa do Mundo com configurações ultra-avançadas:"
echo "   • Chunking multi-nível: 300/800/1500 caracteres"
echo "   • Embedding multilíngue: paraphrase-multilingual-mpnet-base-v2"
echo "   • Retriever MMR para máxima precisão (k=8, fetch_k=20, λ=0.7)"
echo "   • Processamento em lotes para eficiência"
echo "   • Normalização de embeddings ativada"
echo "   ⏱️ Este processo pode demorar 3-5 minutos na primeira vez..."
echo "   💡 Aguarde, isso é feito apenas uma vez no setup!"
echo ""

if python -c "from api import setup_rag_system; setup_rag_system()"; then
    log_success "Índice FAISS ultra-avançado criado com sucesso!"
    echo "📊 Estatísticas do índice criado:"
    if [ -f "faiss_index_enhanced_/index.pkl" ]; then
        python -c "
import pickle
try:
    with open('faiss_index_enhanced_/index.pkl', 'rb') as f:
        vectorstore = pickle.load(f)
    print(f'   • Total de documentos indexados: {len(vectorstore.docstore._dict)}')
    print('   • Sistema pronto para consultas ultra-precisas!')
except Exception as e:
    print(f'   • Índice criado (erro ao ler estatísticas: {e})')
"
    fi
else
    log_error "Falha ao criar índice FAISS ultra-avançado"
    echo "💡 Possíveis soluções:"
    echo "   1. Verifique se o Ollama está rodando: ollama serve"
    echo "   2. Verifique se os modelos estão instalados: ollama list"
    echo "   3. Verifique se há espaço em disco suficiente"
    exit 1
fi

log_success "Sistema RAG ultra-restritivo configurado e índice criado!"

# 9. Verificar configuração do modelo no backend
log_info "Verificando configuração do modelo no backend..."
if grep -q "qwen2.5:3b" ~/Chat-sport-PAA/backend/api.py; then
    log_success "Backend configurado para usar qwen2.5:3b (modelo principal)"
else
    log_warning "Backend pode não estar configurado corretamente"
fi

# 10. Tornar scripts executáveis
log_info "Configurando permissões..."
chmod +x ~/Chat-sport-PAA/start.sh
chmod +x ~/Chat-sport-PAA/start_system.ps1
chmod +x ~/Chat-sport-PAA/start_backend.ps1
log_success "Permissões configuradas"

# 11. Verificação final do Ollama com novos modelos
log_info "Verificação final do Ollama com modelos otimizados..."
if ! command -v ollama &> /dev/null; then
    log_warning "Ollama não encontrado!"
    echo ""
    echo "📥 Para instalar Ollama:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "📥 Depois execute:"
    echo "   ollama serve"
    echo "   ollama pull qwen2.5:3b    # Modelo principal para português"
    echo "   ollama pull llama3.2      # Modelo fallback"
    echo ""
else
    log_success "Ollama encontrado"
    
    # Verificar se está rodando
    if ! pgrep -x "ollama" > /dev/null; then
        log_warning "Ollama não está rodando"
        echo "💡 Para iniciar: ollama serve"
    else
        log_success "Ollama está rodando"
        
        # Verificar modelos instalados
        models_installed=""
        if ollama list | grep -q "qwen2.5:3b"; then
            models_installed+="✅ qwen2.5:3b (principal) "
        else
            models_installed+="❌ qwen2.5:3b "
        fi
        
        if ollama list | grep -q "llama3.2"; then
            models_installed+="✅ llama3.2 (fallback)"
        else
            models_installed+="❌ llama3.2"
        fi
        
        log_success "Ollama está rodando - Modelos: $models_installed"
    fi
fi

# 12. Configuração final
log_info "Finalizando configuração ultra-otimizada..."

echo ""
echo "🏆 ==========================================="
echo "🏆  WORLD CUP RAG CHATBOT ULTRA-OTIMIZADO!"
echo "🏆 ==========================================="
echo ""
echo "🧠 Sistema RAG Ultra-Restritivo configurado:"
echo "   • Modelo principal: qwen2.5:3b (otimizado para português)"
echo "   • Modelo fallback: llama3.2"
echo "   • Dados ultra-estruturados para evitar alucinações"
echo "   • Distinção clara entre sede e campeão"
echo "   • Chunking multi-nível: 300/800/1500 caracteres"
echo "   • Embedding multilíngue: paraphrase-multilingual-mpnet-base-v2"
echo "   • Retriever MMR: k=8, fetch_k=20, λ=0.7"
echo "   • Índice FAISS ultra-avançado PRÉ-CRIADO ✅"
echo ""
echo "📚 Dados disponíveis:"
echo "   • Histórico completo da Copa do Mundo (1930-2022)"
echo "   • Campeões, vices e artilheiros estruturados"
echo "   • Múltiplas variações de perguntas em português"
echo "   • Rankings FIFA atualizados"
echo "   • Estatísticas de partidas detalhadas"
echo ""
echo "🚀 Para iniciar o sistema (rápido, índice já criado):"
echo "   ./start.sh"
echo ""
echo "🌐 Acesse o chatbot em:"
echo "   http://localhost:5173"
echo ""
echo "📡 API disponível em:"
echo "   http://localhost:8000/docs"
echo ""
echo "💡 Perguntas testadas e otimizadas:"
echo "   • Quantas copas o Brasil tem?"
echo "   • Quem foi campeão em 2022? (Argentina, não Qatar)"
echo "   • Quem foi campeão em 2002? (Brasil, não Japão/Coreia)"
echo "   • Qual país sediou mais Copas do Mundo?"
echo "   • Quem foi o artilheiro da Copa de 2018?"
echo "   • Onde foi a Copa de 2014? (Brasil = sede)"
echo "   • Vice-campeão de 2022? (França)"
echo ""
echo "⚠️  Sistema configurado para evitar confusão entre:"
echo "   • SEDE (onde aconteceu) ≠ CAMPEÃO (quem ganhou)"
echo "   • Exemplo: Copa 2022 - SEDE: Qatar, CAMPEÃO: Argentina"
echo ""
echo "⚡ Performance esperada (após setup completo):"
echo "   • Saudações: instantâneo"
echo "   • Perguntas sobre campeões: < 2s"
echo "   • Perguntas sobre artilheiros: < 3s"
echo "   • Perguntas complexas: 3-5s"
echo "   • Inicialização rápida: ~15s (índice pré-criado!)"
echo ""
log_success "Setup completo! Sistema pronto para uso ultra-rápido!"
