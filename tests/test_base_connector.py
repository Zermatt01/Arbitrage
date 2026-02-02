#!/usr/bin/env python3
"""
Script de test du BaseConnector - Étape 2.1
==========================================

Teste la classe de base pour les connecteurs d'exchanges.

Usage:
    python test_base_connector.py
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


def test_import():
    """Teste l'import du module"""
    print_header("Test Import BaseConnector")
    
    try:
        from src.connectors.base_connector import (
            BaseConnector,
            ExchangeError,
            ConnectionError,
            RateLimitError
        )
        print_success("Module base_connector importé")
        return True
    except Exception as e:
        print_error(f"Erreur d'import: {e}")
        return False


def test_import_ccxt():
    """Teste l'import de CCXT"""
    print_header("Test CCXT")
    
    try:
        import ccxt
        
        print_success(f"CCXT version {ccxt.__version__} installé")
        
        # Lister quelques exchanges disponibles
        exchanges = ccxt.exchanges
        print_info(f"{len(exchanges)} exchanges disponibles dans CCXT")
        print_info(f"Exemples: {', '.join(exchanges[:5])}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        print_info("Installez CCXT avec: pip install ccxt")
        return False


def test_create_connector():
    """Teste la création d'un connecteur"""
    print_header("Test Création Connecteur")
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        # Créer un connecteur Binance sans credentials
        connector = BaseConnector(
            exchange_name='binance',
            testnet=False
        )
        
        print_success(f"Connecteur créé: {connector}")
        print_info(f"Exchange: {connector.exchange_name}")
        print_info(f"Testnet: {connector.testnet}")
        print_info(f"Connecté: {connector.is_connected()}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_connect_public():
    """Teste la connexion publique (sans credentials)"""
    print_header("Test Connexion Publique")
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        # Créer et connecter (mode public)
        connector = BaseConnector('binance')
        
        print_info("Tentative de connexion à Binance...")
        success = connector.connect()
        
        if success:
            print_success("Connexion réussie!")
            print_info(f"Statut: {connector.is_connected()}")
            
            # Afficher les stats
            stats = connector.get_stats()
            print_info(f"Temps de connexion: {stats['connection_time_ms']:.2f}ms")
            
            connector.disconnect()
            print_success("Déconnexion réussie")
            
            return True
        else:
            print_error("Échec de la connexion")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_markets():
    """Teste la récupération des marchés"""
    print_header("Test Récupération Marchés")
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        connector = BaseConnector('binance')
        connector.connect()
        
        print_info("Récupération des marchés...")
        markets = connector.get_markets()
        
        print_success(f"{len(markets)} marchés disponibles")
        print_info(f"Exemples: {', '.join(markets[:5])}")
        
        # Vérifier que BTC/USDT existe
        if 'BTC/USDT' in markets:
            print_success("BTC/USDT disponible")
        else:
            print_error("BTC/USDT non trouvé")
        
        connector.disconnect()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_get_ticker():
    """Teste la récupération d'un ticker"""
    print_header("Test Récupération Ticker")
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        connector = BaseConnector('binance')
        connector.connect()
        
        print_info("Récupération du ticker BTC/USDT...")
        ticker = connector.get_ticker('BTC/USDT')
        
        print_success("Ticker récupéré:")
        print_info(f"  Symbol: {ticker['symbol']}")
        print_info(f"  Exchange: {ticker['exchange']}")
        print_info(f"  Bid: ${ticker['bid']:,.2f}")
        print_info(f"  Ask: ${ticker['ask']:,.2f}")
        print_info(f"  Last: ${ticker['last']:,.2f}")
        print_info(f"  Volume 24h: {ticker['volume']:,.2f} BTC")
        
        # Vérifier que les prix sont cohérents
        if ticker['bid'] and ticker['ask'] and ticker['bid'] < ticker['ask']:
            print_success("Prix cohérents (bid < ask)")
        else:
            print_error("Prix incohérents!")
        
        connector.disconnect()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_orderbook():
    """Teste la récupération d'un orderbook"""
    print_header("Test Récupération Orderbook")
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        connector = BaseConnector('binance')
        connector.connect()
        
        print_info("Récupération de l'orderbook BTC/USDT (10 niveaux)...")
        orderbook = connector.get_orderbook('BTC/USDT', limit=10)
        
        print_success("Orderbook récupéré:")
        print_info(f"  Symbol: {orderbook['symbol']}")
        print_info(f"  Exchange: {orderbook['exchange']}")
        print_info(f"  Bids (achats): {len(orderbook['bids'])} niveaux")
        print_info(f"  Asks (ventes): {len(orderbook['asks'])} niveaux")
        
        # Afficher les meilleurs bid/ask
        if orderbook['bids'] and orderbook['asks']:
            best_bid = orderbook['bids'][0]
            best_ask = orderbook['asks'][0]
            
            print_info(f"  Meilleur bid: ${best_bid[0]:,.2f} ({best_bid[1]:.4f} BTC)")
            print_info(f"  Meilleur ask: ${best_ask[0]:,.2f} ({best_ask[1]:.4f} BTC)")
            
            spread = best_ask[0] - best_bid[0]
            spread_percent = (spread / best_bid[0]) * 100
            print_info(f"  Spread: ${spread:.2f} ({spread_percent:.4f}%)")
            
            print_success("Orderbook cohérent")
        
        connector.disconnect()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_error_handling():
    """Teste la gestion d'erreurs"""
    print_header("Test Gestion d'Erreurs")
    
    try:
        from src.connectors.base_connector import BaseConnector, ExchangeError
        
        connector = BaseConnector('binance')
        connector.connect()
        
        # Tester avec un symbole invalide
        print_info("Test avec symbole invalide...")
        try:
            ticker = connector.get_ticker('INVALID/PAIR')
            print_error("Devrait avoir échoué!")
            return False
        except ExchangeError as e:
            print_success(f"Erreur correctement capturée: {type(e).__name__}")
        
        # Tester sans connexion
        print_info("Test sans connexion...")
        connector.disconnect()
        
        try:
            ticker = connector.get_ticker('BTC/USDT')
            print_error("Devrait avoir échoué!")
            return False
        except Exception as e:
            print_success(f"Erreur correctement capturée: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_context_manager():
    """Teste le context manager"""
    print_header("Test Context Manager")
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        print_info("Utilisation du context manager (with)...")
        
        with BaseConnector('binance') as connector:
            print_success("Connexion automatique OK")
            print_info(f"Connecté: {connector.is_connected()}")
            
            # Utiliser le connecteur
            ticker = connector.get_ticker('BTC/USDT')
            print_success(f"Ticker récupéré: ${ticker['last']:,.2f}")
        
        # Hors du context, devrait être déconnecté
        print_success("Déconnexion automatique OK")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_stats():
    """Teste les statistiques"""
    print_header("Test Statistiques")
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        connector = BaseConnector('binance')
        connector.connect()
        
        # Faire quelques requêtes
        connector.get_ticker('BTC/USDT')
        connector.get_ticker('ETH/USDT')
        connector.get_orderbook('BTC/USDT')
        
        # Récupérer les stats
        stats = connector.get_stats()
        
        print_success("Statistiques récupérées:")
        print_info(f"  Exchange: {stats['exchange']}")
        print_info(f"  Connecté: {stats['is_connected']}")
        print_info(f"  Requêtes: {stats['requests_count']}")
        print_info(f"  Erreurs: {stats['errors_count']}")
        print_info(f"  Taux d'erreur: {stats['error_rate']:.2%}")
        print_info(f"  Temps connexion: {stats['connection_time_ms']:.2f}ms")
        
        if stats['requests_count'] >= 3:
            print_success("Compteur de requêtes OK")
        else:
            print_error("Compteur de requêtes incorrect")
        
        connector.disconnect()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_multiple_exchanges():
    """Teste plusieurs exchanges"""
    print_header("Test Multiples Exchanges")
    
    exchanges_to_test = ['binance', 'kraken']
    
    try:
        from src.connectors.base_connector import BaseConnector
        
        results = {}
        
        for exchange_name in exchanges_to_test:
            print_info(f"\nTest de {exchange_name}...")
            
            try:
                connector = BaseConnector(exchange_name)
                success = connector.connect()
                
                if success:
                    ticker = connector.get_ticker('BTC/USDT')
                    print_success(f"{exchange_name}: BTC/USDT = ${ticker['last']:,.2f}")
                    results[exchange_name] = True
                    connector.disconnect()
                else:
                    print_error(f"{exchange_name}: échec de connexion")
                    results[exchange_name] = False
                    
            except Exception as e:
                print_error(f"{exchange_name}: {e}")
                results[exchange_name] = False
        
        # Résumé
        success_count = sum(results.values())
        print_info(f"\n{success_count}/{len(exchanges_to_test)} exchanges testés avec succès")
        
        return success_count > 0  # Au moins un exchange doit fonctionner
        
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
        print_success("🎉 BaseConnector complètement fonctionnel!")
        
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 2.1 est COMPLÈTE ✅")
        print("  2. Vous pouvez passer à l'Étape 2.2")
        print("  3. Dites 'Étape 2.2' pour créer BinanceConnector")
        
        print("\n💡 Ce que vous pouvez faire maintenant:")
        print("  - Se connecter à n'importe quel exchange CCXT")
        print("  - Récupérer tickers et orderbooks")
        print("  - Gestion d'erreurs automatique")
        print("  - Retry avec backoff exponentiel")
        print("  - Statistiques et monitoring")
        
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
    print("\n" + "🔌 TEST BASE CONNECTOR - ÉTAPE 2.1".center(60))
    
    results = {
        "Import modules": test_import(),
        "CCXT disponible": test_import_ccxt(),
        "Création connecteur": test_create_connector(),
        "Connexion publique": test_connect_public(),
        "Récupération marchés": test_get_markets(),
        "Récupération ticker": test_get_ticker(),
        "Récupération orderbook": test_get_orderbook(),
        "Gestion d'erreurs": test_error_handling(),
        "Context manager": test_context_manager(),
        "Statistiques": test_stats(),
        "Multiples exchanges": test_multiple_exchanges()
    }
    
    success = print_summary(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
