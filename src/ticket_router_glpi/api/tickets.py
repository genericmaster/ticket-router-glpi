from fastapi import APIRouter,Request
import queue
from src.ticket_router_glpi.services.router import update,route
q = queue.Queue()
ticket_router = APIRouter()

def process_ticket(body: dict):
    try:
        print("process_ticket started", body)
        ticket_id = body["item"]["id"]
        print("calling route")
        group_id = route(data=body)
        print("route returned", group_id)
        update(ticket_id=ticket_id, group_id=group_id)
        print("update done")
    except Exception as e:
        print("ERROR:", type(e), e)
         
@ticket_router.post("/glpi")
async def add_to_queue(data: Request):
    body = await data.json()
    q.put(body)
    return {"200": "ok"}

def worker():
    while True:
        body =q.get()
        process_ticket(body)
        q.task_done()


    


