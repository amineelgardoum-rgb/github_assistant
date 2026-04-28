from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_health():
    """ A health check endpoint ,to verify the api is working or not """
    return {"status": "healthy","content":"the api is working"}
