#!/usr/bin/env python3
"""
Script de test de la configuration - Étape 1.3
==============================================

Vérifie que le fichier .env est bien chargé et que toutes les
configurations sont accessibles.

Usage:
    python test_config.py
"""

import sys
from pathlib import Path


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


def test_env_file_exists():
    """Vérifie que le fichier .env existe"""
    print_header("Vérification du Fichier .env")
    
    env_file = Path('.env')
    
    if env_file.exists():
        print_success("Fichier .env trouvé")
        
        # Vérifier qu'il n'est pas vide
        if env_file.stat().st_size > 0:
            print_success(f"Fichier .env non vide ({env_file.stat().st_size} bytes)")
            return True
        else:
            print_error("Fichier .env vide")
            return False
    else:
        print_error("Fichier .env non trouvé")
        print_info("Copiez .env.template vers .env : copy .env.template .env")
        return False


def test_dotenv_import():
    """Vérifie que python-dotenv est installé"""
    print_header("Vérification de python-dotenv")
    
    try:
        from dotenv import load_dotenv
        print_success("Module python-dotenv importé")
        return True
    except ImportError:
        print_error("Module python-dotenv non installé")
        print_info("Installez-le avec: pip install python-dotenv")
        return False


def test_config_import():
    """Vérifie que le module config peut être importé"""
    print_header("Vérification du Module config")
    
    try:
        from config.config import Config, config
        print_success("Module config.config importé")
        return True
    except ImportError as e:
        print_error(f"Impossible d'importer config.config: {e}")
        return False


def test_config_values():
    """Teste l'accès aux valeurs de configuration"""
    print_header("Test des Valeurs de Configuration")
    
    try:
        from config.config import Config
        
        tests_passed = []
        
        # Test Environment
        env = Config.ENVIRONMENT
        print_info(f"Environment: {env}")
        tests_passed.append(env is not None)
        
        # Test Dry Run Mode
        dry_run = Config.DRY_RUN_MODE
        print_info(f"Dry Run Mode: {dry_run}")
        tests_passed.append(dry_run is not None)
        
        # Test Trading Pairs
        pairs = Config.TRADING_PAIRS
        print_info(f"Trading Pairs: {', '.join(pairs)}")
        tests_passed.append(len(pairs) > 0)
        
        # Test Min/Max Trade Amount
        min_amount = Config.MIN_TRADE_AMOUNT
        max_amount = Config.MAX_TRADE_AMOUNT
        print_info(f"Trade Amount: {min_amount} - {max_amount} USD")
        tests_passed.append(min_amount > 0 and max_amount > min_amount)
        
        # Test Min Profit Threshold
        min_profit = Config.MIN_PROFIT_THRESHOLD
        print_info(f"Min Profit Threshold: {min_profit}%")
        tests_passed.append(min_profit >= 0)
        
        # Test Log Level
        log_level = Config.LOG_LEVEL
        print_info(f"Log Level: {log_level}")
        tests_passed.append(log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        
        if all(tests_passed):
            print_success("Toutes les configurations sont accessibles")
            return True
        else:
            print_error("Certaines configurations ont des valeurs invalides")
            return False
            
    except Exception as e:
        print_error(f"Erreur lors du test des valeurs: {e}")
        return False


def test_config_methods():
    """Teste les méthodes de la classe Config"""
    print_header("Test des Méthodes de Configuration")
    
    try:
        from config.config import Config
        
        # Test is_development
        is_dev = Config.is_development()
        print_info(f"Mode développement: {is_dev}")
        
        # Test is_production
        is_prod = Config.is_production()
        print_info(f"Mode production: {is_prod}")
        
        # Test is_dry_run
        is_dry = Config.is_dry_run()
        print_info(f"Mode dry-run: {is_dry}")
        
        # Test validate_config
        is_valid, errors = Config.validate_config()
        
        if is_valid:
            print_success("Configuration valide ✓")
        else:
            print_warning("Avertissements de configuration:")
            for error in errors:
                print_warning(f"  - {error}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur lors du test des méthodes: {e}")
        return False


def test_display_config():
    """Teste l'affichage de la configuration"""
    print_header("Affichage de la Configuration Actuelle")
    
    try:
        from config.config import Config
        
        config_display = Config.display_config()
        
        for key, value in config_display.items():
            print(f"  {key:.<30} {value}")
        
        print_success("Affichage réussi")
        return True
        
    except Exception as e:
        print_error(f"Erreur lors de l'affichage: {e}")
        return False


def test_api_keys():
    """Vérifie l'état des clés API"""
    print_header("Vérification des Clés API")
    
    try:
        from config.config import Config
        
        # Binance
        if Config.BINANCE_API_KEY:
            print_success(f"Binance API Key configurée: {Config._mask_secret(Config.BINANCE_API_KEY)}")
        else:
            print_warning("Binance API Key non configurée (OK pour Phase 1)")
        
        # Kraken
        if Config.KRAKEN_API_KEY:
            print_success(f"Kraken API Key configurée: {Config._mask_secret(Config.KRAKEN_API_KEY)}")
        else:
            print_warning("Kraken API Key non configurée (OK pour Phase 1)")
        
        # Mode Testnet
        if Config.BINANCE_TESTNET:
            print_info("Mode Binance Testnet activé ✓")
        else:
            print_warning("Mode Binance Testnet désactivé (utilisez le testnet d'abord!)")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur lors de la vérification des clés API: {e}")
        return False


def print_summary(results):
    """Affiche le résumé des tests"""
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n✅ Tests réussis: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 Configuration complète et fonctionnelle!")
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 1.3 est COMPLÈTE ✅")
        print("  2. Vous pouvez passer à l'Étape 1.4")
        print("  3. Dites 'Étape 1.4' pour configurer PostgreSQL")
        
        # Rappel important
        print("\n⚠️  IMPORTANT:")
        print("  - Le fichier .env ne doit JAMAIS être commité dans Git")
        print("  - Les clés API sont optionnelles pour les premières étapes")
        print("  - Utilisez toujours le mode testnet pour commencer")
        
        return True
    else:
        print_error("❌ Certains tests ont échoué")
        print("\n🔧 Actions requises:")
        
        for test_name, result in results.items():
            if not result:
                print(f"  - Corriger: {test_name}")
        
        return False


def main():
    """Fonction principale"""
    print("\n" + "🔧 TEST DE CONFIGURATION - ÉTAPE 1.3".center(60))
    
    results = {
        "Fichier .env existe": test_env_file_exists(),
        "Module python-dotenv": test_dotenv_import(),
        "Module config": test_config_import(),
        "Valeurs de configuration": test_config_values(),
        "Méthodes de configuration": test_config_methods(),
        "Affichage de configuration": test_display_config(),
        "Clés API": test_api_keys()
    }
    
    success = print_summary(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
