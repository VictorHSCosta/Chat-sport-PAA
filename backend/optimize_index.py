#!/usr/bin/env python3

import os
import shutil
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def recreate_optimized_index():
    """Recria o índice FAISS com configurações otimizadas para performance"""
    
    print("🚀 Recriando índice FAISS otimizado para performance...")
    
    # Remove índice existente
    faiss_index_path = "faiss_index_"
    if os.path.exists(faiss_index_path):
        print("🗑️ Removendo índice existente...")
        shutil.rmtree(faiss_index_path)
    
    # Carrega dados
    print("📁 Carregando dados...")
    with open("data.txt", 'r', encoding='utf-8') as f:
        text = f.read()
    documents = [Document(page_content=text, metadata={"source": "data.txt"})]
    
    # Chunks pequenos para performance
    print("✂️ Criando chunks otimizados (300 chars)...")
    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=20, separator="\n")
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
