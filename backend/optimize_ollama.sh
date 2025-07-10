#!/bin/bash

echo "🚀 Otimizando Ollama para respostas mais rápidas..."

# Verifica se Ollama está rodando
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "❌ Ollama não está rodando!"
    echo "Execute: ollama serve"
    exit 1
fi

echo "✅ Ollama está rodando"

# Lista modelos disponíveis
echo "📋 Modelos disponíveis:"
ollama list

# Verifica se tinyllama está instalado
if ! ollama list | grep -q "tinyllama"; then
    echo "📥 Instalando tinyllama (modelo mais rápido)..."
    ollama pull tinyllama
else
    echo "✅ tinyllama já está instalado"
fi

# Testa resposta do modelo
echo "🧪 Testando velocidade do modelo..."
time ollama run tinyllama "Hello, respond in Portuguese"

echo "🔧 Configurações recomendadas para performance:"
echo "- Modelo: tinyllama (mais rápido)"
echo "- num_predict: 300 (respostas completas)"
echo "- temperature: 0.2 (mais determinístico)"
echo "- backend timeout: 120s"
echo "- frontend timeout: 150s"
echo "- llm timeout: 60s por chamada"

echo "✅ Otimização concluída!"
echo "🎯 Timeouts estendidos para respostas completas!"
