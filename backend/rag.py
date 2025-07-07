from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

def load_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [{"page_content": text}]

documents = load_text_file("data.txt")  

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
docs = text_splitter.split_documents(documents)

embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cuda"} 
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name, model_kwargs=model_kwargs)

vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("faiss_index_")
persisted_vectorstore = FAISS.load_local("faiss_index_", embeddings, allow_dangerous_deserialization=True)

llm = Ollama(model="llama3.1")

retriever = persisted_vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

print("\n[Type your query or 'exit' to quit]\n")
while True:
    query = input("Query: ")
    if query.lower() in ("exit", "quit"):
        print("Exiting.")
        break
    response = qa.run(query)
    print("\nAnswer:", response, "\n")
