#!/usr/bin/env python3

import os
import shutil
import pandas as pd
import glob
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def load_csv_files(directory_path):
    """Load all CSV files from the specified directory and convert to documents."""
    documents = []
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))
    
    print(f"📊 Encontrados {len(csv_files)} arquivos CSV")
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            file_name = os.path.basename(csv_file)
            
            if 'world_cup' in file_name.lower():
                content = f"FIFA World Cup Data from {file_name}:\n\n"
                for _, row in df.iterrows():
                    content += f"World Cup {row.get('Year', 'Unknown Year')}:\n"
                    content += f"- Host Country: {row.get('Host', 'Unknown')}\n"
                    content += f"- Number of Teams: {row.get('Teams', 'Unknown')}\n"
                    content += f"- Champion: {row.get('Champion', 'Unknown')}\n"
                    content += f"- Runner-up: {row.get('Runner-Up', 'Unknown')}\n"
                    content += f"- Top Scorer: {row.get('TopScorrer', 'Unknown')}\n"
                    content += f"- Total Attendance: {row.get('Attendance', 'Unknown')}\n"
                    content += f"- Average Attendance: {row.get('AttendanceAvg', 'Unknown')}\n"
                    content += f"- Total Matches: {row.get('Matches', 'Unknown')}\n\n"
                    
            elif 'fifa_ranking' in file_name.lower():
                content = f"FIFA World Ranking Data from {file_name}:\n\n"
                for _, row in df.iterrows():
                    content += f"Team: {row.get('team', 'Unknown Team')}\n"
                    content += f"- Country Code: {row.get('team_code', 'Unknown')}\n"
                    content += f"- Association: {row.get('association', 'Unknown')}\n"
                    content += f"- Current Rank: {row.get('rank', 'Unknown')}\n"
                    content += f"- Previous Rank: {row.get('previous_rank', 'Unknown')}\n"
                    content += f"- Current Points: {row.get('points', 'Unknown')}\n"
                    content += f"- Previous Points: {row.get('previous_points', 'Unknown')}\n\n"
                    
            elif 'matches' in file_name.lower():
                content = f"World Cup Matches Data from {file_name}:\n\n"
                content += f"This dataset contains detailed match information from World Cup tournaments.\n"
                content += f"Total matches in dataset: {len(df)}\n\n"
                content += f"Available match data includes: {', '.join(df.columns.tolist())}\n\n"
                
                sample_size = min(15, len(df))
                content += f"Sample of {sample_size} matches:\n"
                for i in range(sample_size):
                    row = df.iloc[i]
                    content += f"Match {i+1}: {str(row.to_dict())}\n"
                    
            else:
                content = f"Data from {file_name}:\n\n"
                content += f"Columns: {', '.join(df.columns.tolist())}\n\n"
                content += df.head(20).to_string(index=False)
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": csv_file,
                    "file_type": "csv",
                    "file_name": file_name,
                    "rows": len(df),
                    "columns": len(df.columns)
                }
            ))
            
            print(f"✅ Carregado {file_name}: {len(df)} linhas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar {csv_file}: {str(e)}")
            continue
    
    return documents

def recreate_optimized_index():
    """Recria o índice FAISS com configurações otimizadas para Copa do Mundo"""
    
    print("🏆 Recriando índice FAISS otimizado para Copa do Mundo...")
    
    # Remove índice existente
    faiss_index_path = "faiss_index_"
    if os.path.exists(faiss_index_path):
        print("🗑️ Removendo índice existente...")
        shutil.rmtree(faiss_index_path)
    
    # Carrega dados CSV da Copa do Mundo
    print("📁 Carregando dados da Copa do Mundo...")
    documents = load_csv_files("wcdataset")
    
    if not documents:
        print("❌ Nenhum arquivo CSV encontrado!")
        return False
    
    # Chunks otimizados para Copa do Mundo
    print("✂️ Criando chunks otimizados (600 chars)...")
    text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=50, separator="\n")
    docs = text_splitter.split_documents(documents)
    print(f"📝 Criados {len(docs)} chunks otimizados")
    
    # Embedding mais rápido
    print("🧠 Carregando modelo de embedding rápido...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    
    # Cria vectorstore otimizado
    print("🏗️ Criando vectorstore otimizado...")
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # Salva
    print("💾 Salvando índice otimizado...")
    vectorstore.save_local(faiss_index_path)
    
    print("✅ Índice FAISS otimizado criado com sucesso!")
    print(f"📊 Estatísticas:")
    print(f"   - Chunks: {len(docs)}")
    print(f"   - Tamanho do chunk: 300 caracteres")
    print(f"   - Sobreposição: 20 caracteres")
    print(f"   - Modelo embedding: all-MiniLM-L6-v2 (rápido)")

if __name__ == "__main__":
    recreate_optimized_index()
