from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
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

def create_advanced_chunks(documents):
    """Criar chunks avançados com múltiplas estratégias para melhor recuperação."""
    all_docs = []
    
    # Estratégia 1: Chunks pequenos e focados (para respostas precisas)
    small_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["=====", "\n\n", "\n", ".", "!", "?", ";", ":", " "],
        length_function=len,
    )
    
    # Estratégia 2: Chunks médios (para contexto balanceado)
    medium_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["=====", "\n\n", "\n", ".", " "],
        length_function=len,
    )
    
    # Estratégia 3: Chunks grandes (para contexto completo)
    large_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        separators=["=====", "\n\n"],
        length_function=len,
    )
    
    for doc in documents:
        # Adicionar documento original completo
        all_docs.append(Document(
            page_content=doc.page_content,
            metadata={**doc.metadata, "chunk_type": "original", "chunk_size": len(doc.page_content)}
        ))
        
        # Chunks pequenos para precisão
        small_chunks = small_splitter.split_documents([doc])
        for i, chunk in enumerate(small_chunks):
            chunk.metadata.update({
                **doc.metadata,
                "chunk_type": "small",
                "chunk_index": i,
                "chunk_size": len(chunk.page_content),
                "chunk_strategy": "precision"
            })
            all_docs.append(chunk)
        
        # Chunks médios para equilíbrio
        medium_chunks = medium_splitter.split_documents([doc])
        for i, chunk in enumerate(medium_chunks):
            chunk.metadata.update({
                **doc.metadata,
                "chunk_type": "medium", 
                "chunk_index": i,
                "chunk_size": len(chunk.page_content),
                "chunk_strategy": "balanced"
            })
            all_docs.append(chunk)
        
        # Chunks grandes para contexto
        large_chunks = large_splitter.split_documents([doc])
        for i, chunk in enumerate(large_chunks):
            chunk.metadata.update({
                **doc.metadata,
                "chunk_type": "large",
                "chunk_index": i, 
                "chunk_size": len(chunk.page_content),
                "chunk_strategy": "context"
            })
            all_docs.append(chunk)
    
    print(f"📊 Chunks criados: {len(all_docs)} total")
    print(f"   • Documentos originais: {len(documents)}")
    print(f"   • Chunks pequenos (precisão): {len([d for d in all_docs if d.metadata.get('chunk_type') == 'small'])}")
    print(f"   • Chunks médios (equilíbrio): {len([d for d in all_docs if d.metadata.get('chunk_type') == 'medium'])}")
    print(f"   • Chunks grandes (contexto): {len([d for d in all_docs if d.metadata.get('chunk_type') == 'large'])}")
    
    return all_docs

def create_enhanced_embeddings():
    """Criar embeddings melhorados com modelo mais poderoso."""
    print("🧠 Inicializando modelo de embedding avançado...")
    
    # Tentar modelo multilíngue mais poderoso primeiro
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            model_kwargs={
                "device": "cpu",
                "trust_remote_code": True
            },
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": 32
            }
        )
        print("✅ Usando paraphrase-multilingual-mpnet-base-v2 (melhor para português)")
        return embeddings, "paraphrase-multilingual-mpnet-base-v2"
    except Exception as e:
        print(f"⚠️ Fallback do modelo multilíngue: {e}")
        
        # Fallback para modelo mais rápido mas ainda bom
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_kwargs={
                    "device": "cpu",
                    "trust_remote_code": True
                },
                encode_kwargs={
                    "normalize_embeddings": True,
                    "batch_size": 16
                }
            )
            print("✅ Usando all-mpnet-base-v2 (modelo robusto)")
            return embeddings, "all-mpnet-base-v2"
        except Exception as e2:
            print(f"⚠️ Usando modelo padrão: {e2}")
            
            # Último fallback
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            print("✅ Usando all-MiniLM-L6-v2 (modelo rápido)")
            return embeddings, "all-MiniLM-L6-v2"

def create_optimized_vectorstore(docs, embeddings):
    """Criar vectorstore otimizado com configurações avançadas."""
    print("🏗️ Criando vectorstore otimizado...")
    print(f"   • Processando {len(docs)} chunks...")
    
    # Processar em lotes para não sobrecarregar a memória
    batch_size = 50
    vectorstore = None
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        print(f"   • Processando lote {i//batch_size + 1}/{(len(docs) + batch_size - 1)//batch_size}")
        
        if vectorstore is None:
            # Criar vectorstore inicial
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            # Adicionar ao vectorstore existente
            batch_vectorstore = FAISS.from_documents(batch, embeddings)
            vectorstore.merge_from(batch_vectorstore)
    
    print("✅ Vectorstore otimizado criado com sucesso")
    return vectorstore

def load_csv_files(directory_path):
    """Carregar dados CSV de forma ultra-simples para evitar alucinações."""
    documents = []
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='latin1')
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
            
            elif 'all_goals' in file_name.lower():
                content_parts = []
                content_parts.append("=== DETALHES DE TODOS OS GOLS (1930-2022) ===\n\n")
                
                # Agrupamento por torneio
                for tournament in df['tournament_name'].unique():
                    tournament_data = df[df['tournament_name'] == tournament]
                    year = re.search(r'\b(19\d{2}|20\d{2})\b', str(tournament)).group(0)
                    
                    content_parts.append(f"★ COPADOMUNDO {year}:\n")
                    
                    # Artilheiro principal
                    top_scorer = tournament_data['player_name'].mode()[0]
                    goals_count = tournament_data['player_name'].value_counts().max()
                    content_parts.append(f"Artilheiro: {top_scorer} ({goals_count} gols)\n")
                    
                    # Detalhes dos gols
                    content_parts.append("Gols marcados:\n")
                    for _, row in tournament_data.iterrows():
                        content_parts.append(
                            f"- {row['minute']}' {row['player_name']} ({row['team_name']}) vs {row['opponent']}\n"
                        )
                    content_parts.append("\n")
                
                content = "".join(content_parts)
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": csv_file,
                        "file_name": file_name,
                        "data_category": "goals_details",
                        "rows": len(df)
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

def process_csv_data():
    """Processar dados CSV em documentos estruturados para RAG ultra-restritivo."""
    
    print("📊 Processando CSVs com estruturação ultra-clara...")
    
    all_docs = []
    csv_files = glob.glob(os.path.join("wcdataset", "*.csv"))
    
    if not csv_files:
        print("❌ Nenhum arquivo CSV encontrado em wcdataset/")
        return []
    
    # Processar cada CSV
    for csv_file in csv_files:
        try:
            print(f"📄 Processando {os.path.basename(csv_file)}...")
            df = pd.read_csv(csv_file, encoding='latin1')
            
            if 'world_cup.csv' in csv_file:
                # Dados principais da Copa do Mundo
                for _, row in df.iterrows():
                    year = row.get('Year', '')
                    champion = row.get('Winner', row.get('Champion', ''))
                    runner_up = row.get('Runners-Up', row.get('Runner_up', ''))
                    host = row.get('Country', row.get('Host', ''))
                    
                    # Documento para campeão (múltiplas variações)
                    if champion:
                        champion_variations = [
                            f"Copa do Mundo de {year}: Campeão foi {champion}",
                            f"Campeão da Copa do Mundo {year}: {champion}",
                            f"Quem ganhou a Copa do Mundo de {year}? {champion}",
                            f"Vencedor Copa {year}: {champion}",
                            f"{champion} foi campeão mundial em {year}",
                            f"Mundial {year} - Campeão: {champion}",
                            f"Título mundial {year}: {champion}"
                        ]
                        
                        for variation in champion_variations:
                            all_docs.append(Document(
                                page_content=variation,
                                metadata={
                                    "type": "champion",
                                    "year": year,
                                    "champion": champion,
                                    "source": "world_cup.csv"
                                }
                            ))
                    
                    # Documento para vice-campeão (ULTRA-EXPANDIDO)
                    if runner_up:
                        runner_up_variations = [
                            # Variações básicas
                            f"Copa do Mundo de {year}: Vice-campeão foi {runner_up}",
                            f"Vice-campeão da Copa do Mundo {year}: {runner_up}",
                            f"Segundo lugar Copa {year}: {runner_up}",
                            f"Final Copa {year}: {champion} venceu {runner_up}",
                            f"Finalista derrotado em {year}: {runner_up}",
                            
                            # Perguntas diretas
                            f"Quem foi vice-campeão de {year}? {runner_up}",
                            f"Quem foi vice-campeão da Copa de {year}? {runner_up}",
                            f"Quem foi vice-campeão da Copa do Mundo de {year}? {runner_up}",
                            f"Quem foi o vice em {year}? {runner_up}",
                            f"Quem foi o vice da Copa de {year}? {runner_up}",
                            f"Quem foi vice da Copa do Mundo de {year}? {runner_up}",
                            f"Quem ficou em segundo lugar em {year}? {runner_up}",
                            f"Quem perdeu a final de {year}? {runner_up}",
                            f"Quem foi derrotado na final de {year}? {runner_up}",
                            f"Quem chegou à final em {year}? {runner_up}",
                            f"Quem foi finalista em {year}? {runner_up}",
                            f"Quem foi o finalista de {year}? {runner_up}",
                            f"Quem foi finalista da Copa de {year}? {runner_up}",
                            f"Quem foi finalista da Copa do Mundo de {year}? {runner_up}",
                            f"Quem disputou a final de {year}? {champion} e {runner_up}",
                            
                            # Variações "vice" abreviado
                            f"Vice {year}: {runner_up}",
                            f"Vice de {year}: {runner_up}",
                            f"Vice da Copa {year}: {runner_up}",
                            f"Vice Copa {year}: {runner_up}",
                            f"Vice-campeão {year}: {runner_up}",
                            f"Vice campeão {year}: {runner_up}",
                            f"Vice mundial {year}: {runner_up}",
                            f"Vice do Mundial {year}: {runner_up}",
                            
                            # Formas mais elaboradas
                            f"{runner_up} foi vice-campeão mundial em {year}",
                            f"{runner_up} foi vice-campeão da Copa do Mundo de {year}",
                            f"{runner_up} foi vice-campeão em {year}",
                            f"{runner_up} ficou em segundo lugar em {year}",
                            f"{runner_up} perdeu a final de {year}",
                            f"{runner_up} chegou à final em {year}",
                            f"{runner_up} foi finalista em {year}",
                            f"{runner_up} disputou a final contra {champion} em {year}",
                            f"{runner_up} foi derrotado por {champion} na final de {year}",
                            
                            # Com contexto de sede
                            f"Na Copa de {year} em {host}, {runner_up} foi vice-campeão",
                            f"Em {year} ({host}), {runner_up} foi vice-campeão",
                            f"Copa {year} no {host}: {runner_up} foi vice",
                            f"Mundial {year} em {host}: vice foi {runner_up}",
                            
                            # Variações em inglês para busca internacional
                            f"Runner-up {year}: {runner_up}",
                            f"Second place {year}: {runner_up}",
                            f"Finalist {year}: {runner_up}",
                            
                            # Contexto da final
                            f"A final de {year} foi {champion} vs {runner_up}, venceu {champion}",
                            f"Final da Copa {year}: {champion} derrotou {runner_up}",
                            f"Resultado final {year}: {champion} campeão, {runner_up} vice",
                            f"Decisão {year}: {champion} venceu {runner_up}",
                            f"Copa {year} - Final: {champion} x {runner_up}, campeão {champion}",
                        ]
                        
                        for variation in runner_up_variations:
                            all_docs.append(Document(
                                page_content=variation,
                                metadata={
                                    "type": "runner_up",
                                    "year": year,
                                    "runner_up": runner_up,
                                    "champion": champion,
                                    "host": host,
                                    "source": "world_cup.csv"
                                }
                            ))
                    
                    # Documento para sede (ULTRA-EXPANDIDO - CRÍTICO para distinguir de campeão)
                    if host:
                        host_variations = [
                            # Variações básicas de sede
                            f"Copa do Mundo de {year}: Sede foi {host}",
                            f"Sede da Copa do Mundo {year}: {host}",
                            f"Onde foi a Copa do Mundo de {year}? {host}",
                            f"País anfitrião Copa {year}: {host}",
                            f"{host} sediou a Copa do Mundo em {year}",
                            f"Local Copa {year}: {host}",
                            f"Organização Copa {year}: {host}",
                            
                            # Perguntas diretas sobre sede
                            f"Onde foi a Copa de {year}? {host}",
                            f"Onde foi a Copa do Mundo de {year}? {host}",
                            f"Onde aconteceu a Copa de {year}? {host}",
                            f"Onde aconteceu a Copa do Mundo de {year}? {host}",
                            f"Onde foi realizada a Copa de {year}? {host}",
                            f"Onde foi realizada a Copa do Mundo de {year}? {host}",
                            f"Onde ocorreu a Copa de {year}? {host}",
                            f"Onde ocorreu a Copa do Mundo de {year}? {host}",
                            f"Em que país foi a Copa de {year}? {host}",
                            f"Em que país foi a Copa do Mundo de {year}? {host}",
                            f"Qual foi a sede da Copa de {year}? {host}",
                            f"Qual foi a sede da Copa do Mundo de {year}? {host}",
                            f"Qual país sediou a Copa de {year}? {host}",
                            f"Qual país sediou a Copa do Mundo de {year}? {host}",
                            f"Quem sediou a Copa de {year}? {host}",
                            f"Quem sediou a Copa do Mundo de {year}? {host}",
                            f"Quem foi anfitrião da Copa de {year}? {host}",
                            f"Quem foi anfitrião da Copa do Mundo de {year}? {host}",
                            f"Quem organizou a Copa de {year}? {host}",
                            f"Quem organizou a Copa do Mundo de {year}? {host}",
                            f"Quem foi o organizador da Copa de {year}? {host}",
                            f"Qual foi o país-sede de {year}? {host}",
                            f"Qual foi o país anfitrião de {year}? {host}",
                            
                            # Variações "sede" abreviadas
                            f"Sede {year}: {host}",
                            f"Sede de {year}: {host}",
                            f"Sede da Copa {year}: {host}",
                            f"Sede Copa {year}: {host}",
                            f"Local {year}: {host}",
                            f"Local da Copa {year}: {host}",
                            f"País-sede {year}: {host}",
                            f"Anfitrião {year}: {host}",
                            f"País anfitrião {year}: {host}",
                            f"Organizador {year}: {host}",
                            
                            # Formas mais elaboradas
                            f"{host} foi sede da Copa do Mundo de {year}",
                            f"{host} foi sede em {year}",
                            f"{host} foi o país-sede em {year}",
                            f"{host} foi anfitrião da Copa de {year}",
                            f"{host} foi anfitrião em {year}",
                            f"{host} organizou a Copa de {year}",
                            f"{host} organizou a Copa do Mundo de {year}",
                            f"{host} recebeu a Copa de {year}",
                            f"{host} recebeu a Copa do Mundo de {year}",
                            f"{host} hospedou a Copa de {year}",
                            f"{host} hospedou a Copa do Mundo de {year}",
                            f"A Copa de {year} foi realizada em {host}",
                            f"A Copa do Mundo de {year} foi realizada em {host}",
                            f"A Copa de {year} aconteceu em {host}",
                            f"A Copa do Mundo de {year} aconteceu em {host}",
                            f"O Mundial de {year} foi em {host}",
                            f"O Mundial de {year} aconteceu em {host}",
                            
                            # DISTINÇÃO CRÍTICA - Sede vs Campeão
                            f"ATENÇÃO: {host} foi SEDE em {year}, mas campeão foi {champion}",
                            f"IMPORTANTE: {host} foi o local, {champion} foi o campeão em {year}",
                            f"DIFERENÇA: {host} = sede (local), {champion} = campeão (vencedor) em {year}",
                            f"NÃO CONFUNDIR: {host} sediou, {champion} ganhou em {year}",
                            f"CUIDADO: {host} foi anfitrião, {champion} foi vencedor em {year}",
                            f"Copa {year}: sede em {host}, campeão {champion}",
                            f"Em {year}: local {host}, vencedor {champion}",
                            f"Mundial {year}: organizado por {host}, ganho por {champion}",
                            f"A Copa de {year} foi EM {host}, mas GANHOU {champion}",
                            f"Realizada em {host}, vencida por {champion} em {year}",
                            
                            # Variações em inglês
                            f"Host {year}: {host}",
                            f"Host country {year}: {host}",
                            f"Where was {year} World Cup? {host}",
                            f"Location {year}: {host}",
                            
                            # Com contexto do campeão e vice
                            f"Copa {year} sediada por {host}: {champion} venceu {runner_up}",
                            f"Em {host} ({year}): {champion} foi campeão, {runner_up} vice",
                            f"Mundial {year} no {host}: campeão {champion}, vice {runner_up}",
                            f"Sede {host} em {year}: final {champion} x {runner_up}",
                            
                            # Variações específicas por continente/região
                            f"Copa {year} na {host} (sede)",
                            f"Copa {year} no {host} (local do torneio)",
                            f"Mundial {year} em território {host}",
                            f"Torneio {year} realizado em {host}",
                        ]
                        
                        for variation in host_variations:
                            all_docs.append(Document(
                                page_content=variation,
                                metadata={
                                    "type": "host",
                                    "year": year,
                                    "host": host,
                                    "champion": champion,
                                    "runner_up": runner_up,
                                    "source": "world_cup.csv"
                                }
                            ))
            
            elif 'matches_1930_2022.csv' in csv_file:
                # Dados de partidas para artilheiros
                print(f"   📊 Processando partidas... ({len(df)} registros)")
                
                # Agrupar por Copa para encontrar artilheiros
                if 'World Cup' in df.columns or 'Tournament' in df.columns:
                    tournament_col = 'World Cup' if 'World Cup' in df.columns else 'Tournament'
                    
                    for tournament in df[tournament_col].unique():
                        if pd.isna(tournament):
                            continue
                            
                        tournament_matches = df[df[tournament_col] == tournament]
                        
                        # Extrair year do tournament name
                        year_match = tournament
                        if str(year_match).isdigit():
                            year = year_match
                        else:
                            # Tentar extrair ano
                            import re
                            year_search = re.search(r'\b(19\d{2}|20\d{2})\b', str(tournament))
                            year = year_search.group(1) if year_search else str(tournament)
                        
                        # Contar gols por jogador (simplificado)
                        scorer_col = None
                        for col in ['Scorer', 'Goal_scorer', 'Player']:
                            if col in df.columns:
                                scorer_col = col
                                break
                        
                        if scorer_col and not tournament_matches[scorer_col].isna().all():
                            top_scorer = tournament_matches[scorer_col].value_counts().head(1)
                            if not top_scorer.empty:
                                top_scorer_name = top_scorer.index[0]
                                goals = top_scorer.iloc[0]
                                
                                # Criar documentos para artilheiro (ULTRA-EXPANDIDO)
                                scorer_variations = [
                                    # Variações básicas
                                    f"Artilheiro da Copa do Mundo de {year}: {top_scorer_name} com {goals} gols",
                                    f"Maior artilheiro Copa {year}: {top_scorer_name} ({goals} gols)",
                                    f"Quem foi o artilheiro da Copa de {year}? {top_scorer_name}",
                                    f"Copa {year} - Artilheiro: {top_scorer_name} ({goals} gols)",
                                    f"{top_scorer_name} foi artilheiro em {year} com {goals} gols",
                                    
                                    # Perguntas diretas sobre artilheiro
                                    f"Quem foi artilheiro de {year}? {top_scorer_name}",
                                    f"Quem foi artilheiro da Copa de {year}? {top_scorer_name}",
                                    f"Quem foi artilheiro da Copa do Mundo de {year}? {top_scorer_name}",
                                    f"Quem foi o artilheiro de {year}? {top_scorer_name}",
                                    f"Quem foi o artilheiro da Copa de {year}? {top_scorer_name}",
                                    f"Quem foi o artilheiro da Copa do Mundo de {year}? {top_scorer_name}",
                                    f"Quem foi o goleador de {year}? {top_scorer_name}",
                                    f"Quem foi o goleador da Copa de {year}? {top_scorer_name}",
                                    f"Quem foi o goleador da Copa do Mundo de {year}? {top_scorer_name}",
                                    f"Quem foi o maior goleador de {year}? {top_scorer_name}",
                                    f"Quem foi o maior goleador da Copa de {year}? {top_scorer_name}",
                                    f"Quem foi o maior artilheiro de {year}? {top_scorer_name}",
                                    f"Quem foi o maior artilheiro da Copa de {year}? {top_scorer_name}",
                                    f"Quem marcou mais gols em {year}? {top_scorer_name}",
                                    f"Quem marcou mais gols na Copa de {year}? {top_scorer_name}",
                                    f"Quem fez mais gols em {year}? {top_scorer_name}",
                                    f"Quem fez mais gols na Copa de {year}? {top_scorer_name}",
                                    f"Quem foi o cestinha de {year}? {top_scorer_name}",
                                    f"Quem foi o cestinha da Copa de {year}? {top_scorer_name}",
                                    
                                    # Variações "artilheiro" abreviadas
                                    f"Artilheiro {year}: {top_scorer_name}",
                                    f"Artilheiro de {year}: {top_scorer_name}",
                                    f"Artilheiro da Copa {year}: {top_scorer_name}",
                                    f"Goleador {year}: {top_scorer_name}",
                                    f"Goleador de {year}: {top_scorer_name}",
                                    f"Goleador da Copa {year}: {top_scorer_name}",
                                    f"Maior artilheiro {year}: {top_scorer_name}",
                                    f"Maior goleador {year}: {top_scorer_name}",
                                    f"Top scorer {year}: {top_scorer_name}",
                                    
                                    # Formas mais elaboradas
                                    f"{top_scorer_name} foi artilheiro da Copa do Mundo de {year}",
                                    f"{top_scorer_name} foi artilheiro em {year}",
                                    f"{top_scorer_name} foi o artilheiro em {year}",
                                    f"{top_scorer_name} foi goleador da Copa de {year}",
                                    f"{top_scorer_name} foi goleador em {year}",
                                    f"{top_scorer_name} foi o goleador em {year}",
                                    f"{top_scorer_name} foi o maior artilheiro de {year}",
                                    f"{top_scorer_name} foi o maior goleador de {year}",
                                    f"{top_scorer_name} marcou mais gols em {year}",
                                    f"{top_scorer_name} fez mais gols na Copa de {year}",
                                    f"{top_scorer_name} liderou os gols em {year}",
                                    f"{top_scorer_name} foi o cestinha de {year}",
                                    f"{top_scorer_name} terminou artilheiro em {year}",
                                    f"{top_scorer_name} ficou como artilheiro em {year}",
                                    f"{top_scorer_name} conquistou a artilharia em {year}",
                                    f"{top_scorer_name} ganhou a artilharia em {year}",
                                    
                                    # Com número de gols específico
                                    f"{top_scorer_name} marcou {goals} gols em {year}",
                                    f"{top_scorer_name} fez {goals} gols na Copa de {year}",
                                    f"{top_scorer_name} balançou as redes {goals} vezes em {year}",
                                    f"Com {goals} gols, {top_scorer_name} foi artilheiro em {year}",
                                    f"Foram {goals} gols de {top_scorer_name} em {year}",
                                    f"Total de {goals} gols para {top_scorer_name} em {year}",
                                    f"{top_scorer_name}: {goals} gols na Copa {year}",
                                    f"Placar final da artilharia {year}: {top_scorer_name} com {goals} gols",
                                    
                                    # Variações com contexto da sede
                                    f"Na Copa de {year}, {top_scorer_name} foi artilheiro com {goals} gols",
                                    f"Em {year}, {top_scorer_name} foi o maior goleador com {goals} gols",
                                    f"Copa {year}: artilheiro {top_scorer_name} ({goals} gols)",
                                    f"Mundial {year}: goleador {top_scorer_name} com {goals} gols",
                                    
                                    # Variações em inglês
                                    f"Top scorer {year}: {top_scorer_name} ({goals} goals)",
                                    f"Leading scorer {year}: {top_scorer_name}",
                                    f"Golden Boot {year}: {top_scorer_name}",
                                    f"Most goals {year}: {top_scorer_name} with {goals}",
                                    
                                    # Contexto de premiação
                                    f"{top_scorer_name} ganhou a Chuteira de Ouro em {year}",
                                    f"{top_scorer_name} conquistou a Chuteira de Ouro de {year}",
                                    f"Chuteira de Ouro {year}: {top_scorer_name}",
                                    f"Golden Boot {year}: {top_scorer_name}",
                                    f"Prêmio de artilheiro {year}: {top_scorer_name}",
                                    f"Artilharia da Copa {year}: {top_scorer_name} com {goals} gols",
                                    
                                    # Contexto comparativo
                                    f"{top_scorer_name} liderou a artilharia com {goals} gols em {year}",
                                    f"O maior pontuador de {year} foi {top_scorer_name}",
                                    f"Ninguém marcou mais que {top_scorer_name} em {year}",
                                    f"{top_scorer_name} superou todos na artilharia de {year}",
                                ]
                                
                                for variation in scorer_variations:
                                    all_docs.append(Document(
                                        page_content=variation,
                                        metadata={
                                            "type": "top_scorer",
                                            "year": year,
                                            "scorer": top_scorer_name,
                                            "goals": goals,
                                            "source": "matches_1930_2022.csv"
                                        }
                                    ))
            
            elif 'fifa_ranking' in csv_file:
                # Dados de ranking FIFA
                print(f"   📊 Processando ranking FIFA... ({len(df)} países)")
                
                # Documentos sobre ranking atual
                if 'Country' in df.columns and 'Total Points' in df.columns:
                    top_10 = df.head(10)
                    
                    for idx, row in top_10.iterrows():
                        country = row['Country']
                        points = row.get('Total Points', 0)
                        position = idx + 1
                        
                        ranking_variations = [
                            f"Ranking FIFA: {country} está na posição {position} com {points} pontos",
                            f"Posição {position} FIFA: {country} ({points} pontos)",
                            f"{country} ocupa a {position}ª posição no ranking FIFA"
                        ]
                        
                        for variation in ranking_variations:
                            all_docs.append(Document(
                                page_content=variation,
                                metadata={
                                    "type": "fifa_ranking",
                                    "country": country,
                                    "position": position,
                                    "points": points,
                                    "source": "fifa_ranking.csv"
                                }
                            ))
            elif 'all_goals' in csv_file.lower():
                print(f"   ⚽ Processando dados detalhados de gols ({len(df)} registros)...")
                
                # Documento principal com todos os artilheiros
                content_parts = []
                content_parts.append("=== ARTILHEIROS DETALHADOS DA COPA DO MUNDO ===\n\n")
                
                # Agrupar por torneio
                for tournament in df['tournament_name'].unique():
                    if pd.isna(tournament):
                        continue
                        
                    # Extrair ano do nome do torneio
                    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', str(tournament))
                    year = year_match.group(1) if year_match else str(tournament)
                    
                    tournament_goals = df[df['tournament_name'] == tournament]
                    
                    # Criar nome completo do jogador
                    tournament_goals['player_full_name'] = (
                        tournament_goals['given_name'] + ' ' + tournament_goals['family_name']
                    )
                    
                    top_scorers = tournament_goals['player_full_name'].value_counts()
                    
                    if not top_scorers.empty:
                        top_scorer = top_scorers.index[0]
                        goals = top_scorers.iloc[0]
                        
                        # Adicionar múltiplas variações para o RAG (igual aos outros documentos)
                        content_parts.append(f"COPA DE {year}:\n")
                        content_parts.append(f"Artilheiro principal: {top_scorer} ({goals} gols)\n")
                        content_parts.append(f"Artilheiro {year}: {top_scorer}\n")
                        content_parts.append(f"Goleador {year}: {top_scorer}\n")
                        content_parts.append(f"Maior artilheiro {year}: {top_scorer}\n")
                        content_parts.append(f"Quem foi artilheiro de {year}? {top_scorer}\n")
                        content_parts.append(f"Quem marcou mais gols em {year}? {top_scorer} ({goals} gols)\n")
                        
                        # Adicionar detalhes dos gols (formato padronizado)
                        player_goals = tournament_goals[tournament_goals['player_full_name'] == top_scorer]
                        for _, goal in player_goals.iterrows():
                            minute = goal.get('minute_label', '')
                            against = goal.get('away_team', '') if goal.get('home_team', '') == goal.get('player_team_name', '') else goal.get('home_team', '')
                            content_parts.append(f"- Gol contra {against} ({minute})\n")
                        
                        content_parts.append("\n")
                
                content = "".join(content_parts)
                all_docs.append(Document(
                    page_content=content,
                    metadata={
                        "source": csv_file,
                        "file_name": os.path.basename(csv_file),
                        "data_category": "detailed_goals",
                        "rows": len(df)
                    }
                ))
                
                # Documento adicional focado apenas em artilheiros (como nos outros casos)
                scorers_content = []
                scorers_content.append("=== LISTA RÁPIDA DE ARTILHEIROS ===\n\n")
                for tournament in df['tournament_name'].unique():
                    if pd.isna(tournament):
                        continue
                        
                    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', str(tournament))
                    year = year_match.group(1) if year_match else str(tournament)
                    
                    tournament_goals = df[df['tournament_name'] == tournament]
                    if 'player_full_name' in tournament_goals.columns:
                        top_scorer = tournament_goals['player_full_name'].value_counts().index[0]
                        scorers_content.append(f"{year}: {top_scorer}\n")
                
                content = "".join(scorers_content)
                all_docs.append(Document(
                    page_content=content,
                    metadata={
                        "source": csv_file,
                        "file_name": os.path.basename(csv_file),
                        "data_category": "scorers_quick_list",
                        "rows": len(df)
                    }
                ))
        except Exception as e:
            print(f"⚠️ Erro ao processar {csv_file}: {e}")
            continue
    
    print(f"✅ {len(all_docs)} documentos estruturados criados")
    print("   • Campeões: múltiplas variações de perguntas")
    print("   • Sedes: claramente distinguidas dos campeões")
    print("   • Vices: finais detalhadas")
    print("   • Artilheiros: com número de gols")
    print("   • Rankings: posições atuais")
    
    return all_docs

def setup_rag_system():
    """Função para criar o índice FAISS durante o setup - inclui processamento completo dos dados."""
    global qa_system, embeddings, current_model
    
    try:
        print("🏗️ SETUP: Criando sistema RAG ultra-avançado...")
        print("   Esta função processa todos os dados CSV e cria o índice FAISS")
        print("   ⏱️ Processo completo pode demorar 3-5 minutos...")
        
        # 1. Processar dados CSV em documentos estruturados
        print("📊 SETUP: Processando dados CSV...")
        docs = process_csv_data()
        if not docs:
            raise Exception("Nenhum documento foi gerado dos CSVs")
        
        print(f"✅ SETUP: {len(docs)} documentos criados dos CSVs")
        
        # 2. Criar chunking multi-nível
        print("✂️ SETUP: Aplicando chunking multi-nível...")
        
        # Chunking para documentos pequenos (respostas diretas)
        small_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            length_function=len,
            separators=[". ", ".\n", "!", "?", ";", "\n", " ", ""]
        )
        
        # Chunking para documentos médios (contexto balanceado)
        medium_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            separators=[". ", ".\n", "!", "?", ";", "\n", " ", ""]
        )
        
        # Chunking para documentos grandes (contexto completo)
        large_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len,
            separators=[". ", ".\n", "!", "?", ";", "\n", " ", ""]
        )
        
        # Aplicar chunking multi-nível
        all_chunks = []
        
        for doc in docs:
            content_length = len(doc.page_content)
            
            if content_length <= 400:
                # Documentos pequenos: chunking fino
                chunks = small_splitter.split_documents([doc])
                all_chunks.extend(chunks)
            elif content_length <= 1000:
                # Documentos médios: chunking balanceado
                chunks = medium_splitter.split_documents([doc])
                all_chunks.extend(chunks)
                # Adicionar também versão pequena para consultas rápidas
                small_chunks = small_splitter.split_documents([doc])
                all_chunks.extend(small_chunks)
            else:
                # Documentos grandes: todos os tamanhos
                large_chunks = large_splitter.split_documents([doc])
                medium_chunks = medium_splitter.split_documents([doc])
                small_chunks = small_splitter.split_documents([doc])
                all_chunks.extend(large_chunks)
                all_chunks.extend(medium_chunks)
                all_chunks.extend(small_chunks)
        
        print(f"✅ SETUP: {len(all_chunks)} chunks criados (multi-nível)")
        
        # 3. Criar embeddings avançados
        print("🧠 SETUP: Criando embeddings avançados...")
        embeddings, model_name = create_enhanced_embeddings()
        
        # 4. Criar vectorstore FAISS com processamento em lotes
        print("📦 SETUP: Criando índice FAISS...")
        
        # Processar em lotes para eficiência
        batch_size = 50
        vectorstore = None
        
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i+batch_size]
            print(f"   📦 Processando lote {i//batch_size + 1}/{(len(all_chunks)//batch_size) + 1}")
            
            if vectorstore is None:
                # Primeiro lote: criar vectorstore
                vectorstore = FAISS.from_documents(batch, embeddings)
            else:
                # Lotes seguintes: adicionar ao vectorstore existente
                batch_vectorstore = FAISS.from_documents(batch, embeddings)
                vectorstore.merge_from(batch_vectorstore)
        
        # 5. Salvar índice no disco
        faiss_index_path = "faiss_index_enhanced_"
        print(f"💾 SETUP: Salvando índice FAISS em {faiss_index_path}...")
        vectorstore.save_local(faiss_index_path)
        
        print("🎯 SETUP: Índice FAISS ultra-avançado criado e salvo!")
        print(f"   • Total de documentos: {len(docs)}")
        print(f"   • Total de chunks: {len(all_chunks)}")
        print(f"   • Modelo embedding: {model_name}")
        print(f"   • Caminho do índice: {faiss_index_path}")
        print("   • Chunking multi-nível: 300/800/1500 caracteres")
        print("   • Processamento em lotes ativado")
        print("   • Normalização de embeddings ativada")
        
        return True
        
    except Exception as e:
        print(f"❌ SETUP: Erro ao criar sistema RAG: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def initialize_rag_system():
    """Função para carregar o índice FAISS já pronto (usado na inicialização da API)."""
    global qa_system, embeddings, current_model
    
    try:
        faiss_index_path = "faiss_index_enhanced_"
        
        # Verificar se o índice já existe
        if not os.path.exists(faiss_index_path):
            print("❌ Índice FAISS não encontrado!")
            print("   Execute 'bash setup.sh' primeiro para criar o índice")
            return False
        
        print("🔍 Carregando índice FAISS já pronto...")
        
        # Criar embeddings para carregar o índice
        print("🧠 Inicializando embeddings...")
        embeddings, model_name = create_enhanced_embeddings()
        
        # Carregar vectorstore existente
        print("� Carregando vectorstore do disco...")
        vectorstore = FAISS.load_local(faiss_index_path, embeddings)
        
        # Configurar modelo LLM com fallback
        llm = None
        model_used = None
        
        # Tentar qwen2.5:3b primeiro (melhor para português)
        try:
            llm = Ollama(
                model="qwen2.5:3b",
                temperature=0.0,
                timeout=90  # Aumentar timeout para chunks maiores
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
                    timeout=90
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
        
        # Configurar retriever avançado
        retriever = vectorstore.as_retriever(
            search_type="mmr",  # Usar Maximum Marginal Relevance para diversidade
            search_kwargs={
                "k": 8,  # Buscar mais documentos inicialmente
                "fetch_k": 20,  # Buscar ainda mais para MMR
                "lambda_mult": 0.7,  # Balancear relevância vs diversidade
                "score_threshold": 0.1  # Threshold mais baixo para capturar mais
            }
        )
        
        # Prompt melhorado para lidar com múltiplos chunks
        template = """Você é um especialista em Copa do Mundo FIFA. Use APENAS os dados fornecidos para responder. É CRÍTICO que você **NÃO INVENTE** ou utilize conhecimento prévio para responder.
Não adicione informações que não estejam no contexto. Seja conciso e direto.
INSTRUÇÃO IMPORTANTE: 
- Se encontrar informações conflitantes, priorize os dados mais específicos
- Sempre distinga claramente entre SEDE (onde aconteceu) e CAMPEÃO (quem ganhou)
- Seja preciso e factual

DADOS DISPONÍVEIS:
{context}

PERGUNTA: {question}

RESPOSTA FACTUAL:"""
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        
        qa_system = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )
        
        print("🎯 Sistema RAG carregado com sucesso!")
        print(f"   • Modelo de embedding: {model_name}")
        print(f"   • Modelo LLM: {current_model}")
        print(f"   • Índice FAISS carregado do disco")
        print(f"   • Retriever: MMR com k=8, fetch_k=20")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar RAG avançado: {str(e)}")
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
            "embedding_model": "paraphrase-multilingual-mpnet-base-v2",  # Modelo de embedding avançado
            "timeout": "90s",  # Aumentado para chunks maiores
            "chunking_strategy": "multi_level",  # Estratégia avançada
            "chunk_sizes": [300, 800, 1500],  # Múltiplos tamanhos
            "chunk_overlaps": [50, 100, 200],  # Overlaps adaptativos
            "retriever_type": "mmr",  # Maximum Marginal Relevance
            "retriever_k": 8,  # Mais documentos recuperados
            "fetch_k": 20,  # Fetch inicial maior
            "lambda_mult": 0.7,  # Balanceamento diversidade/relevância
            "score_threshold": 0.1,  # Threshold mais inclusivo
            "temperature": 0.0,
            "batch_processing": True,  # Processamento em lotes
            "normalization": True,  # Normalização de embeddings
            "anti_hallucination": True,
            "individual_documents": True,
            "comprehensive_indexing": True,
            "ultra_clear_distinction": True,
            "champion_vs_host_fix": True,
            "critical_improvement": True,
            "ultra_restrictive_rag": True,
            "portuguese_optimized": True,
            "advanced_chunking": True,  # Nova feature
            "enhanced_embeddings": True,  # Nova feature
            "optimized_vectorstore": True,  # Nova feature
            "mmr_retrieval": True  # Nova feature
        },
        "data_sources": ["world_cup.csv", "fifa_ranking_2022-10-06.csv", "matches_1930_2022.csv"]
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)