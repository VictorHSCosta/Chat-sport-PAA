# -*- coding: utf-8 -*-
"""
API FastAPI com LlamaIndex para Chat sobre Copa do Mundo FIFA
Versão Essencial - Groq (llama3-70b-8192) + Dataset CSV
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import uvicorn
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# LlamaIndex imports
from llama_index.llms.groq import Groq

class QuestionRequest(BaseModel):
    message: str

class QuestionResponse(BaseModel):
    answer: str
    success: bool
    message: str = ""

class HealthResponse(BaseModel):
    status: str
    message: str

app = FastAPI(
    title="World Cup RAG API with LlamaIndex",
    description="API para chatbot sobre Copa do Mundo FIFA usando LlamaIndex + Groq",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis globais
llm = None
template = None
datasets_loaded = False

# Configuração da API Key do Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Provedor LLM - usando apenas Groq para simplicidade
LLM_PROVIDER = "groq"

def initialize_llm():
    """Inicializar o LLM Groq"""
    global llm
    try:
        if not GROQ_API_KEY:
            print("❌ GROQ_API_KEY não configurada!")
            print("💡 Configure com: export GROQ_API_KEY=sua_chave_aqui")
            return False
            
        print("🚀 Inicializando Groq LLM...")
        llm = Groq(model='llama3-70b-8192', api_key=GROQ_API_KEY)
        print("✅ Groq LLM inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar Groq LLM: {e}")
        return False

def load_csv_datasets():
    """Carregar os datasets CSV essenciais e criar o template"""
    global template, datasets_loaded
    
    try:
        print("📊 Carregando datasets CSV...")
        
        # Apenas datasets essenciais (removido ranking para simplificar)
        csv_paths = [
            "wcdataset/world_cup.csv",
            "wcdataset/matches_1930_2022.csv"
        ]
        
        dataframes = []
        loaded_files = []
        
        for csv_path in csv_paths:
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path, encoding='latin1')
                    print(f"✅ {csv_path} carregado - {len(df)} linhas")
                    dataframes.append(df)
                    loaded_files.append(csv_path)
                except Exception as e:
                    print(f"⚠️ Erro ao carregar {csv_path}: {e}")
            else:
                print(f"⚠️ Arquivo não encontrado: {csv_path}")
        
        if not dataframes:
            print("❌ Nenhum dataset foi carregado!")
            return False
        
        # Otimizar datasets para o Groq (limite de tokens)
        optimized_dataframes = []
        optimized_files = []
        
        for i, df in enumerate(dataframes):
            if "world_cup" in loaded_files[i]:
                # Manter world_cup.csv COMPLETO - é o dataset mais importante
                print(f"✅ Dataset {loaded_files[i]} mantido COMPLETO com {len(df)} linhas")
            elif "matches" in loaded_files[i]:
                # Matches: apenas 5 jogos mais importantes para economizar tokens
                df = df.head(5)
                print(f"⚽ Dataset {loaded_files[i]} otimizado para {len(df)} linhas")
            
            optimized_dataframes.append(df)
            optimized_files.append(loaded_files[i])
        
        dataframes = optimized_dataframes
        loaded_files = optimized_files
        
        # Criar template ultra-compacto para Groq
        template = "Copa do Mundo FIFA - Dados Oficiais:\n"

        # Adicionar dados de forma ultra-compacta
        for i, df in enumerate(dataframes):
            file_name = loaded_files[i].split('/')[-1]
            print(f"📄 Processando {file_name}...")
            
            if "world_cup" in file_name:
                # World Cup: formato ultra-compacto - apenas essencial
                template += "COPAS:\n"
                for _, row in df.iterrows():
                    # Apenas dados críticos: Ano|Sede|Campeão|Vice|Artilheiro
                    template += f"{row['Year']}|{row['Host']}|{row['Champion']}|{row['Runner-Up']}|{row['TopScorrer']}\n"
                    
            elif "matches" in file_name:
                # Matches: ultra limitado - apenas 3 jogos mais importantes
                template += "JOGOS:\n"
                for _, row in df.head(3).iterrows():
                    # Dados essenciais dos jogos
                    cols = df.columns.tolist()[:4]  # Apenas primeiras 4 colunas
                    values = [str(row[col]) if pd.notna(row[col]) else "-" for col in cols]
                    template += "|".join(values) + "\n"
        
        print(f"✅ Template criado com {len(template)} caracteres")
        datasets_loaded = True
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar datasets: {e}")
        return False

def initialize_system():
    """Inicializar todo o sistema"""
    print("🚀 Inicializando sistema LlamaIndex + Groq...")
    
    # 1. Inicializar LLM Groq
    if not initialize_llm():
        return False
    
    # 2. Carregar datasets
    if not load_csv_datasets():
        return False
    
    print("🎉 Sistema inicializado com sucesso!")
    return True

def get_quick_answer(message: str) -> Optional[str]:
    """Respostas rápidas para perguntas comuns"""
    message_lower = message.lower().strip()
    
    quick_answers = {
        "oi": "Olá! Sou seu assistente especializado em Copa do Mundo FIFA. Como posso ajudar?",
        "olá": "Olá! Sou seu assistente especializado em Copa do Mundo FIFA. Como posso ajudar?",
        "hello": "Hello! I'm your FIFA World Cup specialist assistant. How can I help?",
        "hi": "Oi! Sou especialista em Copa do Mundo FIFA. O que você gostaria de saber?",
        
        # Respostas rápidas específicas
        "quem ganhou a copa de 1970": "O Brasil conquistou a Copa do Mundo de 1970, realizada no México. Foi o terceiro título mundial brasileiro.",
        "artilheiro copa 1970": "Gerd Müller (Alemanha Ocidental) foi o artilheiro da Copa de 1970 com 10 gols.",
        "quantas copas o brasil tem": "O Brasil conquistou 5 Copas do Mundo: 1958 (Suécia), 1962 (Chile), 1970 (México), 1994 (EUA), 2002 (Japão/Coreia do Sul).",
        "próxima copa": "A próxima Copa do Mundo será em 2026, realizada conjuntamente pelos EUA, Canadá e México, com 48 seleções.",
    }
    
    return quick_answers.get(message_lower)

def process_question_with_llm(question: str) -> str:
    """Processar pergunta usando o LLM Groq com o template completo"""
    try:
        # Combinar template com a pergunta
        full_prompt = template + f"\n\nPERGUNTA: {question}\n\nResponda em português baseado APENAS nos dados fornecidos acima:"
        
        # Usar o LLM Groq diretamente
        response = llm.complete(full_prompt)
        
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Erro ao processar pergunta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da API"""
    success = initialize_system()
    if not success:
        print("❌ AVISO: Sistema não foi inicializado corretamente")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificar saúde da API"""
    if llm is None or not datasets_loaded:
        return HealthResponse(
            status="unhealthy",
            message="Sistema não inicializado completamente"
        )
    return HealthResponse(
        status="healthy",
        message="API funcionando corretamente com LlamaIndex + Groq"
    )

@app.post("/chat", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Endpoint principal para fazer perguntas"""
    
    if llm is None or not datasets_loaded:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")
    
    # Verificar respostas rápidas primeiro
    quick_answer = get_quick_answer(request.message)
    if quick_answer:
        return QuestionResponse(
            answer=quick_answer,
            success=True,
            message="Resposta rápida"
        )
    
    try:
        # Processar com LLM usando template completo
        answer = process_question_with_llm(request.message)
        
        return QuestionResponse(
            answer=answer,
            success=True,
            message="Resposta processada com LlamaIndex + Groq"
        )
        
    except Exception as e:
        print(f"❌ Erro no endpoint /chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "World Cup RAG API with LlamaIndex",
        "version": "4.0.0",
        "description": "Chatbot especializado em Copa do Mundo FIFA usando LlamaIndex + Groq",
        "llm_model": "llama3-70b-8192",
        "provider": "GROQ",
        "framework": "LlamaIndex",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "status": "/status",
            "docs": "/docs"
        }
    }

@app.get("/status")
async def status_check():
    """Status detalhado do sistema"""
    return {
        "system": "World Cup RAG API with LlamaIndex",
        "llm_ready": llm is not None,
        "datasets_loaded": datasets_loaded,
        "template_size": len(template) if template else 0,
        "model_config": {
            "llm_provider": "GROQ",
            "llm_model": "llama3-70b-8192",
            "framework": "LlamaIndex",
            "approach": "Direct CSV Template Injection",
            "language": "Portuguese",
            "anti_hallucination": True,
            "data_only": True
        },
        "data_sources": {
            "world_cup": "✅" if os.path.exists("wcdataset/world_cup.csv") else "❌",
            "matches": "✅" if os.path.exists("wcdataset/matches_1930_2022.csv") else "❌"
        }
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
