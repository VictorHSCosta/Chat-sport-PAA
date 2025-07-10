#!/bin/bash

echo "🔍 Testando respostas completas do sistema..."

# Função para testar uma pergunta
test_question() {
    local question="$1"
    local endpoint="$2"
    
    echo -e "\n📝 Testando: '$question'"
    echo "🔗 Endpoint: $endpoint"
    echo "⏱️ Tempo de resposta:"
    
    time curl -s -X POST "http://localhost:8000$endpoint" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$question\"}" | \
        jq -r '.answer' | \
        head -c 500
    
    echo -e "\n---"
}

# Verifica se backend está rodando
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend não está rodando!"
    exit 1
fi

echo "✅ Backend está rodando"
echo "📊 Status do sistema:"
curl -s http://localhost:8000/status | jq '.model_config'

echo -e "\n🧪 Comparando respostas normais vs debug..."

# Teste 1: Endpoint normal
test_question "fale sobre o messi" "/chat"

# Teste 2: Endpoint debug (verbose)
test_question "fale sobre o messi" "/chat-debug"

# Teste 3: Pergunta mais específica
test_question "qual a biografia completa de neymar?" "/chat-debug"

# Teste 4: Pergunta sobre história
test_question "como foi a copa do mundo de 2022?" "/chat-debug"

echo -e "\n✅ Teste concluído!"
echo "💡 Use /chat-debug para análise detalhada das respostas"
echo "📊 Verifique os logs do backend para debug completo"
