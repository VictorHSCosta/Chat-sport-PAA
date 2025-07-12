# 🏆 World Cup RAG Chatbot - Fluxo de Setup e Start

## Visão Geral

O sistema agora está otimizado com **separação clara** entre setup e execução:

- **`setup.sh`**: Configura tudo e **cria o índice FAISS** (demora 3-5 minutos, só uma vez)
- **`start.sh`**: Inicia os serviços rapidamente usando o índice já criado (~15 segundos)

## 🚀 Fluxo Recomendado

### 1. Setup Inicial (Apenas uma vez)
```bash
./setup.sh
```

**O que faz:**
- ✅ Verifica Python, Node.js, Ollama
- ✅ Baixa modelos LLM (qwen2.5:3b + llama3.2)
- ✅ Instala dependências Python e Node.js
- ✅ **Cria o índice FAISS ultra-avançado** (3-5 minutos)
- ✅ Configura sistema RAG com dados da Copa do Mundo

### 2. Iniciar Sistema (Sempre rápido)
```bash
./start.sh
```

**O que faz:**
- ✅ Verifica se o índice FAISS existe
- ✅ Inicia backend e frontend rapidamente (~15s)
- ✅ Sistema pronto para uso em segundos!

## 📊 Performance Esperada

### Após Setup Completo:
- **Inicialização**: ~15 segundos (super rápida!)
- **Saudações**: instantâneo
- **Perguntas sobre campeões**: < 2s
- **Perguntas sobre artilheiros**: < 3s
- **Perguntas complexas**: 3-5s

## 🔧 Comandos Úteis

```bash
# Setup inicial (só uma vez)
./setup.sh

# Iniciar sistema completo
./start.sh

# Iniciar apenas backend
./start.sh backend

# Iniciar apenas frontend
./start.sh frontend

# Testes de performance
./start.sh test

# Se precisar recriar índice
./setup.sh  # Recomendado
# ou
./start.sh optimize  # Alternativa
```

## 🧠 Configurações Ultra-Avançadas

### Sistema RAG:
- **Chunking multi-nível**: 300/800/1500 caracteres
- **Embedding**: paraphrase-multilingual-mpnet-base-v2
- **Retriever MMR**: k=8, fetch_k=20, λ=0.7
- **Processamento**: em lotes para eficiência
- **Normalização**: embeddings otimizados

### Modelos LLM:
- **Principal**: qwen2.5:3b (otimizado para português)
- **Fallback**: llama3.2 (automático se qwen falhar)
- **Temperatura**: 0.0 (determinístico, anti-alucinação)

## ⚠️ Importantes

1. **Sempre execute `setup.sh` primeiro** - cria o índice FAISS
2. **`start.sh` não recria o índice** - apenas usa o existente
3. **Para recriar índice**: execute `setup.sh` novamente
4. **Ollama deve estar rodando**: `ollama serve` em terminal separado

## 🎯 URLs do Sistema

- **Frontend**: http://localhost:5173
- **API Backend**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Status Avançado**: http://localhost:8000/status

## 💡 Exemplos de Perguntas Testadas

- "Quantas copas o Brasil tem?"
- "Quem foi campeão em 2022?" → Argentina (não Qatar)
- "Quem foi campeão em 2002?" → Brasil (não Japão/Coreia) 
- "Onde foi a Copa de 2014?" → Brasil (sede)
- "Vice-campeão de 2022?" → França
- "Quem foi o artilheiro da Copa de 2018?"

## 🔍 Distinção Importante

O sistema está configurado para **nunca confundir**:
- **SEDE** (onde aconteceu) ≠ **CAMPEÃO** (quem ganhou)
- Exemplo: Copa 2022 → **SEDE**: Qatar, **CAMPEÃO**: Argentina
