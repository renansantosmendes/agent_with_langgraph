import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")  # Altere para "chromadb.EphemeralClient()" para rodar em memória

collection = chroma_client.get_or_create_collection(name="test_collection")

collection.add(
    ids=["doc1", "doc2"],
    documents=["Este é um exemplo de documento", "Outro documento de teste"],
    metadatas=[{"source": "site1"}, {"source": "site2"}]
)

results = collection.query(
    query_texts=["exemplo"],
    n_results=2
)

print(results)
