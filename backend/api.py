from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_core.documents import Document
import uvicorn
import os
import json
import asyncio

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
    title="Chat Sport RAG API",
    description="API para sistema de chat esportivo com RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qa_system = None
embeddings = None
response_cache = {}

QUICK_ANSWERS = {
    "oi": "Olá! Como posso ajudar com suas perguntas sobre futebol?",
    "olá": "Olá! Como posso ajudar com suas perguntas sobre futebol?",
    "ola": "Olá! Como posso ajudar com suas perguntas sobre futebol?",
    "hello": "Olá! Como posso ajudar com suas perguntas sobre futebol?",
    "quantas copas o brasil tem": "O Brasil tem 5 títulos de Copa do Mundo: 1958, 1962, 1970, 1994, 2002.",
    "quantas copas brasil tem": "O Brasil tem 5 títulos de Copa do Mundo: 1958, 1962, 1970, 1994, 2002.",
    "copa do mundo de clubes": "A Copa do Mundo de Clubes da FIFA é disputada anualmente entre os campeões continentais. O formato expandido com 32 times começará em 2025.",
    "mundial de clubes": "A Copa do Mundo de Clubes da FIFA é disputada anualmente entre os campeões continentais. O formato expandido com 32 times começará em 2025.",
    "quando é a próxima copa": "A próxima Copa do Mundo FIFA será em 2026, realizada conjuntamente por EUA, Canadá e México.",
    "copa 2026": "A Copa do Mundo de 2026 será realizada nos EUA, Canadá e México, com 48 seleções participantes.",
    "real madrid campeão": "O Real Madrid conquistou a Champions League 2023-24, sendo o clube com mais títulos da competição (15 títulos).",
    "champions league": "A Champions League é a principal competição de clubes da Europa. O Real Madrid é o maior campeão com 15 títulos.",
    "libertadores": "A Copa Libertadores é a principal competição de clubes da América do Sul, equivalente à Champions League europeia.",
    "brasileirão": "O Campeonato Brasileiro (Brasileirão) é a principal competição nacional do Brasil, disputada por 20 clubes.",
    "messi barcelona": "Lionel Messi deixou o Barcelona em 2021 e atualmente joga pelo Inter Miami na MLS americana.",
    "neymar psg": "Neymar deixou o PSG em 2023 e se transferiu para o Al-Hilal da Arábia Saudita.",
    "mbappé real madrid": "Kylian Mbappé se transferiu para o Real Madrid em 2024, após deixar o PSG."
}

def get_quick_answer(message):
    message_lower = message.lower().strip()
    
    # Cache MUITO restritivo - apenas saudações e pergunta exata sobre copas
    if message_lower in QUICK_ANSWERS:
        return QUICK_ANSWERS[message_lower]
    
    return None

def initialize_rag_system():
    global qa_system, embeddings
    
    print("🚀 [DEBUG] Iniciando sistema RAG...")
    
    try:
        # Carrega o arquivo de dados
        def load_text_file(path):
            print(f"📁 [DEBUG] Tentando carregar arquivo: {path}")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Arquivo {path} não encontrado")
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"📄 [DEBUG] Arquivo carregado, tamanho: {len(text)} caracteres")
            return [Document(page_content=text, metadata={"source": path})]

        faiss_index_path = "faiss_index_"
        if os.path.exists(f"{faiss_index_path}/index.faiss"):
            print("🔄 [DEBUG] Carregando índice FAISS existente...")
            embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
            model_kwargs = {"device": "cpu"}
            print(f"🧠 [DEBUG] Carregando embeddings: {embedding_model_name}")
            embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name, model_kwargs=model_kwargs)
            print("📚 [DEBUG] Carregando vectorstore...")
            persisted_vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
            print("✅ [DEBUG] Vectorstore carregado!")
        else:
            print("🆕 [DEBUG] Criando novo índice FAISS...")
            documents = load_text_file("data.txt")
            
            print("✂️ [DEBUG] Dividindo texto em chunks...")
            text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=15, separator="\n")
            docs = text_splitter.split_documents(documents)
            print(f"📝 [DEBUG] Criados {len(docs)} chunks")
            
            embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
            model_kwargs = {"device": "cpu"}
            print(f"🧠 [DEBUG] Carregando embeddings: {embedding_model_name}")
            embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name, model_kwargs=model_kwargs)
            
            print("🏗️ [DEBUG] Criando vectorstore...")
            persisted_vectorstore = FAISS.from_documents(docs, embeddings)
            print("💾 [DEBUG] Salvando vectorstore...")
            persisted_vectorstore.save_local(faiss_index_path)
            print("✅ [DEBUG] Vectorstore criado e salvo!")
        
        print("🤖 [DEBUG] Inicializando modelo LLM...")
        llm = Ollama(
            model="tinyllama",
            temperature=0.2,
            top_p=0.8,
            num_predict=300,
            repeat_penalty=1.05,
            stop=["Human:", "Assistant:", "\n\nHuman:", "\n\nAssistant:", "Pergunta:", "Resposta:"],
            timeout=60
        )
        print("✅ [DEBUG] LLM inicializado com tokens aumentados e timeout de 60s!")
        
        print("🧪 [DEBUG] Testando conexão com Ollama...")
        try:
            test_response = llm.invoke("Hello")
            print(f"✅ [DEBUG] Teste do Ollama bem-sucedido: {test_response[:50]}...")
        except Exception as ollama_error:
            print(f"❌ [DEBUG] Erro no teste do Ollama: {ollama_error}")
            raise ollama_error
        
        print("🔗 [DEBUG] Criando sistema de perguntas e respostas...")
        retriever = persisted_vectorstore.as_retriever(search_kwargs={"k": 2})
        
        # Template personalizado em português - otimizado para respostas completas
        template = """Com base nas informações sobre futebol, responda em português brasileiro de forma completa:

{context}

Pergunta: {question}
Resposta completa:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        qa_system = RetrievalQA.from_chain_type(
            llm=llm, 
            chain_type="stuff", 
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )
        print("✅ [DEBUG] QA System criado com prompt em português!")
        
        print("🎉 [DEBUG] Sistema RAG inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ [DEBUG] Erro ao inicializar sistema RAG: {str(e)}")
        import traceback
        print(f"❌ [DEBUG] Traceback completo: {traceback.format_exc()}")
        return False

@app.on_event("startup")
async def startup_event():
    success = initialize_rag_system()
    if not success:
        print("AVISO: Sistema RAG não foi inicializado corretamente")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    if qa_system is None:
        return HealthResponse(
            status="unhealthy",
            message="Sistema RAG não inicializado"
        )
    return HealthResponse(
        status="healthy",
        message="API funcionando corretamente"
    )

@app.post("/chat", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    
    print(f"🔥 [DEBUG] Recebida requisição: {request.message}")
    
    if qa_system is None:
        print("❌ [DEBUG] Sistema RAG não está inicializado!")
        raise HTTPException(
            status_code=500,
            detail="Sistema RAG não inicializado. Verifique os logs do servidor."
        )
    
    print("✅ [DEBUG] Sistema RAG está inicializado")
    
    if not request.message.strip():
        print("❌ [DEBUG] Mensagem está vazia")
        raise HTTPException(
            status_code=400,
            detail="Pergunta não pode estar vazia"
        )
    
    print(f"📝 [DEBUG] Processando pergunta: {request.message}")
    
    quick_answer = get_quick_answer(request.message)
    if quick_answer:
        print("⚡ [DEBUG] Resposta rápida encontrada!")
        return QuestionResponse(
            answer=f"⚡ **Resposta Rápida**: {quick_answer}",
            success=True,
            message="Resposta rápida do cache"
        )
    
    cache_key = request.message.lower().strip()
    if cache_key in response_cache:
        print("💾 [DEBUG] Resposta encontrada no cache!")
        return QuestionResponse(
            answer=f"💾 **Do Cache**: {response_cache[cache_key]}",
            success=True,
            message="Resposta do cache"
        )
    
    try:
        print("🔍 [DEBUG] Iniciando invoke do qa_system...")
        
        import asyncio
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        start_time = time.time()
        print(f"⏰ [DEBUG] Tempo inicial: {start_time}")
        
        def run_qa_system():
            return qa_system.invoke({"query": request.message})
        
        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_qa_system)
            try:
                response = future.result(timeout=120)
            except FutureTimeoutError:
                return QuestionResponse(
                    answer="Sua pergunta está demorando para processar. O sistema pode estar sobrecarregado. Tente novamente em alguns instantes.",
                    success=True,
                    message="Timeout - sistema sobrecarregado (120s)"
                )
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏰ [DEBUG] Tempo final: {end_time}, duração: {duration:.2f}s")
        print(f"✅ [DEBUG] Resposta recebida (tipo: {type(response)})")
        print(f"📝 [DEBUG] Resposta completa: {response}")
        
        if isinstance(response, dict) and "result" in response:
            answer = response["result"]
        elif isinstance(response, str):
            answer = response
        else:
            print(f"⚠️ [DEBUG] Formato de resposta inesperado: {type(response)}")
            answer = str(response)
        
        # Validação de resposta completa
        if len(answer.strip()) < 20:
            print(f"⚠️ [DEBUG] Resposta muito curta ({len(answer)} chars), pode estar incompleta")
        
        # Remove possíveis artifacts do template
        answer = answer.replace("Responda de forma DIRETA e CONCISA em português brasileiro:", "").strip()
        answer = answer.replace("Baseado nas informações sobre futebol abaixo:", "").strip()
        
        print(f"📤 [DEBUG] Enviando resposta limpa ({len(answer)} chars): {answer[:200]}...")
        
        # Salva resposta no cache automático para acelerar futuras consultas
        cache_key = request.message.lower().strip()
        if len(response_cache) < 50:
            response_cache[cache_key] = answer
            print("💾 [DEBUG] Resposta salva no cache!")
        
        return QuestionResponse(
            answer=f"🤖 **RAG/LLM**: {answer}",
            success=True,
            message="Pergunta processada com RAG/LLM"
        )
        
    except Exception as e:
        print(f"❌ [DEBUG] Erro ao processar pergunta: {str(e)}")
        import traceback
        print(f"❌ [DEBUG] Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Chat Sport RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.get("/status")
async def status_check():
    return {
        "system": "Chat Sport RAG API",
        "qa_system_ready": qa_system is not None,
        "cache_size": len(response_cache),
        "quick_answers": len(QUICK_ANSWERS),
        "model_config": {
            "model": "tinyllama",
            "timeout": "120s backend + 150s frontend",
            "chunk_size": 200,
            "retriever_k": 2,
            "num_predict": 300,
            "temperature": 0.2,
            "stop_tokens": ["Human:", "Assistant:", "Pergunta:", "Resposta:"],
            "llm_timeout": "60s"
        },
        "performance": {
            "cache_response_time": "< 0.5s",
            "rag_response_time": "3-30s",
            "total_timeout": "150s"
        },
        "debug_endpoint": "/chat-debug (verbose logging)"
    }

@app.post("/chat-debug", response_model=QuestionResponse)
async def ask_question_debug(request: QuestionRequest):
    """Endpoint de debug que mostra informações detalhadas da resposta"""
    
    print(f"🔥 [DEBUG-VERBOSE] Recebida requisição: {request.message}")
    
    if qa_system is None:
        print("❌ [DEBUG] Sistema RAG não está inicializado!")
        raise HTTPException(
            status_code=500,
            detail="Sistema RAG não inicializado. Verifique os logs do servidor."
        )
    
    quick_answer = get_quick_answer(request.message)
    if quick_answer:
        print("⚡ [DEBUG] Resposta rápida encontrada!")
        return QuestionResponse(
            answer=f"⚡ **Resposta Rápida**: {quick_answer}",
            success=True,
            message="Resposta rápida do cache"
        )
    
    cache_key = request.message.lower().strip()
    if cache_key in response_cache:
        print("💾 [DEBUG] Resposta encontrada no cache!")
        return QuestionResponse(
            answer=f"💾 **Do Cache**: {response_cache[cache_key]}",
            success=True,
            message="Resposta do cache"
        )
    
    try:
        print("🔍 [DEBUG-VERBOSE] Iniciando invoke do qa_system...")
        print(f"📝 [DEBUG-VERBOSE] Query original: '{request.message}'")
        
        # Busca documentos relevantes primeiro
        retriever = qa_system.retriever
        docs = retriever.get_relevant_documents(request.message)
        print(f"📚 [DEBUG-VERBOSE] Documentos encontrados: {len(docs)}")
        for i, doc in enumerate(docs):
            print(f"📄 [DEBUG-VERBOSE] Doc {i+1}: {doc.page_content[:100]}...")
        
        import time
        start_time = time.time()
        
        # Invoke manual para mais controle
        response = qa_system.invoke({"query": request.message})
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏰ [DEBUG-VERBOSE] Duração: {duration:.2f}s")
        print(f"📋 [DEBUG-VERBOSE] Resposta bruta: {response}")
        print(f"🔍 [DEBUG-VERBOSE] Tipo da resposta: {type(response)}")
        
        if isinstance(response, dict) and "result" in response:
            answer = response["result"]
            print(f"📝 [DEBUG-VERBOSE] Result extraído: '{answer}'")
        else:
            answer = str(response)
            print(f"📝 [DEBUG-VERBOSE] Resposta convertida: '{answer}'")
        
        # Limpeza da resposta
        answer = answer.replace("Com base nas informações sobre futebol, responda em português brasileiro de forma completa:", "").strip()
        answer = answer.replace("Resposta completa:", "").strip()
        
        print(f"✨ [DEBUG-VERBOSE] Resposta final limpa ({len(answer)} chars): '{answer}'")
        
        # Salva no cache
        if len(response_cache) < 50:
            response_cache[cache_key] = answer
            print("💾 [DEBUG-VERBOSE] Resposta salva no cache!")
        
        return QuestionResponse(
            answer=f"🤖 **RAG/LLM** ({duration:.1f}s): {answer}",
            success=True,
            message=f"Processado em {duration:.1f}s com {len(docs)} documentos"
        )
        
    except Exception as e:
        print(f"❌ [DEBUG-VERBOSE] Erro detalhado: {str(e)}")
        import traceback
        print(f"❌ [DEBUG-VERBOSE] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
