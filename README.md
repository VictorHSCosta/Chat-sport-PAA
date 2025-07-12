# 🏆 World Cup RAG Chatbot

Um chatbot inteligente especializado em Copa do Mundo FIFA usando RAG (Retrieval-Augmented Generation) com Ollama e dados históricos.

## ⚡ Início Rápido

```bash
# 1. Configure o ambiente
./setup.sh

# 2. Inicie o sistema
./start.sh

# 3. Acesse o chatbot
# Frontend: http://localhost:5173
# API: http://localhost:8000/docs
```

## 📚 Sobre o Projeto

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
