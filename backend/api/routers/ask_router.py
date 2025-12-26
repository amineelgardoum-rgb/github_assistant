from fastapi import APIRouter
from api.schemas.loadRequest import LoadRepoRequest
from loaders.repo_loader import clone_repo, load_repo_files, split_code_docs
from embeddings.vector_store import get_vector_store
from api.vector_cache import vector_cache
router=APIRouter()
@router.post("/load_repo")
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
