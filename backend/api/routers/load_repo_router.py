from fastapi import APIRouter
from api.schemas.askRequest import AskRequest
from llm.llm_chain import answer_from_docs
from utils.retriever_utils import retrieve_docs
from api.vector_cache import vector_cache
router=APIRouter()
@router.post("/ask")
def ask_question(req: AskRequest):
    print(f"Received question: {req.question}") # Debug log
    vector_store = vector_cache.get(req.repo_id)
    
    if not vector_store:
        return {"error": "Repo not loaded"}

    print("Retrieving documents...")
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})
    docs = retrieve_docs(req.question, retriever)
    
    print("Generating answer from LLM (this may take a while)...")
    answer, sources = answer_from_docs(docs, req.question)
    
    print("Generation complete!")
    sources = [ "\\".join(src.split("\\")[2:]) for src in sources ]
    return {"answer": answer, "sources": sources}