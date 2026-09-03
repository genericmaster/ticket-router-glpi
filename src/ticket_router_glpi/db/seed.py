from src.ticket_router_glpi.db.models import Llmconfig
from src.ticket_router_glpi.db.sessions import SessionFactory

def add_model()->None:
    """checks if llmconfig is empty if so then adds a base model and provider"""
    with SessionFactory() as session:
        existing = session.query(Llmconfig).first()
        if existing is  None:
            config = Llmconfig(model_name="qwen3.5:9b", base_url="http://host.docker.internal:11434/v1/chat/completions",is_active=True,system_prompt="")
            session.add(config)
            session.commit()
            