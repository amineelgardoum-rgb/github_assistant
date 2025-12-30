from langchain_huggingface import HuggingFaceEmbeddings

from langchain_chroma import Chroma


def get_vector_store(documents, repo_id):
    """get the stored vector (embedding from the chroma db for a fast retrieving process)

    Args:
        documents (str): the documents from the repo_dir 
        repo_id (str): the id of the repo which is the repo stored in 

    Returns:
       vector_store (str): the embedding of the documents vectors
    """
    persist_dir = f"./chroma_langchain_db/{repo_id}"

    embeddings =HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = Chroma(
        collection_name=repo_id,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    if vector_store._collection.count() == 0:
        print("Building embeddings (first time)...")

        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        vector_store.add_texts(texts=texts, metadatas=metadatas)
    else:
        print("Using cached embeddings")

    return vector_store
