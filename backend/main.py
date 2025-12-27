from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.ask_router import router as ask_router
from api.routers.load_repo_router import router as load_router
import uvicorn
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ask_router,tags=["ask"])
app.include_router(load_router,tags=["load"])

if __name__=="__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)