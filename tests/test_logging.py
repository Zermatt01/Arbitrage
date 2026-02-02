#!/usr/bin/env python3
"""
Script de test du système de logging - Étape 1.6
================================================

Teste toutes les fonctionnalités du logger.

Usage:
    python test_logging.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime


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


def test_import_logger():
    """Teste l'import du module logger"""
    print_header("Test Import Logger")
    
    try:
        from src.utils.logger import get_logger, log_function_call
        print_success("Module logger importé")
        return True
    except Exception as e:
        print_error(f"Erreur d'import: {e}")
        return False


def test_basic_logging():
    """Teste les logs de base"""
    print_header("Test Logging de Base")
    
    try:
        from src.utils.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Tester tous les niveaux
        logger.debug("Message DEBUG")
        logger.info("Message INFO")
        logger.warning("Message WARNING")
        logger.error("Message ERROR")
        logger.critical("Message CRITICAL")
        
        print_success("Tous les niveaux de log testés")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_context_logging():
    """Teste les logs avec contexte"""
    print_header("Test Logging avec Contexte")
    
    try:
        from src.utils.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Log avec contexte
        logger.info("Opportunité détectée", extra={
            'context': {
                'symbol': 'BTC/USDT',
                'buy_exchange': 'binance',
                'sell_exchange': 'kraken',
                'profit_percent': 0.85
            }
        })
        
        logger.warning("Latence élevée détectée", extra={
            'context': {
                'exchange': 'binance',
                'latency_ms': 1500,
                'threshold_ms': 1000
            }
        })
        
        print_success("Logs avec contexte créés")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_exception_logging():
    """Teste le logging des exceptions"""
    print_header("Test Logging d'Exceptions")
    
    try:
        from src.utils.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Générer une exception
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.error("Division par zéro détectée", exc_info=True)
        
        # Exception avec contexte
        try:
            invalid_data = {'price': 'invalid'}
            price = float(invalid_data['price'])
        except ValueError:
            logger.error(
                "Erreur de conversion de prix",
                exc_info=True,
                extra={'context': {'data': invalid_data}}
            )
        
        print_success("Exceptions loggées avec stack trace")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_file_logging():
    """Teste que les logs sont écrits dans les fichiers"""
    print_header("Test Fichiers de Logs")
    
    try:
        logs_dir = Path('logs')
        
        # Vérifier que le dossier existe
        if not logs_dir.exists():
            print_error("Dossier 'logs/' n'existe pas")
            return False
        
        print_success(f"Dossier 'logs/' existe")
        
        # Vérifier les fichiers
        all_logs = logs_dir / 'arbitrage.log'
        error_logs = logs_dir / 'errors.log'
        
        if all_logs.exists():
            size = all_logs.stat().st_size
            print_success(f"arbitrage.log existe ({size} bytes)")
            
            # Lire les dernières lignes
            with open(all_logs, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print_info(f"  {len(lines)} lignes de logs")
                    print_info(f"  Dernier log: {lines[-1][:80]}...")
        else:
            print_error("arbitrage.log n'existe pas")
            return False
        
        if error_logs.exists():
            size = error_logs.stat().st_size
            print_success(f"errors.log existe ({size} bytes)")
        else:
            print_info("errors.log n'existe pas encore (normal si aucune erreur)")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_database_logging():
    """Teste que les logs sont écrits en base de données"""
    print_header("Test Logs en Base de Données")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        # Ne tester que si pas en dry-run
        if Config.DRY_RUN_MODE:
            print_info("Mode DRY_RUN activé - logs DB désactivés (normal)")
            return True
        
        engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Compter les logs récents
        query = text("""
            SELECT COUNT(*) 
            FROM system_logs 
            WHERE created_at > NOW() - INTERVAL '5 minutes'
        """)
        result = session.execute(query)
        count = result.scalar()
        
        print_success(f"{count} log(s) dans la DB (5 dernières minutes)")
        
        # Afficher les derniers logs
        if count > 0:
            query = text("""
                SELECT level, module, message, created_at 
                FROM system_logs 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            result = session.execute(query)
            rows = result.fetchall()
            
            print_info("Derniers logs en DB:")
            for row in rows:
                timestamp = row.created_at.strftime('%H:%M:%S')
                print_info(f"  [{timestamp}] {row.level:8} - {row.module}: {row.message[:50]}")
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        print_info("Vérifiez que PostgreSQL est démarré et accessible")
        return False


def test_decorator():
    """Teste le décorateur log_function_call"""
    print_header("Test Décorateur @log_function_call")
    
    try:
        from src.utils.logger import log_function_call, get_logger
        
        @log_function_call
        def calculer_profit(buy_price, sell_price, amount):
            """Calcule le profit d'un trade"""
            profit = (sell_price - buy_price) * amount
            return profit
        
        # Appeler la fonction décorée
        profit = calculer_profit(45000, 45500, 0.1)
        
        print_success(f"Fonction décorée appelée (profit: ${profit})")
        print_info("Vérifiez les logs pour voir l'appel de fonction")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_log_levels():
    """Teste les différents niveaux de log"""
    print_header("Test Niveaux de Log")
    
    try:
        from src.utils.logger import setup_logger
        
        # Logger avec niveau DEBUG
        debug_logger = setup_logger(
            name='test_debug',
            log_level='DEBUG',
            log_to_console=False,
            log_to_file=True,
            log_to_database=False
        )
        
        debug_logger.debug("Ce message DEBUG devrait être visible")
        print_success("Logger DEBUG créé")
        
        # Logger avec niveau WARNING (ne verra pas INFO)
        warning_logger = setup_logger(
            name='test_warning',
            log_level='WARNING',
            log_to_console=False,
            log_to_file=True,
            log_to_database=False
        )
        
        warning_logger.info("Ce message INFO ne devrait PAS être visible")
        warning_logger.warning("Ce message WARNING devrait être visible")
        print_success("Logger WARNING créé")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_json_format():
    """Vérifie que les logs sont bien en JSON"""
    print_header("Test Format JSON")
    
    try:
        import json
        
        logs_file = Path('logs') / 'arbitrage.log'
        
        if not logs_file.exists():
            print_error("Fichier arbitrage.log n'existe pas")
            return False
        
        # Lire la dernière ligne
        with open(logs_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                print_error("Fichier de logs vide")
                return False
            
            last_line = lines[-1].strip()
            
            # Tenter de parser en JSON
            try:
                log_data = json.loads(last_line)
                
                print_success("Format JSON valide")
                print_info(f"  Champs présents: {', '.join(log_data.keys())}")
                
                # Vérifier les champs essentiels
                required_fields = ['timestamp', 'level', 'module', 'message']
                missing = [f for f in required_fields if f not in log_data]
                
                if missing:
                    print_error(f"Champs manquants: {missing}")
                    return False
                else:
                    print_success("Tous les champs requis présents")
                
                return True
                
            except json.JSONDecodeError as e:
                print_error(f"Impossible de parser le JSON: {e}")
                print_info(f"Ligne: {last_line[:100]}")
                return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_performance():
    """Teste la performance du logging"""
    print_header("Test Performance")
    
    try:
        import time
        from src.utils.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Logger 1000 messages
        start = time.time()
        
        for i in range(1000):
            logger.info(f"Message de test #{i}", extra={
                'context': {'iteration': i}
            })
        
        elapsed = time.time() - start
        
        print_success(f"1000 logs en {elapsed:.2f} secondes")
        print_info(f"  Performance: {1000/elapsed:.0f} logs/seconde")
        
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
        print_success("🎉 Système de logging complètement fonctionnel!")
        
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 1.6 est COMPLÈTE ✅")
        print("  2. Phase 1 (Configuration) est TERMINÉE 🎊")
        print("  3. Vous pouvez passer à la Phase 2 (Connexion aux Exchanges)")
        print("  4. Dites 'Étape 2.1' pour continuer")
        
        print("\n📁 Fichiers de logs créés:")
        print("  - logs/arbitrage.log (tous les logs en JSON)")
        print("  - logs/errors.log (uniquement les erreurs)")
        
        print("\n💡 Utilisation dans votre code:")
        print("  from src.utils.logger import get_logger")
        print("  logger = get_logger(__name__)")
        print("  logger.info('Message')")
        
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
    print("\n" + "📝 TEST SYSTÈME DE LOGGING - ÉTAPE 1.6".center(60))
    
    # Créer le dossier logs s'il n'existe pas
    Path('logs').mkdir(exist_ok=True)
    
    results = {
        "Import logger": test_import_logger(),
        "Logging de base": test_basic_logging(),
        "Contexte": test_context_logging(),
        "Exceptions": test_exception_logging(),
        "Fichiers de logs": test_file_logging(),
        "Format JSON": test_json_format(),
        "Décorateur": test_decorator(),
        "Niveaux de log": test_log_levels(),
        "Base de données": test_database_logging(),
        "Performance": test_performance()
    }
    
    success = print_summary(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
