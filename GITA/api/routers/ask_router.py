from fastapi import APIRouter
from api.schemas.askRequest import AskRequest
from llm.llm_chain import answer_from_docs,llm_provider
from utils.retriever_utils import retrieve_docs
from api.vector_cache import vector_cache


router=APIRouter()
@router.post("/ask")
def ask_question(req: AskRequest):
    """Ask question endpoint to ask questions about the repo"""
    print(f"Received question: {req.question}")
    vector_store = vector_cache.get(req.repo_id)
    
    if not vector_store:
        return {"error": "Repo not loaded"}

    print("Retrieving documents...")
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 100})
    docs = retrieve_docs(req.question, retriever)
    
    print(f"✅ Retrieved {len(docs)} chunks from documents")
    print(f"Using the llm provider:{llm_provider}.")
    
    print("Generating answer from LLM...")
    answer, sources = answer_from_docs(docs, req.question)
    
    print(f"📚 Sources used: {len(sources)} unique files")
    for src in sources:
        print(f"   - {src}")
    
    # ✅ SIMPLEST: Just get the repo_path from metadata (it's already clean)
    cleaned_sources = []
    for doc in docs:
        repo_path = doc.metadata.get('repo_path') or doc.metadata.get('file_name')
        if repo_path and repo_path not in cleaned_sources:
            cleaned_sources.append(repo_path)
    
    return {
        "answer": answer,
        "sources": cleaned_sources,  # Now shows all files!
        "total_chunks": len(docs)
    }