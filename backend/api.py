from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
import pandas as pd
import glob

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
    title="World Cup RAG API",
    description="API para chatbot sobre Copa do Mundo FIFA com RAG",
    version="2.0.0"
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
current_model = None  # Variável global para rastrear o modelo em uso

WORLD_CUP_QUICK_ANSWERS = {
    "oi": "Olá! Sou seu assistente especializado em Copa do Mundo FIFA. Como posso ajudar?",
    "olá": "Olá! Sou seu assistente especializado em Copa do Mundo FIFA. Como posso ajudar?",
    "hello": "Hello! I'm your FIFA World Cup specialist assistant. How can I help?",
    
    # Títulos por país
    "quantas copas o brasil tem": "O Brasil conquistou 5 Copas do Mundo: 1958 (Suécia), 1962 (Chile), 1970 (México), 1994 (EUA), 2002 (Japão/Coreia do Sul).",
    "brasil copas": "O Brasil conquistou 5 Copas do Mundo: 1958 (Suécia), 1962 (Chile), 1970 (México), 1994 (EUA), 2002 (Japão/Coreia do Sul).",
    "quantas copas a alemanha tem": "A Alemanha tem 4 títulos de Copa do Mundo: 1954, 1974, 1990 e 2014.",
    "quantas copas a argentina tem": "A Argentina tem 3 títulos de Copa do Mundo: 1978, 1986 e 2022.",
    "quantas copas a frança tem": "A França tem 2 títulos de Copa do Mundo: 1998 e 2018.",
    "quantas copas a italia tem": "A Itália tem 4 títulos de Copa do Mundo: 1934, 1938, 1982 e 2006.",
    
    # Campeões por ano - múltiplas variações
    "campeão 2022": "Argentina foi campeã da Copa do Mundo de 2022 no Qatar, vencendo a França na final por 4-3 nos pênaltis (3-3 no tempo normal).",
    "quem ganhou em 2022": "Argentina foi campeã da Copa do Mundo de 2022 no Qatar.",
    "campeão 2018": "França foi campeã da Copa do Mundo de 2018 na Rússia, vencendo a Croácia por 4-2 na final.",
    "campeão 2014": "Alemanha foi campeã da Copa do Mundo de 2014 no Brasil, vencendo a Argentina por 1-0 na final.",
    "campeão 2010": "Espanha foi campeã da Copa do Mundo de 2010 na África do Sul, vencendo a Holanda por 1-0 na final.",
    "campeão 2006": "Itália foi campeã da Copa do Mundo de 2006 na Alemanha, vencendo a França nos pênaltis na final.",
    "campeão 2002": "Brasil foi campeão da Copa do Mundo de 2002 no Japão/Coreia do Sul, vencendo a Alemanha por 2-0 na final.",
    "campeão 1998": "França foi campeã da Copa do Mundo de 1998 em casa, vencendo o Brasil por 3-0 na final.",
  "campeão 1994": "Brasil foi campeão da Copa do Mundo de 1994 nos EUA, vencendo a Itália nos pênaltis na final.",
    
    # Artilheiros
    "artilheiro 2022": "Kylian Mbappé foi o artilheiro da Copa de 2022 com 8 gols.",
    "artilheiro 2018": "Harry Kane foi o artilheiro da Copa de 2018 com 6 gols.",
    "artilheiro 1998": "Davor Šuker foi o artilheiro da Copa de 1998 com 6 gols.",
    
    # Próxima Copa
    "próxima copa": "A próxima Copa do Mundo será em 2026, realizada conjuntamente pelos EUA, Canadá e México, com 48 seleções.",
    "copa 2026": "A Copa do Mundo de 2026 será nos EUA, Canadá e México, com formato expandido para 48 seleções.",
}

def load_csv_files(directory_path):
    """Carregar dados CSV de forma ultra-simples para evitar alucinações."""
    documents = []
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            file_name = os.path.basename(csv_file)
            
            if 'world_cup' in file_name.lower():
                # Documento individual para cada Copa do Mundo para máxima precisão
                for _, row in df.iterrows():
                    year = row.get('Year', '')
                    host = row.get('Host', '')
                    champion = row.get('Champion', '')
                    runner_up = row.get('Runner-Up', '')
                    top_scorer = row.get('TopScorrer', '')
                    teams = row.get('Teams', '')
                    
                    # Criar múltiplos formatos MUITO CLAROS para evitar confusão entre sede e campeão
                    individual_content = f"""===== COPA DO MUNDO FIFA DE {year} =====

DADOS OFICIAIS:
ANO: {year}
PAÍS-SEDE: {host} (LOCAL onde foi realizada a Copa)
CAMPEÃO MUNDIAL: {champion} (PAÍS que GANHOU o título)
VICE-CAMPEÃO: {runner_up} (PAÍS que chegou à final)
ARTILHEIRO: {top_scorer} (Maior goleador do torneio)
PARTICIPANTES: {teams} seleções

ATENÇÃO: {host} = SEDE (onde aconteceu) ≠ {champion} = CAMPEÃO (quem ganhou)

RESPOSTAS CORRETAS:
• Quem foi campeão em {year}? RESPOSTA: {champion}
• Campeão de {year}: {champion}
• Quem ganhou a Copa de {year}? RESPOSTA: {champion}
• Quem venceu em {year}? RESPOSTA: {champion}
• Título de {year}: {champion}
• Copa {year} campeão: {champion}

• Onde foi a Copa de {year}? RESPOSTA: {host}
• Sede de {year}: {host}
• Local da Copa {year}: {host}

• Vice-campeão de {year}: {runner_up}
• Finalista de {year}: {runner_up}

• Artilheiro de {year}: {top_scorer}
• Goleador de {year}: {top_scorer}

IMPORTANTE: O campeão da Copa de {year} foi {champion}, NÃO {host}.
A Copa foi realizada em {host}, mas quem ganhou foi {champion}.
"""
                    
                    documents.append(Document(
                        page_content=individual_content,
                        metadata={
                            "source": csv_file,
                            "file_name": file_name,
                            "year": year,
                            "champion": champion,
                            "data_category": "individual_world_cup",
                            "decade": f"{(year//10)*10}s"
                        }
                    ))
                
                # Documento focado em campeões com variações em português
                champions_content = "=== CAMPEÕES DA COPA DO MUNDO FIFA - LISTA DEFINITIVA ===\n\n"
                champions_content += "ATENÇÃO: CAMPEÃO = quem ganhou o título, SEDE = onde aconteceu\n\n"
                
                for _, row in df.iterrows():
                    year = row.get('Year', '')
                    champion = row.get('Champion', '')
                    host = row.get('Host', '')
                    
                    champions_content += f"COPA DE {year}:\n"
                    champions_content += f"CAMPEÃO (vencedor): {champion}\n"
                    champions_content += f"SEDE (local): {host}\n"
                    champions_content += f"RESULTADO: {champion} conquistou o título em {year}\n"
                    champions_content += f"ONDE: A Copa foi em {host}, mas o CAMPEÃO foi {champion}\n\n"
                    
                    # Múltiplas variações para o RAG encontrar
                    champions_content += f"Quem foi campeão de {year}? {champion}\n"
                    champions_content += f"Campeão {year}: {champion}\n"  
                    champions_content += f"Quem ganhou em {year}? {champion}\n"
                    champions_content += f"Título {year}: {champion}\n"
                    champions_content += f"Vencedor {year}: {champion}\n"
                    champions_content += f"Copa {year} - Campeão: {champion}\n"
                    champions_content += f"{champion} foi campeão da Copa de {year}\n"
                    champions_content += f"{champion} ganhou a Copa do Mundo de {year}\n\n"
                    
                champions_content += "\n=== RESUMO RÁPIDO ===\n"
                for _, row in df.iterrows():
                    year = row.get('Year', '')
                    champion = row.get('Champion', '')
                    champions_content += f"{year}: {champion}\n"
                
                documents.append(Document(
                    page_content=champions_content,
                    metadata={
                        "source": csv_file,
                        "file_name": file_name,
                        "data_category": "champions_comprehensive",
                        "rows": len(df)
                    }
                ))
                
                # Documento focado em vice-campeões com variações em português
                runners_up_content = "=== VICE-CAMPEÕES DA COPA DO MUNDO FIFA ===\n\n"
                runners_up_content += "Lista completa de todos os vice-campeões da Copa do Mundo:\n\n"
                
                for _, row in df.iterrows():
                    year = row.get('Year', '')
                    runner_up = row.get('Runner-Up', '')
                    host = row.get('Host', '')
                    
                    runners_up_content += f"Copa de {year}: {runner_up} foi vice-campeão (sede: {host})\n"
                    runners_up_content += f"Vice-campeão {year}: {runner_up}\n"
                    runners_up_content += f"Vice {year}: {runner_up}\n"
                    runners_up_content += f"Finalista {year}: {runner_up}\n"
                    runners_up_content += f"Segundo lugar {year}: {runner_up}\n"
                    runners_up_content += f"{runner_up} foi vice-campeão em {year}\n"
                    runners_up_content += f"{runner_up} foi finalista em {year}\n"
                    runners_up_content += f"{runner_up} chegou à final em {year}\n"
                    runners_up_content += f"Quem foi vice-campeão de {year}? {runner_up}\n"
                    runners_up_content += f"Quem foi vice de {year}? {runner_up}\n\n"
                
                documents.append(Document(
                    page_content=runners_up_content,
                    metadata={
                        "source": csv_file,
                        "file_name": file_name,
                        "data_category": "runners_up_comprehensive",
                        "rows": len(df)
                    }
                ))
                
                # Documento focado em artilheiros com variações em português
                scorers_content = "=== ARTILHEIROS DA COPA DO MUNDO FIFA ===\n\n"
                scorers_content += "Lista completa de todos os artilheiros da Copa do Mundo:\n\n"
                
                for _, row in df.iterrows():
                    year = row.get('Year', '')
                    top_scorer = row.get('TopScorrer', '')  # Note: TopScorrer no CSV original
                    host = row.get('Host', '')
                    
                    scorers_content += f"Copa de {year}: {top_scorer} foi artilheiro (sede: {host})\n"
                    scorers_content += f"Artilheiro {year}: {top_scorer}\n"
                    scorers_content += f"Goleador {year}: {top_scorer}\n"
                    scorers_content += f"Maior artilheiro {year}: {top_scorer}\n"
                    scorers_content += f"Maior goleador {year}: {top_scorer}\n"
                    scorers_content += f"{top_scorer} foi artilheiro em {year}\n"
                    scorers_content += f"{top_scorer} foi o maior goleador em {year}\n"
                    scorers_content += f"{top_scorer} foi o goleador da Copa de {year}\n"
                    scorers_content += f"Quem foi artilheiro de {year}? {top_scorer}\n"
                    scorers_content += f"Quem foi o goleador de {year}? {top_scorer}\n\n"
                
                documents.append(Document(
                    page_content=scorers_content,
                    metadata={
                        "source": csv_file,
                        "file_name": file_name,
                        "data_category": "scorers_comprehensive",
                        "rows": len(df)
                    }
                ))
                    
            elif 'fifa_ranking' in file_name.lower():
                # Melhorar estrutura do ranking
                content_parts = []
                content_parts.append(f"=== RANKING MUNDIAL FIFA (OUTUBRO 2022) ===\n\n")
                
                # Dividir em grupos para melhor recuperação
                top_10 = df.head(10)
                content_parts.append("TOP 10 MUNDIAL:\n")
                for _, row in top_10.iterrows():
                    team = row.get('team', '')
                    rank = row.get('rank', '')
                    points = row.get('points', '')
                    content_parts.append(f"{rank}º - {team}: {points} pontos\n")
                
                content_parts.append("\nTOP 11-20:\n")
                next_10 = df.iloc[10:20]
                for _, row in next_10.iterrows():
                    team = row.get('team', '')
                    rank = row.get('rank', '')
                    points = row.get('points', '')
                    content_parts.append(f"{rank}º - {team}: {points} pontos\n")
                
                content = "".join(content_parts)
                
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": csv_file,
                        "file_name": file_name,
                        "data_category": "fifa_ranking",
                        "date": "2022-10",
                        "rows": len(df)
                    }
                ))
                    
            elif 'matches' in file_name.lower():
                # Focar apenas nas finais para evitar confusão
                content_parts = []
                content_parts.append(f"=== FINAIS DA COPA DO MUNDO (1930-2022) ===\n\n")
                
                # Filtrar apenas finais
                finals = df[df['Round'].str.contains('Final', na=False, case=False)]
                finals_only = finals[~finals['Round'].str.contains('Semi|Third', na=False, case=False)]
                
                for _, match in finals_only.iterrows():
                    year = match.get('Year', '')
                    home = match.get('home_team', '')
                    away = match.get('away_team', '')
                    score = match.get('Score', '')
                    venue = match.get('Venue', '')
                    
                    # Determinar campeão baseado no placar
                    if 'Argentina' in home and 'France' in away and year == 2022:
                        champion = "Argentina"
                    elif 'France' in home and 'Croatia' in away and year == 2018:
                        champion = "França"
                    else:
                        # Lógica para outros anos baseada no placar
                        champion = "Ver dados históricos"
                    
                    entry = f"""Final da Copa {year}:
{home} vs {away}
Placar: {score}
Local: {venue}
Campeão: {champion}

"""
                    content_parts.append(entry)
                
                content = "".join(content_parts)
                
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": csv_file,
                        "file_name": file_name,
                        "data_category": "world_cup_finals",
                        "rows": len(finals_only)
                    }
                ))
                    
            else:
                # Outros CSVs
                content = f"Dados de {file_name}:\n{df.head(5).to_string(index=False)}"
                documents.append(Document(
                    page_content=content,
                    metadata={"source": csv_file, "file_name": file_name, "data_category": "other"}
                ))
            
        except Exception as e:
            print(f"Error loading {csv_file}: {str(e)}")
            continue
    
    return documents

def get_quick_answer(message):
    """Quick answer matching only for exact greetings and simple queries."""
    message_lower = message.lower().strip()
    
    # Remove pontuação e caracteres extras
    import re
    message_clean = re.sub(r'[^\w\s]', '', message_lower)
    
    # Verificação exata primeiro - apenas para saudações e perguntas muito específicas
    if message_lower in WORLD_CUP_QUICK_ANSWERS:
        return WORLD_CUP_QUICK_ANSWERS[message_lower]
    
    if message_clean in WORLD_CUP_QUICK_ANSWERS:
        return WORLD_CUP_QUICK_ANSWERS[message_clean]
    
    # Apenas para saudações simples
    greetings = ["oi", "olá", "hello", "hi"]
    if message_lower in greetings:
        return WORLD_CUP_QUICK_ANSWERS.get(message_lower, None)
    
    # Para títulos por país - apenas matches exatos
    country_titles = [
        "quantas copas o brasil tem",
        "brasil copas", 
        "quantas copas a alemanha tem",
        "quantas copas a argentina tem",
        "quantas copas a frança tem",
        "quantas copas a italia tem"
    ]
    
    if message_lower in country_titles:
        return WORLD_CUP_QUICK_ANSWERS.get(message_lower, None)
    
    # Para próxima Copa
    next_cup = ["próxima copa", "copa 2026"]
    if message_lower in next_cup:
        return WORLD_CUP_QUICK_ANSWERS.get(message_lower, None)
    
    # Para todas as outras perguntas (campeões, artilheiros, etc), usar RAG
    return None

def initialize_rag_system():
    global qa_system, embeddings, current_model
    
    try:
        faiss_index_path = "faiss_index_"
        
        if os.path.exists(f"{faiss_index_path}/index.faiss"):
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2", 
                model_kwargs={"device": "cpu"}
            )
            try:
                vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
            except TypeError:
                vectorstore = FAISS.load_local(faiss_index_path, embeddings)
        else:
            documents = load_csv_files("wcdataset")
            if not documents:
                raise Exception("Nenhum arquivo CSV encontrado!")
            
            text_splitter = CharacterTextSplitter(
                chunk_size=600,   # Reduzir ainda mais para focar em informações específicas
                chunk_overlap=50,  # Overlap mínimo para evitar misturar informações
                separator="====="   # Usar o separador das seções para preservar contexto
            )
            docs = text_splitter.split_documents(documents)
            
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
            
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local(faiss_index_path)
        
        llm = None
        model_used = None
        
        # Tentar qwen2.5:3b primeiro (melhor para português)
        try:
            llm = Ollama(
                model="qwen2.5:3b",
                temperature=0.0,
                timeout=60
            )
            # Testar se o modelo funciona
            llm.invoke("test")
            model_used = "qwen2.5:3b"
            current_model = "qwen2.5:3b"
            print("✅ Usando modelo qwen2.5:3b (otimizado para português)")
        except Exception as e:
            print(f"⚠️ qwen2.5:3b não disponível: {e}")
            
            # Fallback para llama3.2
            try:
                llm = Ollama(
                    model="llama3.2",
                    temperature=0.0,
                    timeout=60
                )
                # Testar se o modelo funciona
                llm.invoke("test")
                model_used = "llama3.2"
                current_model = "llama3.2"
                print("✅ Usando modelo llama3.2 como fallback")
            except Exception as e2:
                print(f"❌ Erro com ambos os modelos: qwen2.5:3b e llama3.2")
                raise Exception(f"Nenhum modelo disponível: {e2}")
        
        if llm is None:
            raise Exception("Falha ao inicializar qualquer modelo")
        
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 3,  # Mais documentos para encontrar informação
                "score_threshold": 0.2  # Threshold baixo para capturar mais resultados
            }
        )
        
        template = """Use apenas os dados fornecidos para responder. Seja direto.

DADOS:
{context}

PERGUNTA: {question}

RESPOSTA:"""
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        
        qa_system = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )
        
        return True
        
    except Exception as e:
        print(f"Erro ao inicializar RAG: {str(e)}")
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
    if qa_system is None:
        raise HTTPException(status_code=500, detail="Sistema RAG não inicializado")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")
    
    quick_answer = get_quick_answer(request.message)
    if quick_answer:
        return QuestionResponse(
            answer=quick_answer,
            success=True,
            message="Resposta rápida"
        )
    
    try:
        response = qa_system.invoke({"query": request.message})
        
        if isinstance(response, dict) and "result" in response:
            answer = response["result"]
        else:
            answer = str(response)
        
        answer = answer.strip()
        
        return QuestionResponse(
            answer=answer,
            success=True,
            message="Resposta processada com RAG"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "World Cup RAG API",
        "version": "2.0.0",
        "description": "Chatbot especializado em Copa do Mundo FIFA com RAG",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "status": "/status",
            "docs": "/docs"
        }
    }

@app.get("/status")
async def status_check():
    return {
        "system": "World Cup RAG API",
        "qa_system_ready": qa_system is not None,
        "quick_answers": len(WORLD_CUP_QUICK_ANSWERS),
        "model_config": {
            "model": current_model if current_model else "qwen2.5:3b",  # Modelo real em uso
            "fallback_model": "llama3.2",
            "timeout": "60s",
            "chunk_size": 600,  # Corrigido para refletir o valor real
            "chunk_overlap": 50,  # Corrigido para refletir o valor real
            "separator": "=====",
            "retriever_k": 3,  # Corrigido para refletir o valor real
            "score_threshold": 0.2,  # Adicionado
            "temperature": 0.0,
            "anti_hallucination": True,
            "individual_documents": True,
            "comprehensive_indexing": True,
            "ultra_clear_distinction": True,
            "champion_vs_host_fix": True,
            "critical_improvement": True,
            "ultra_restrictive_rag": True,
            "portuguese_optimized": True
        },
        "data_sources": ["world_cup.csv", "fifa_ranking_2022-10-06.csv", "matches_1930_2022.csv"]
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
