from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.load_repo_router import router as load_router
from api.routers.ask_router import router as ask_router
from api.routers.health_router import router as health_router
from api.routers.main_router import router as main_router
import uvicorn
import os 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router,tags=["ask"])
app.include_router(load_router,tags=["load"])
app.include_router(health_router,tags=["health"])
app.include_router(main_router)

if __name__=="__main__":
    host=os.getenv("HOST","127.0.0.1")
    port=int(os.getenv("PORT","8000"))
    reload=os.getenv("ENV","development")=="development"
    uvicorn.run("main:app",host=host,port=port,reload=reload)