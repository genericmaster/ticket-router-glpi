from fastapi import APIRouter
from pydantic import BaseModel
from src.ticket_router_glpi.db.models import RoutingGroup,Llmconfig
from src.ticket_router_glpi.db.sessions import SessionFactory
from config.providers import  PROVIDERS
config_router = APIRouter()

class RoutingGroupCreate(BaseModel):
    glpi_group_id: int
    glpi_group_name: str
    
class RouterConfig(BaseModel):
    groups: list[RoutingGroupCreate]
    
class LlmConfiguration(BaseModel):
    model_name: str
    provider: str
    system_prompt: str
    

@config_router.get('/setup-status')
def setup_status()->dict:
    with SessionFactory() as session:
        groups =session.query(RoutingGroup).all()
        
        if not groups:
           return  {"configured": False}
        else:
            return  {"configured": True}
        
@config_router.get("/llm")
def llm()->dict:
    with SessionFactory() as session:
        model_config = session.query(Llmconfig).first()
    return {"model_name": model_config.model_name, "base_url": model_config.base_url, "system_prompt": model_config.system_prompt}

@config_router.post("/routing-groups")
def routing_groups(data:RouterConfig):
    with SessionFactory() as session:
        for group in data.groups:
            session.add(RoutingGroup(glpi_group_id =group.glpi_group_id,glpi_group_name =group.glpi_group_name))
        session.commit()
            
    return {"200":"ok"}

@config_router.get("/routing-groups")
def get_routing_groups()->list:
    with SessionFactory() as session:
            groups =session.query(RoutingGroup).all()
            groups_dict=[{"glpi_group_name": g.glpi_group_name, "glpi_group_id": g.glpi_group_id} for g in groups]
            return groups_dict
                       
@config_router.put("/llm")
def update_llm_config(data:LlmConfiguration):
    with SessionFactory() as session:
        update_config = session.query(Llmconfig).first()
        update_config.model_name = data.model_name
        update_config.system_prompt =data.system_prompt
        if data.provider in PROVIDERS:
            update_config.base_url = PROVIDERS[data.provider]
        session.commit()
            
    return {"200":"ok"}
        
            
    
        
