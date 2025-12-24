def retrieve_docs(question: str, retriever):
    docs = retriever.invoke(question)
    if not docs:
        print("No documents retrieved")
    return docs
