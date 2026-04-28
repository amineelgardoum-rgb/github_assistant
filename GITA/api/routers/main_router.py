from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def main_router():
    """main router"""
    return {"content": "This is the llm serving api to react frontend."}
