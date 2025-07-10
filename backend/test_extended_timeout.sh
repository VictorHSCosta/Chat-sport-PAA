#!/bin/bash

echo "⏰ Testando timeouts aumentados do sistema..."

# Verifica se backend está rodando
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend não está rodando!"
    echo "Execute: ./start_simple.sh backend"
    exit 1
fi

echo "✅ Backend está rodando"

# Mostra configurações atuais de timeout
echo "⚙️ Configurações de timeout:"
curl -s http://localhost:8000/status | jq '.model_config | {timeout, llm_timeout, num_predict}'

echo -e "\n🧪 Testando pergunta que pode demorar..."

# Pergunta complexa que pode demorar
echo "📝 Pergunta: 'Faça uma análise completa da carreira de Neymar, incluindo Santos, Barcelona, PSG e Al-Hilal'"

echo "⏱️ Iniciando teste (timeout máximo: 150s)..."
start_time=$(date +%s)

curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Faça uma análise completa da carreira de Neymar, incluindo Santos, Barcelona, PSG e Al-Hilal"}' | \
  jq -r '.answer'

end_time=$(date +%s)
duration=$((end_time - start_time))

echo -e "\n⏰ Tempo total: ${duration}s"

if [ $duration -lt 150 ]; then
    echo "✅ Resposta entregue dentro do timeout!"
else
    echo "⚠️ Resposta demorou mais que o timeout esperado"
fi

echo -e "\n📊 Configurações aplicadas:"
echo "- Backend timeout: 120s"
echo "- Frontend timeout: 150s"
echo "- LLM timeout: 60s"
echo "- Tokens máximos: 300"

echo -e "\n💡 Se ainda houver timeouts, considere:"
echo "1. Verificar se Ollama está saudável: ollama list"
echo "2. Usar perguntas mais simples temporariamente"
echo "3. Reiniciar o Ollama: pkill ollama && ollama serve"
