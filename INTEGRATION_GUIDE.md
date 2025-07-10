# Chat Sport - Sistema RAG para Futebol 🏈⚽

Sistema completo de chat sobre futebol usando RAG (Retrieval-Augmented Generation) com FastAPI e React.

## 🏗️ Arquitetura

- **Backend**: FastAPI + LangChain + FAISS + Ollama
- **Frontend**: React + Vite
- **AI**: Sistema RAG com embeddings HuggingFace e LLM Ollama

## 🚀 Como Executar

### 1. Backend (FastAPI)

```bash
# Navegar para o diretório backend
cd Chat-sport-PAA/backend

# Ativar ambiente virtual
source footbot/bin/activate

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Iniciar servidor
python api.py
```

O backend estará disponível em: `http://localhost:8000`

### 2. Frontend (React)

```bash
# Navegar para o diretório frontend
cd Chat-sport-PAA/Front/front-end

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em: `http://localhost:5173`

## 📋 Pré-requisitos

### Backend
- Python 3.9+
- Ollama instalado e rodando
- Modelo `tinyllama` baixado (`ollama pull tinyllama`)

### Frontend
- Node.js 16+
- npm ou yarn

## 🔧 Configuração

### 1. Verificar Ollama
```bash
# Verificar se Ollama está rodando
ollama serve

# Baixar modelo (em outro terminal)
ollama pull tinyllama

# Testar modelo
ollama run tinyllama "Hello"
```

### 2. Verificar Backend
```bash
# Testar health check
curl http://localhost:8000/health

# Testar chat
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Quais são os principais times do Brasil?"}'
```

### 3. Verificar Frontend
- Abra `http://localhost:5173`
- Verifique se o status da API aparece como "Online" no header
- Teste enviando uma mensagem

## 📊 Endpoints da API

- `GET /` - Informações da API
- `GET /health` - Status de saúde
- `POST /chat` - Enviar mensagem para o chat
- `GET /docs` - Documentação Swagger

## 🐛 Solução de Problemas

### Backend não inicia
1. Verificar se o ambiente virtual está ativo
2. Verificar se todas as dependências estão instaladas
3. Verificar se o Ollama está rodando
4. Verificar logs no terminal

### Frontend não conecta
1. Verificar se o backend está rodando em `localhost:8000`
2. Verificar console do navegador para erros
3. Verificar se CORS está configurado corretamente

### Sistema RAG não funciona
1. Verificar se o arquivo `data.txt` existe
2. Verificar se o índice FAISS foi criado
3. Verificar logs de debug no terminal do backend

## 📁 Estrutura do Projeto

```
Chat-sport-PAA/
├── backend/
│   ├── api.py                 # API principal
│   ├── data.txt              # Dados de futebol
│   ├── faiss_index_/         # Índice FAISS
│   ├── footbot/              # Ambiente virtual
│   └── requirements.txt      # Dependências Python
└── Front/front-end/
    ├── src/
    │   ├── components/       # Componentes React
    │   ├── hooks/           # Hooks customizados
    │   ├── services/        # Serviços da API
    │   └── App.jsx          # Componente principal
    ├── package.json         # Dependências Node.js
    └── vite.config.js      # Configuração Vite
```

## 🚀 Funcionalidades

- ✅ Chat em tempo real
- ✅ Sistema RAG para perguntas sobre futebol
- ✅ Interface moderna e responsiva
- ✅ Indicador de status da API
- ✅ Tratamento de erros
- ✅ Timeout em requisições
- ✅ Verificação automática de saúde da API

## 🔄 Próximos Passos

- [ ] Adicionar histórico de conversas
- [ ] Melhorar interface de usuário
- [ ] Adicionar mais dados de futebol
- [ ] Implementar autenticação
- [ ] Adicionar testes automatizados
