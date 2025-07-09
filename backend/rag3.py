from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.llms import Ollama  
#import torch

def load_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [Document(page_content=f.read(), metadata={"source": path})]

print("Loading and processing documents...")
documents = load_text_file("data.txt")
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  
docs = text_splitter.split_documents(documents)

print("Loading embeddings...")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5", 
    model_kwargs={"device": 
        #"cuda" if torch.cuda.is_available() else 
        "cpu"}
)

print("Creating vector store...")
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("faiss_index_")

print("Loading TinyLlama...")
llm = Ollama(
    model="tinyllama", 
    temperature=0.3,
    system="Answer in 1-2 sentences using ONLY the context below:"
)

retriever = vectorstore.as_retriever(
    search_type="mmr",  
    search_kwargs={"k": 2} 
)

def ask_local_llm(query, context):
    try:
        return llm.invoke(f"Context:\n{context}\n\nQuestion: {query}")
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("\nLoading vector store...")
    persisted_vectorstore = FAISS.load_local(
        "faiss_index_",
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = persisted_vectorstore.as_retriever(search_kwargs={"k": 2})

    print("\nReady! Ask anything (type 'exit' to quit):")
    while True:
        query = input("\nQuery: ").strip()
        if query.lower() in ("exit", "quit"):
            break
        
        print("Searching for relevant information...")
        docs = retriever.invoke(query)  
        context = "\n---\n".join(doc.page_content for doc in docs)
        
        print("Generating answer...")
        response = ask_local_llm(query, context)
        print(f"\nAnswer: {response}\n")