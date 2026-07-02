import sys
import os

# Allow this script to import database.py and models.py from backend/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database import engine
from models import Base

Base.metadata.create_all(engine)
print("Tables created successfully: players, matches, deliveries")