from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.troubles.router import router as troubles_router

app = FastAPI()
app.include_router(troubles_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
