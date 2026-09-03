import os
from dotenv import load_dotenv
from httpx import AsyncClient
import json
from  src.ticket_router_glpi.utils.cleaning import clean
from src.ticket_router_glpi.llm.client import  call_llm
from src.ticket_router_glpi.db.sessions import SessionFactory
from src.ticket_router_glpi.db.models import Llmconfig,RoutingGroup

load_dotenv()
APP_TOKEN = os.getenv("APP_TOKEN")
USER_TOKEN = os.getenv("USER_TOKEN")
GLPI_BASE = os.getenv("GLPI_BASE")


async def route(data):
    content =data["item"]["content"]
    cleaned_content=clean(content=content)
    with SessionFactory() as session:
            config = session.query(Llmconfig).first()
            glpi_groups=session.query(RoutingGroup).all()
            
    glpi_groups_info = [{"name": group.glpi_group_name, "id": group.glpi_group_id} for group in glpi_groups]
    
    base_system_prompt = f""" You are a ticket routing assistant. Your job is to read a support ticket and assign it to exactly one of the following groups:{glpi_groups_info}
                             -You must respond with only a JSON object in this exact format: {{"_groups_id_assign": <id>}} 
                             -Where <id> is the integer ID of the group. No explanation, no extra text, nothing outside the JSON object."""
                             
    system_prompt = base_system_prompt + "\n" +config.system_prompt
    print("calling LLM with", config.base_url, config.model_name)
    response = await call_llm(model_name=config.model_name,system_prompt=system_prompt,prompt=cleaned_content,model_url=config.base_url)
    return response
                                      
                                      
        
async def update(ticket_id:int,group_id:str):
    body = json.loads(group_id)
    session_token = await get_session_token()
    
    async with AsyncClient() as client:
        response = await client.patch(
            f"{GLPI_BASE}/Ticket/{ticket_id}",
            headers={
                "Session-Token": session_token,
                "App-Token": APP_TOKEN,
                "Content-Type": "application/json"
            },
            json={"input": body}
        )
        return {"200":"ok"}
            
                
async def get_session_token():
    async with AsyncClient() as client:
        response = await client.get(
            f"{GLPI_BASE}/initSession",
            headers={
                "Authorization": f"user_token {USER_TOKEN}",
                "App-Token": APP_TOKEN
            }
        )
        print(response.json()["session_token"]) 
        return response.json()["session_token"]   
        
    
    
    
    
    