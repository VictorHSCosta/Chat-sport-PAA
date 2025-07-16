# 🏆 Chat-sport-PAA - World Cup RAG Chatbot

Chatbot especializado em Copa do Mundo FIFA usando **LlamaIndex + Groq** (llama3-70b-8192).

## ⚡ Arquitetura Essencial

- **Backend**: FastAPI + LlamaIndex + Groq
- **Frontend**: React + Vite
- **Dados**: CSV (World Cup + Matches essenciais)
- **LLM**: Groq llama3-70b-8192

## 🚀 Configuração Rápida

### 1. Pré-requisitos
```bash
# Python 3.8+
python3 --version

# Node.js 18+
node --version
```

### 2. Setup Automático
```bash
chmod +x setup.sh start.sh
./setup.sh
```

> **Nota**: O setup criará automaticamente o arquivo `backend/.env`. 
> Edite este arquivo e configure sua GROQ_API_KEY obtida em: https://console.groq.com/keys

### 3. Executar
```bash
./start.sh
```

## 🌐 Acesso

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

Este chatbot utiliza dados históricos da Copa do Mundo FIFA (1930-2022) incluindo:
- Histórico completo de todas as Copas do Mundo
- Rankings FIFA dos países
- Estatísticas detalhadas de partidas
- Informações sobre campeões, artilheiros e recordes

## 🛠️ Tecnologias

- **Backend**: FastAPI + LangChain + FAISS + Ollama (TinyLlama)
- **Frontend**: React + Vite + Lucide Icons
- **Dados**: CSV com dados históricos da FIFA
- **RAG**: Embeddings HuggingFace + Vector Store FAISS

## 💬 Exemplos de Perguntas

- "Quantas copas o Brasil tem?"
- "Quem foi campeão da Copa de 2022?"
- "Qual país sediou mais Copas do Mundo?"
- "Quem foi o artilheiro da Copa de 2018?"
- "Quando será a próxima Copa do Mundo?"

## 📋 Pré-requisitos

- Python 3.8+
- Node.js 16+
- Ollama instalado
- 4GB RAM mínimo

## 🚀 Instalação Detalhada

Ver `QUICK_START.md` para instruções completas.
