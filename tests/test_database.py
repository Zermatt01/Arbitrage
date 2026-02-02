#!/usr/bin/env python3
"""
Script de test de connexion PostgreSQL - Étape 1.4
==================================================

Vérifie que PostgreSQL est installé et que la connexion fonctionne.

Usage:
    python test_database.py
"""

import sys


def print_header(text):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Affiche un message de succès"""
    print(f"✅ {text}")


def print_error(text):
    """Affiche un message d'erreur"""
    print(f"❌ {text}")


def print_info(text):
    """Affiche une information"""
    print(f"ℹ️  {text}")


def print_warning(text):
    """Affiche un avertissement"""
    print(f"⚠️  {text}")


def test_psycopg2_import():
    """Teste l'import de psycopg2"""
    print_header("Test Import psycopg2")
    
    try:
        import psycopg2
        print_success(f"psycopg2 installé (version {psycopg2.__version__})")
        return True
    except ImportError:
        print_error("psycopg2 non installé")
        print_info("Installez-le avec: pip install psycopg2-binary")
        return False


def test_sqlalchemy_import():
    """Teste l'import de SQLAlchemy"""
    print_header("Test Import SQLAlchemy")
    
    try:
        import sqlalchemy
        print_success(f"SQLAlchemy installé (version {sqlalchemy.__version__})")
        return True
    except ImportError:
        print_error("SQLAlchemy non installé")
        print_info("Installez-le avec: pip install sqlalchemy")
        return False


def test_config_import():
    """Teste l'import de la configuration"""
    print_header("Test Configuration Database")
    
    try:
        from config.config import Config
        
        print_info(f"DB Host: {Config.DB_HOST}")
        print_info(f"DB Port: {Config.DB_PORT}")
        print_info(f"DB Name: {Config.DB_NAME}")
        print_info(f"DB User: {Config.DB_USER}")
        print_info(f"DB Password: {'*' * len(Config.DB_PASSWORD) if Config.DB_PASSWORD else 'Non configuré'}")
        
        if not Config.DB_PASSWORD:
            print_warning("Mot de passe de base de données non configuré dans .env")
            return False
        
        print_success("Configuration chargée")
        return True
        
    except ImportError as e:
        print_error(f"Impossible de charger la config: {e}")
        return False


def test_connection_psycopg2():
    """Teste la connexion directe avec psycopg2"""
    print_header("Test Connexion PostgreSQL (psycopg2)")
    
    try:
        import psycopg2
        from config.config import Config
        
        # Tenter la connexion
        print_info("Tentative de connexion...")
        
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            connect_timeout=5
        )
        
        print_success("Connexion réussie!")
        
        # Tester une requête simple
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_info(f"PostgreSQL: {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print_error(f"Erreur de connexion: {e}")
        
        # Diagnostics
        print("\n🔍 Diagnostics:")
        
        if "password authentication failed" in str(e):
            print_warning("Mot de passe incorrect")
            print_info("Vérifiez DB_PASSWORD dans votre fichier .env")
        elif "could not connect to server" in str(e):
            print_warning("Impossible de se connecter au serveur PostgreSQL")
            print_info("Vérifiez que PostgreSQL est démarré")
            print_info("Commande: services.msc (cherchez PostgreSQL)")
        elif "database" in str(e) and "does not exist" in str(e):
            print_warning("La base de données n'existe pas")
            print_info("Exécutez le script init_database.sql")
        elif "role" in str(e) and "does not exist" in str(e):
            print_warning("L'utilisateur n'existe pas")
            print_info("Exécutez le script init_database.sql")
        
        return False
        
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return False


def test_connection_sqlalchemy():
    """Teste la connexion avec SQLAlchemy"""
    print_header("Test Connexion PostgreSQL (SQLAlchemy)")
    
    try:
        from sqlalchemy import create_engine, text
        from config.config import Config
        
        # Créer l'engine
        print_info("Création de l'engine SQLAlchemy...")
        engine = create_engine(Config.DATABASE_URL, echo=False)
        
        # Tester la connexion
        print_info("Test de connexion...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                print_success("Connexion SQLAlchemy réussie!")
                
                # Informations supplémentaires
                result = connection.execute(text("SELECT current_database(), current_user"))
                db_name, db_user = result.fetchone()
                print_info(f"Base de données: {db_name}")
                print_info(f"Utilisateur: {db_user}")
                
                return True
        
        return False
        
    except Exception as e:
        print_error(f"Erreur SQLAlchemy: {e}")
        return False


def test_database_writable():
    """Teste qu'on peut créer une table de test"""
    print_header("Test Permissions (Création Table)")
    
    try:
        from sqlalchemy import create_engine, text
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL, echo=False)
        
        with engine.connect() as connection:
            # Supprimer la table de test si elle existe
            connection.execute(text("DROP TABLE IF EXISTS test_table"))
            connection.commit()
            
            # Créer une table de test
            print_info("Création d'une table de test...")
            connection.execute(text("""
                CREATE TABLE test_table (
                    id SERIAL PRIMARY KEY,
                    test_data VARCHAR(100)
                )
            """))
            connection.commit()
            
            print_success("Table de test créée")
            
            # Insérer des données
            print_info("Insertion de données...")
            connection.execute(text("""
                INSERT INTO test_table (test_data) 
                VALUES ('Test 1'), ('Test 2')
            """))
            connection.commit()
            
            print_success("Données insérées")
            
            # Lire les données
            result = connection.execute(text("SELECT COUNT(*) FROM test_table"))
            count = result.fetchone()[0]
            print_info(f"{count} lignes dans la table de test")
            
            # Nettoyer
            connection.execute(text("DROP TABLE test_table"))
            connection.commit()
            
            print_success("Permissions OK - lecture/écriture fonctionnelles")
            
            return True
            
    except Exception as e:
        print_error(f"Erreur de permissions: {e}")
        return False


def test_extensions():
    """Vérifie les extensions PostgreSQL disponibles"""
    print_header("Test Extensions PostgreSQL")
    
    try:
        from sqlalchemy import create_engine, text
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL, echo=False)
        
        with engine.connect() as connection:
            # Vérifier pgcrypto
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto'
                )
            """))
            
            has_pgcrypto = result.fetchone()[0]
            
            if has_pgcrypto:
                print_success("Extension pgcrypto installée")
            else:
                print_warning("Extension pgcrypto non installée (optionnel)")
            
            # Lister toutes les extensions
            result = connection.execute(text("""
                SELECT extname, extversion 
                FROM pg_extension 
                ORDER BY extname
            """))
            
            extensions = result.fetchall()
            if extensions:
                print_info(f"{len(extensions)} extensions disponibles:")
                for ext_name, ext_version in extensions:
                    print(f"  - {ext_name} (v{ext_version})")
            
            return True
            
    except Exception as e:
        print_error(f"Erreur lors de la vérification des extensions: {e}")
        return False


def print_connection_info():
    """Affiche les informations de connexion"""
    print_header("Informations de Connexion")
    
    try:
        from config.config import Config
        
        print("\n📋 Configuration actuelle:")
        print(f"  Host:     {Config.DB_HOST}")
        print(f"  Port:     {Config.DB_PORT}")
        print(f"  Database: {Config.DB_NAME}")
        print(f"  User:     {Config.DB_USER}")
        print(f"  URL:      postgresql://{Config.DB_USER}:****@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        
        print("\n💡 Pour vous connecter manuellement:")
        print(f"  psql -h {Config.DB_HOST} -p {Config.DB_PORT} -U {Config.DB_USER} -d {Config.DB_NAME}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def print_summary(results):
    """Affiche le résumé des tests"""
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n✅ Tests réussis: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 PostgreSQL configuré et fonctionnel!")
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 1.4 est COMPLÈTE ✅")
        print("  2. Vous pouvez passer à l'Étape 1.5")
        print("  3. Dites 'Étape 1.5' pour créer les tables")
        
        return True
    else:
        print_error("❌ Certains tests ont échoué")
        print("\n🔧 Actions requises:")
        
        for test_name, result in results.items():
            if not result:
                print(f"  - Corriger: {test_name}")
        
        print("\n💡 Aide:")
        print("  - Vérifiez que PostgreSQL est démarré")
        print("  - Vérifiez le fichier .env (DB_PASSWORD)")
        print("  - Exécutez init_database.sql si la base n'existe pas")
        
        return False


def main():
    """Fonction principale"""
    print("\n" + "🗄️  TEST POSTGRESQL - ÉTAPE 1.4".center(60))
    
    results = {
        "Import psycopg2": test_psycopg2_import(),
        "Import SQLAlchemy": test_sqlalchemy_import(),
        "Configuration": test_config_import()
    }
    
    # Si les imports de base passent, tester la connexion
    if all(results.values()):
        results["Connexion psycopg2"] = test_connection_psycopg2()
        results["Connexion SQLAlchemy"] = test_connection_sqlalchemy()
        
        # Si la connexion marche, tester les permissions
        if results["Connexion SQLAlchemy"]:
            results["Permissions écriture"] = test_database_writable()
            results["Extensions"] = test_extensions()
            print_connection_info()
    
    success = print_summary(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
