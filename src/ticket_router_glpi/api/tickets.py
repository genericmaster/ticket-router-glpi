from fastapi import APIRouter,Request
import asyncio
import threading
import queue
from src.ticket_router_glpi.services.router import update,route
q = queue.Queue()
ticket_router = APIRouter()

async def async_process_ticket(body: dict):
    try:
        print("process_ticket started", body)
        ticket_id = body["item"]["id"]
        print("calling route")
        group_id = await route(data=body)
        print("route returned", group_id)
        await update(ticket_id=ticket_id, group_id=group_id)
        print("update done")
    except Exception as e:
        print("ERROR:", type(e), e)
        

def run_in_thread(body):
    print("THREAD STARTED")
    asyncio.run(async_process_ticket(body))

@ticket_router.post("/glpi")
async def glpi(data: Request):
    body = await data.json()
    thread = threading.Thread(target=run_in_thread, args=(body,))
    thread.daemon = True
    thread.start()
    return {"200": "ok"}


@ticket_router.post("/glpi")
async def add_to_queue(body:dict)->dict:
    q.put(body)
    return {"200": "ok"}
