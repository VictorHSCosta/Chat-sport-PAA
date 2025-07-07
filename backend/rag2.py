from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.llms.ollama import Ollama

llm = Ollama(model="mistral")

documents = SimpleDirectoryReader("data").load_data()

service_context = ServiceContext.from_defaults(llm=llm)

index = VectorStoreIndex.from_documents(documents, service_context=service_context)

query_engine = index.as_query_engine()

while True:
    pergunta = input("Digite sua pergunta: ")
    resposta = query_engine.query(pergunta)
    print("🧠", resposta.response)  