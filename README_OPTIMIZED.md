# 🚀 Chat Sport RAG - Ultra Performance Edition

Sistema de chat especializado em futebol usando **RAG (Retrieval-Augmented Generation)** com otimizações extremas de performance.

## ⚡ Performance Otimizada

- **Respostas em cache**: < 0.5 segundos ⚡
- **Perguntas sobre Pelé, Messi, Copa**: < 0.5 segundos ⚡  
- **Outras perguntas**: 3-30 segundos 🚀
- **Timeout máximo**: 150 segundos para respostas completas

## 🏗️ Arquitetura

### Backend (FastAPI + RAG)
- **LLM**: Ollama (tinyllama) ultra-otimizado
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (rápido)
- **Vector Store**: FAISS com chunks de 200 caracteres
- **Cache inteligente**: Respostas instantâneas para perguntas frequentes
- **Timeout estendido**: 120s backend + 150s frontend para respostas completas

### Frontend (React + Vite)
- Interface de chat moderna e responsiva
- Indicador de status da API em tempo real
- Timeout estendido no cliente (150 segundos)
- Sugestões de perguntas interativas

## 🚀 Instalação Rápida

### 1. Configuração Inicial
```bash
# Clone o repositório
git clone <repo-url>
cd Chat-sport-PAA

# Execute a configuração automática
chmod +x setup.sh
./setup.sh
```

### 2. Iniciar Ollama (obrigatório)
```bash
# Em um terminal separado
ollama serve

# O setup.sh já baixa o modelo, mas se precisar:
ollama pull tinyllama
```

### 3. Iniciar o Projeto
```bash
# Iniciar tudo (backend + frontend)
./start.sh

# Ou separadamente:
./start.sh backend   # Só backend
./start.sh frontend  # Só frontend
```

## 🎯 URLs Importantes

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Docs da API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Scripts Disponíveis

```bash
./start.sh              # Inicia tudo
./start.sh backend      # Só backend
./start.sh frontend     # Só frontend  
./start.sh test         # Testa performance
./start.sh optimize     # Recriar índice FAISS
```

## ⚡ Otimizações Implementadas

### Cache Inteligente
Respostas instantâneas para:
- "Pelé" / "história do Pelé"
- "Messi" 
- "Copa do Mundo"
- "Brasil"
- E muito mais...

### LLM Otimizado para Respostas Completas
- Temperatura: 0.2 (respostas consistentes)
- Máximo: 300 tokens (respostas completas)
- Stop words melhorados para evitar cortes
- Timeout: 120 segundos para processamento completo
- LLM timeout: 60 segundos por chamada

### Retrieval Otimizado
- Chunks: 300 caracteres (vs 1000 antes)
- Sobreposição: 20 caracteres
- Busca: apenas 1 documento mais relevante
- Embedding rápido: all-MiniLM-L6-v2

## 🧪 Testando Performance

```bash
# Teste automatizado de performance
./start.sh test

# Teste manual via curl
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Qual a história do Pelé?"}' \
     -w "\nTempo: %{time_total}s\n"
```

## 📊 Estrutura do Projeto

```
Chat-sport-PAA/
├── backend/                 # API FastAPI
│   ├── api.py              # API principal otimizada
│   ├── optimize_index.py   # Script de otimização FAISS
│   ├── test_performance.sh # Testes de performance
│   ├── requirements.txt    # Dependências Python
│   ├── data.txt           # Base de conhecimento
│   └── faiss_index_/      # Índice vetorial otimizado
├── Front/front-end/        # Interface React
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── hooks/         # Hooks customizados
│   │   └── services/      # API cliente
│   └── package.json       # Dependências Node.js
├── start.sh               # Script principal (NOVO!)
├── setup.sh              # Configuração inicial (NOVO!)
└── README.md             # Este arquivo
```

## 🎮 Como Usar

1. **Perguntas rápidas** (cache instantâneo):
   - "Qual a história do Pelé?"
   - "Quem é Messi?"
   - "Quantas Copas o Brasil tem?"

2. **Perguntas complexas** (RAG em 1-3s):
   - "Compare Pelé e Messi"
   - "História da Copa do Mundo de 1970"
   - "Maiores artilheiros da Champions"

3. **Interface**:
   - Digite sua pergunta
   - Clique nas sugestões
   - Veja o status da API (🟢 Online / 🔴 Offline)

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Verificar se Ollama está rodando
pgrep ollama

# Se não estiver:
ollama serve

# Recriar ambiente virtual
rm -rf backend/footbot
./setup.sh
```

### Frontend com erro
```bash
cd Front/front-end
rm -rf node_modules
pnpm install
```

### Performance baixa
```bash
# Recriar índice otimizado
./start.sh optimize

# Testar performance
./start.sh test
```

### Timeout frequente
1. Verificar se Ollama está saudável: `ollama list`
2. Usar perguntas mais simples
3. Verificar cache: perguntas sobre Pelé devem ser instantâneas

## 🔍 Debug e Análise

### Endpoint de Debug
Para análise detalhada das respostas:
```bash
curl -X POST "http://localhost:8000/chat-debug" \
     -H "Content-Type: application/json" \
     -d '{"message": "fale sobre messi"}' | jq '.'
```

### Monitoramento em Tempo Real
- **Logs do backend**: Mostram processo completo de geração
- **Status da API**: http://localhost:8000/status
- **Teste de respostas completas**: `./backend/test_complete_responses.sh`

### Verificando Respostas Incompletas
Se as respostas estão sendo cortadas:
1. Use `/chat-debug` para análise detalhada
2. Verifique logs do backend para tokens gerados
3. Aumente `num_predict` se necessário
4. Verifique se o modelo Ollama está saudável

## 🤝 Contribuindo

1. Faça um fork
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📝 Licença

MIT License - veja o arquivo LICENSE para detalhes.

---

**⚡ Versão Ultra-Performance** - Respostas em segundos, não minutos!
