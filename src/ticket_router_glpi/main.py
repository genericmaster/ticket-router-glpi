import threading
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from src.ticket_router_glpi.db.models import Base
from src.ticket_router_glpi.db.sessions import engine
from src.ticket_router_glpi.db.seed import add_model
from src.ticket_router_glpi.api.tickets import ticket_router,worker
from src.ticket_router_glpi.api.config import config_router

def run_in_thread():
    print("thread_started")
    threading.Thread(target=worker,daemon=True).start()

@asynccontextmanager
async def lifespan(app:FastAPI):
    """makes sure that all databases are started first at app runtime and that a base language model is provided to user at runtime """
    #startup db
    Base.metadata.create_all(engine)
    add_model()
    run_in_thread()
    yield
    
app = FastAPI(lifespan=lifespan)
app.include_router(ticket_router)
app.include_router(config_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("frontend/router_dashboard.html", "r") as f:
        return f.read()