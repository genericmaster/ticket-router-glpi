
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


"""prevents having to reference or create the engine explicitly at every  file that needs a database query"""
engine= create_engine("sqlite:///data/db.sqlite")
SessionFactory = sessionmaker(engine)