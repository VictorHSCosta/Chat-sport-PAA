# 🚀 Guia Rápido - Chat Sport

## ⚡ Início Rápido (3 passos)

### 1. Inicie o Ollama
```bash
# Em um terminal separado
ollama serve
```

### 2. Torne o script executável
```bash
chmod +x start_simple.sh
```

### 3. Execute o projeto
```bash
# Opção 1: Script simples e robusto
./start_simple.sh

# Opção 2: Script completo com otimizações
./start.sh

# Opção 3: Apenas backend
./start_simple.sh backend

# Opção 4: Apenas frontend  
./start_simple.sh frontend
```

## 🎯 URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## 🐛 Problemas Comuns

### "pnpm: command not found"
✅ **Solução**: Use `./start_simple.sh` que usa `npm`

### "Ollama não está rodando"
✅ **Solução**: Execute `ollama serve` em outro terminal

### "Backend não responde"
✅ **Solução**: Aguarde alguns segundos, o primeiro boot demora

### "Timeout nas respostas"
✅ **Solução**: Execute `./backend/optimize_ollama.sh` para otimizar

### "Respostas muito lentas"
✅ **Solução**: Timeout aumentado para 150s, aguarde mais tempo

### "Respostas sendo cortadas"
✅ **Solução**: Sistema configurado para 300 tokens e timeout de 120s

### "Dependências não instaladas"
✅ **Solução**: Os scripts instalam automaticamente

## ⚡ Performance

- **Primeira execução**: 30-60 segundos (instala tudo)
- **Execuções seguintes**: 5-10 segundos
- **Respostas em cache**: < 0.5 segundos (saudações, copas, notícias básicas)
- **Respostas RAG**: 3-30 segundos (primeira vez, otimizado)
- **Respostas cached do RAG**: < 1 segundo (perguntas repetidas)
- **Timeout máximo**: 150 segundos (aumentado para estabilidade máxima)

## 🧪 Teste Rápido

Após iniciar, teste no frontend:
- "Oi" (cache instantâneo ⚡)
- "Copa do mundo de clubes" (cache instantâneo ⚡)
- "Mbappé Real Madrid" (cache instantâneo ⚡)
- "Quem é Pelé?" (RAG com dados completos 🤖)
- "Fale sobre Neymar" (RAG com informações detalhadas 🤖)
- "Como foi a Copa de 2022?" (RAG com dados atualizados 🤖)
- "Quais foram as transferências recentes?" (RAG com dados 2024-2025 🤖)

## 🔧 Solução de Problemas - Dados

### "Respostas em inglês"
✅ **Solução**: Execute `./backend/restart_backend.sh` para recriar índice

### "Informações desatualizadas"
✅ **Solução**: O data.txt foi atualizado com dados de 2024-2025

### "Backend não carrega dados"
✅ **Solução**: Remova a pasta `faiss_index_` e reinicie

---

**💡 Dica**: Use `./start_simple.sh` se tiver problemas com o script principal!
