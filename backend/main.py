import asyncio
from services.database_service import delete_all_media_path_regex
import uvicorn
from fastapi import FastAPI, WebSocket
from concurrent.futures import ThreadPoolExecutor
from services.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.include_router(router, prefix='/api')


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8001, reload=True)
