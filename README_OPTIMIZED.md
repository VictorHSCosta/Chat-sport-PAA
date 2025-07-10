# 🚀 Chat Sport RAG - Ultra Performance Edition

Sistema de chat especializado em futebol usando **RAG (Retrieval-Augmented Generation)** com otimizações extremas de performance.

## ⚡ Performance Otimizada

- **Respostas em cache**: < 0.5 segundos ⚡
- **Perguntas sobre Pelé, Messi, Copa**: < 0.5 segundos ⚡  
- **Outras perguntas**: 1-3 segundos 🚀
- **Timeout máximo**: 3 segundos com fallback inteligente

## 🏗️ Arquitetura

### Backend (FastAPI + RAG)
- **LLM**: Ollama (tinyllama) ultra-otimizado
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (rápido)
- **Vector Store**: FAISS com chunks de 300 caracteres
- **Cache inteligente**: Respostas instantâneas para perguntas frequentes
- **Timeout agressivo**: 3 segundos com fallback

### Frontend (React + Vite)
- Interface de chat moderna e responsiva
- Indicador de status da API em tempo real
- Timeout otimizado no cliente (15 segundos)
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

### LLM Ultra-Otimizado
- Temperatura: 0.1 (respostas diretas)
- Máximo: 30 tokens
- Stop words para evitar respostas longas
- Timeout: 3 segundos

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
