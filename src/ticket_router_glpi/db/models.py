from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from typing import Optional

class Base(DeclarativeBase):
    pass

class Llmconfig(Base):
    __tablename__  ="llm_config"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str]
    is_active : Mapped[bool]
    base_url : Mapped[str]
    system_prompt :  Mapped[Optional[str]]
    
    
class RoutingGroup(Base):
    __tablename__ = "routing_group"
    id : Mapped[int]= mapped_column(primary_key=True)
    glpi_group_id :Mapped[int]
    glpi_group_name : Mapped[str]