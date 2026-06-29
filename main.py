from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging


from router.routes import router
from websocket.WebsocketManager import WebsocketManger
from bridge.WorkerEventBridge import WorkerEventBridge
from all_models.ApplicationServices import ApplicationServices

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@asynccontextmanager
async def lifespan(app:FastAPI):

    loop = asyncio.get_running_loop()
    app.state.services = ApplicationServices(event_bridge=WorkerEventBridge(event_loop=loop),websocket_manager=WebsocketManger())

    logging.info("Application started")

    yield

    logging.info("Application shutting down")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# To get all the logs with running "uvicorn main:app --reload > my_server_logs.txt 2>&1"