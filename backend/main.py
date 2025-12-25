from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loaders.repo_loader import clone_repo, load_repo_files, split_code_docs
from embeddings.vector_store import get_vector_store
from llm.llm_chain import answer_from_docs
from utils.retriever_utils import retrieve_docs
import uvicorn
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_cache = {}

class LoadRepoRequest(BaseModel):
    repo_url: str

class AskRequest(BaseModel):
    repo_id: str
    question: str

@app.post("/load_repo")
def load_repo_endpoint(req: LoadRepoRequest):
    repo_path, repo_id = clone_repo(req.repo_url)
    docs = load_repo_files(repo_path)
    all_splits = split_code_docs(docs)

    if repo_id in vector_cache:
        vector_store = vector_cache[repo_id]
        msg = "Using cached embeddings"
    else:
        vector_store = get_vector_store(all_splits, repo_id)
        vector_cache[repo_id] = vector_store
        msg = "Created new embeddings"

    return {
        "repo_id": repo_id,
        "num_files": len(docs),
        "num_chunks": len(all_splits),
        "message": msg
    }

@app.post("/ask")
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

if __name__=="__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)