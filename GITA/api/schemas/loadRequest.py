from pydantic import BaseModel
class LoadRepoRequest(BaseModel):
    repo_url: str