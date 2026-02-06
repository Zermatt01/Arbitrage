"""
Database
========

Gestion de la base de données PostgreSQL.
"""

from .db_connection import get_db_connection
from .opportunity_db import OpportunityDB

__all__ = [
    'get_db_connection',
    'OpportunityDB',
]
