# Simple script to make the entity relationship diagram for this database
#Krista Longnecker 30 August 2026

from eralchemy2 import render_er
from models import Base  # Import your SQLAlchemy declarative Base from models.py

## Draw from SQLAlchemy base
render_er(Base, 'test_data/erd_from_sqlalchemy2.png')

#Better figures available here (just copy in models.py)
https://sqltoerdiagram.com/sqlalchemy/
