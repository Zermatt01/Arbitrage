#!/usr/bin/env python3
"""
Script de test des dépendances - Étape 1.2
===========================================

Vérifie que toutes les bibliothèques critiques sont installées
et fonctionnent correctement.

Usage:
    python test_dependencies.py
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


def test_core_libraries():
    """Test des bibliothèques principales"""
    print_header("Test des Bibliothèques Principales")
    
    tests = []
    
    # CCXT (le plus important pour le trading)
    try:
        import ccxt
        print_success(f"CCXT version {ccxt.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"CCXT non installé: {e}")
        tests.append(False)
    
    # Pandas
    try:
        import pandas as pd
        print_success(f"Pandas version {pd.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"Pandas non installé: {e}")
        tests.append(False)
    
    # NumPy
    try:
        import numpy as np
        print_success(f"NumPy version {np.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"NumPy non installé: {e}")
        tests.append(False)
    
    # SQLAlchemy
    try:
        import sqlalchemy
        print_success(f"SQLAlchemy version {sqlalchemy.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"SQLAlchemy non installé: {e}")
        tests.append(False)
    
    # psycopg2 (PostgreSQL)
    try:
        import psycopg2
        print_success(f"psycopg2 installé")
        tests.append(True)
    except ImportError as e:
        print_error(f"psycopg2 non installé: {e}")
        tests.append(False)
    
    return all(tests)


def test_async_libraries():
    """Test des bibliothèques asynchrones"""
    print_header("Test des Bibliothèques Asynchrones")
    
    tests = []
    
    # aiohttp
    try:
        import aiohttp
        print_success(f"aiohttp version {aiohttp.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"aiohttp non installé: {e}")
        tests.append(False)
    
    # websockets
    try:
        import websockets
        print_success(f"websockets installé")
        tests.append(True)
    except ImportError as e:
        print_error(f"websockets non installé: {e}")
        tests.append(False)
    
    # asyncio (standard library)
    try:
        import asyncio
        print_success("asyncio (standard library)")
        tests.append(True)
    except ImportError as e:
        print_error(f"asyncio non disponible: {e}")
        tests.append(False)
    
    return all(tests)


def test_config_libraries():
    """Test des bibliothèques de configuration"""
    print_header("Test des Bibliothèques de Configuration")
    
    tests = []
    
    # python-dotenv
    try:
        import dotenv
        print_success("python-dotenv installé")
        tests.append(True)
    except ImportError as e:
        print_error(f"python-dotenv non installé: {e}")
        tests.append(False)
    
    # pyyaml
    try:
        import yaml
        print_success("PyYAML installé")
        tests.append(True)
    except ImportError as e:
        print_error(f"PyYAML non installé: {e}")
        tests.append(False)
    
    return all(tests)


def test_monitoring_libraries():
    """Test des bibliothèques de monitoring"""
    print_header("Test des Bibliothèques de Monitoring")
    
    tests = []
    
    # prometheus_client
    try:
        import prometheus_client
        print_success("prometheus_client installé")
        tests.append(True)
    except ImportError as e:
        print_error(f"prometheus_client non installé: {e}")
        tests.append(False)
    
    # python-telegram-bot
    try:
        import telegram
        print_success("python-telegram-bot installé")
        tests.append(True)
    except ImportError as e:
        print_error(f"python-telegram-bot non installé: {e}")
        tests.append(False)
    
    return all(tests)


def test_testing_libraries():
    """Test des bibliothèques de test"""
    print_header("Test des Bibliothèques de Test")
    
    tests = []
    
    # pytest
    try:
        import pytest
        print_success(f"pytest version {pytest.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"pytest non installé: {e}")
        tests.append(False)
    
    return all(tests)


def test_ccxt_exchanges():
    """Test que CCXT peut se connecter aux exchanges"""
    print_header("Test de CCXT avec les Exchanges")
    
    try:
        import ccxt
        
        # Lister quelques exchanges disponibles
        exchanges = ['binance', 'kraken', 'coinbasepro']
        
        print_info(f"CCXT supporte {len(ccxt.exchanges)} exchanges")
        print_info(f"Exchanges disponibles pour le projet: {', '.join(exchanges)}")
        
        # Tester l'instanciation d'un exchange
        try:
            binance = ccxt.binance()
            print_success(f"Exchange Binance instancié: {binance.id}")
            
            # Tester la récupération des marchés (sans authentification)
            print_info("Test de récupération des marchés disponibles...")
            markets = binance.load_markets()
            print_success(f"Binance: {len(markets)} paires de trading disponibles")
            
            # Afficher quelques paires BTC
            btc_pairs = [symbol for symbol in markets.keys() if 'BTC' in symbol][:5]
            print_info(f"Exemples de paires BTC: {', '.join(btc_pairs)}")
            
            return True
            
        except Exception as e:
            print_error(f"Erreur lors du test CCXT: {e}")
            print_info("Note: C'est normal si vous n'êtes pas connecté à internet")
            return False
            
    except ImportError:
        print_error("CCXT n'est pas installé")
        return False


def test_redis_optional():
    """Test de Redis (optionnel)"""
    print_header("Test de Redis (Optionnel)")
    
    try:
        import redis
        print_success("redis installé")
        print_info("Note: Redis serveur doit être installé séparément")
        return True
    except ImportError:
        print_error("redis non installé (optionnel pour Phase 1)")
        return False


def print_summary(results):
    """Affiche le résumé final"""
    print_header("RÉSUMÉ DE L'INSTALLATION")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n✅ Tests réussis: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 Toutes les dépendances sont installées et fonctionnelles!")
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 1.2 est COMPLÈTE ✅")
        print("  2. Vous pouvez passer à l'Étape 1.3")
        print("  3. Dites 'Étape 1.3' pour configurer les variables d'environnement")
        return True
    else:
        print_error("❌ Certaines dépendances manquent")
        print("\n🔧 Actions suggérées:")
        
        for test_name, result in results.items():
            if not result:
                print(f"  - Réinstaller: {test_name}")
        
        print("\n💡 Commandes à essayer:")
        print("  pip install -r requirements.txt --upgrade")
        print("  pip install ccxt pandas sqlalchemy psycopg2-binary aiohttp python-dotenv")
        
        return False


def main():
    """Fonction principale"""
    print("\n" + "🧪 TEST DES DÉPENDANCES - ÉTAPE 1.2".center(60))
    
    results = {
        "Bibliothèques Principales": test_core_libraries(),
        "Bibliothèques Asynchrones": test_async_libraries(),
        "Bibliothèques de Configuration": test_config_libraries(),
        "Bibliothèques de Monitoring": test_monitoring_libraries(),
        "Bibliothèques de Test": test_testing_libraries(),
        "CCXT et Exchanges": test_ccxt_exchanges(),
        "Redis (Optionnel)": test_redis_optional()
    }
    
    success = print_summary(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
