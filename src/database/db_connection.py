"""
Database Connection Module
==========================

Gère la connexion à PostgreSQL.

Usage:
    from src.database.db_connection import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # ... utiliser la connexion
    cursor.close()
    conn.close()
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


def get_db_connection():
    """
    Crée et retourne une connexion à PostgreSQL
    
    Returns:
        psycopg2.connection: Connexion à la base de données
    
    Raises:
        psycopg2.Error: Si la connexion échoue
    
    Example:
        >>> conn = get_db_connection()
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT 1")
        >>> cursor.close()
        >>> conn.close()
    """
    # Récupérer les paramètres depuis .env
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'arbitrage_db'),
        'user': os.getenv('DB_USER', 'arbitrage_user'),
        'password': os.getenv('DB_PASSWORD', ''),
    }
    
    # Créer la connexion
    conn = psycopg2.connect(**db_config)
    
    return conn


def get_db_connection_dict():
    """
    Crée une connexion qui retourne des dictionnaires au lieu de tuples
    
    Returns:
        psycopg2.connection: Connexion avec RealDictCursor
    """
    conn = get_db_connection()
    return conn


def test_connection():
    """
    Teste la connexion à la base de données
    
    Returns:
        bool: True si la connexion fonctionne
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tester avec une requête simple
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("✅ Connexion à la base de données OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST CONNEXION DATABASE")
    print("=" * 60)
    
    # Tester la connexion
    test_connection()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
