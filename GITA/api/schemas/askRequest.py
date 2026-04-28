from pydantic import BaseModel
class AskRequest(BaseModel):
    repo_id: str
    question: str