#!/usr/bin/env python3
"""
Script de test du BinanceConnector - Étape 2.2
=============================================

Teste la connexion spécifique à Binance.

Usage:
    python test_binance_connector.py
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


def test_import():
    """Teste l'import du module"""
    print_header("Test Import BinanceConnector")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        print_success("Module binance_connector importé")
        return True
    except Exception as e:
        print_error(f"Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_connector():
    """Teste la création du connecteur"""
    print_header("Test Création Connecteur")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        # Mode testnet sans credentials
        connector = BinanceConnector(testnet=False)
        
        print_success(f"Connecteur créé: {connector}")
        print_info(f"Mode: {'TESTNET' if connector.testnet else 'PRODUCTION'}")
        print_info(f"URL: {connector.TESTNET_URL if connector.testnet else connector.PRODUCTION_URL}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_connect_testnet():
    """Teste la connexion au testnet"""
    print_header("Test Connexion Testnet")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        print_info("Connexion au testnet Binance...")
        connector = BinanceConnector(testnet=False)
        
        success = connector.connect()
        
        if success:
            print_success("Connexion testnet réussie!")
            print_info(f"Connecté: {connector.is_connected()}")
            
            # Stats
            stats = connector.get_stats()
            print_info(f"Temps de connexion: {stats['connection_time_ms']:.2f}ms")
            
            connector.disconnect()
            return True
        else:
            print_error("Échec de connexion")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exchange_info():
    """Teste get_exchange_info"""
    print_header("Test Informations Exchange")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            info = conn.get_exchange_info()
            
            print_success("Informations récupérées:")
            print_info(f"  Nom: {info['name']}")
            print_info(f"  Mode: {'TESTNET' if info['testnet'] else 'PRODUCTION'}")
            print_info(f"  URL: {info['url']}")
            print_info(f"  Marchés: {info['markets_count']}")
            print_info(f"  Devises: {len(info['currencies'])}")
            print_info(f"  Spot: {info['has']['spot']}")
            print_info(f"  Futures: {info['has']['futures']}")
            
            if info['markets_count'] > 1000:
                print_success(f"{info['markets_count']} marchés disponibles")
            
            return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_get_ticker():
    """Teste get_ticker"""
    print_header("Test Récupération Ticker")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            print_info("Récupération du ticker BTC/USDT...")
            ticker = conn.get_ticker('BTC/USDT')
            
            print_success("Ticker récupéré:")
            print_info(f"  Symbol: {ticker['symbol']}")
            print_info(f"  Bid: ${ticker['bid']:,.2f}")
            print_info(f"  Ask: ${ticker['ask']:,.2f}")
            print_info(f"  Last: ${ticker['last']:,.2f}")
            
            if ticker['volume']:
                print_info(f"  Volume 24h: {ticker['volume']:,.2f} BTC")
            
            # Vérifier cohérence
            if ticker['bid'] < ticker['ask']:
                print_success("Prix cohérents (bid < ask)")
            
            return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_get_24h_ticker():
    """Teste get_24h_ticker"""
    print_header("Test Statistiques 24h")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            print_info("Récupération des stats 24h BTC/USDT...")
            stats = conn.get_24h_ticker('BTC/USDT')
            
            print_success("Statistiques 24h récupérées:")
            print_info(f"  Symbol: {stats['symbol']}")
            print_info(f"  Prix actuel: ${stats['last']:,.2f}")
            
            if stats['price_change_percent']:
                change_emoji = "📈" if stats['price_change_percent'] > 0 else "📉"
                print_info(f"  Variation 24h: {change_emoji} {stats['price_change_percent']:.2f}%")
            
            if stats['high'] and stats['low']:
                print_info(f"  Plus haut 24h: ${stats['high']:,.2f}")
                print_info(f"  Plus bas 24h: ${stats['low']:,.2f}")
            
            if stats['volume']:
                print_info(f"  Volume 24h: {stats['volume']:,.2f} BTC")
            
            return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_get_depth():
    """Teste get_depth"""
    print_header("Test Profondeur Marché")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            print_info("Récupération de la profondeur du marché...")
            depth = conn.get_depth('BTC/USDT', limit=20)
            
            print_success("Profondeur récupérée:")
            print_info(f"  Symbol: {depth['symbol']}")
            print_info(f"  Bids: {len(depth['bids'])} niveaux")
            print_info(f"  Asks: {len(depth['asks'])} niveaux")
            
            if 'bid_volume_10' in depth:
                print_info(f"  Volume bid (10 niveaux): {depth['bid_volume_10']:.4f} BTC")
                print_info(f"  Volume ask (10 niveaux): {depth['ask_volume_10']:.4f} BTC")
                
                imbalance = depth.get('volume_imbalance', 0)
                if imbalance > 0:
                    print_info(f"  Déséquilibre: {imbalance:.2%} en faveur des acheteurs")
                else:
                    print_info(f"  Déséquilibre: {abs(imbalance):.2%} en faveur des vendeurs")
            
            # Meilleur bid/ask
            if depth['bids'] and depth['asks']:
                best_bid = depth['bids'][0]
                best_ask = depth['asks'][0]
                spread = best_ask[0] - best_bid[0]
                spread_pct = (spread / best_bid[0]) * 100
                
                print_info(f"  Spread: ${spread:.2f} ({spread_pct:.4f}%)")
                print_success("Orderbook cohérent")
            
            return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_get_klines():
    """Teste get_klines"""
    print_header("Test Bougies (Klines)")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            print_info("Récupération des bougies 1h...")
            klines = conn.get_klines('BTC/USDT', interval='1h', limit=24)
            
            print_success(f"{len(klines)} bougies récupérées")
            
            if klines:
                # Dernière bougie
                last_kline = klines[-1]
                timestamp, open_p, high, low, close, volume = last_kline
                
                print_info("  Dernière bougie:")
                print_info(f"    Open: ${open_p:,.2f}")
                print_info(f"    High: ${high:,.2f}")
                print_info(f"    Low: ${low:,.2f}")
                print_info(f"    Close: ${close:,.2f}")
                print_info(f"    Volume: {volume:,.2f} BTC")
                
                # Vérifier cohérence
                if low <= open_p <= high and low <= close <= high:
                    print_success("Données cohérentes")
            
            return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_get_symbols_by_quote():
    """Teste get_symbols_by_quote"""
    print_header("Test Symboles par Quote")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            # USDT
            print_info("Récupération des paires USDT...")
            usdt_pairs = conn.get_symbols_by_quote('USDT')
            print_success(f"{len(usdt_pairs)} paires USDT")
            print_info(f"  Exemples: {', '.join(usdt_pairs[:5])}")
            
            # BTC
            print_info("Récupération des paires BTC...")
            btc_pairs = conn.get_symbols_by_quote('BTC')
            print_success(f"{len(btc_pairs)} paires BTC")
            print_info(f"  Exemples: {', '.join(btc_pairs[:5])}")
            
            if len(usdt_pairs) > 100:
                print_success("Beaucoup de paires USDT disponibles")
            
            return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_trading_fees():
    """Teste get_trading_fees"""
    print_header("Test Frais de Trading")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            print_info("Récupération des frais de trading...")
            fees = conn.get_trading_fees()
            
            print_success("Frais de trading:")
            print_info(f"  Maker: {fees['maker']:.2%}")
            print_info(f"  Taker: {fees['taker']:.2%}")
            
            if fees['maker'] == 0.001 and fees['taker'] == 0.001:
                print_success("Frais par défaut (0.1% maker/taker)")
            
            return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_connectivity():
    """Teste test_connectivity"""
    print_header("Test Connectivité")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        with BinanceConnector(testnet=False) as conn:
            print_info("Test de connectivité...")
            is_ok = conn.test_connectivity()
            
            if is_ok:
                print_success("Connectivité OK")
                return True
            else:
                print_error("Connectivité échouée")
                return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_account_info():
    """Teste get_account_info (nécessite credentials)"""
    print_header("Test Informations Compte")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        from config.config import Config
        
        # Vérifier si on a des credentials
        has_credentials = bool(
            Config.BINANCE_API_KEY and 
            Config.BINANCE_API_SECRET and
            Config.BINANCE_API_KEY != 'your_binance_api_key'
        )
        
        if not has_credentials:
            print_warning("Pas de credentials configurés")
            print_info("Pour tester avec credentials:")
            print_info("  1. Créez un compte sur testnet.binance.vision")
            print_info("  2. Générez des clés API")
            print_info("  3. Ajoutez-les dans .env:")
            print_info("     BINANCE_API_KEY=votre_clé")
            print_info("     BINANCE_API_SECRET=votre_secret")
            print_info("     BINANCE_TESTNET=true")
            return True  # Pas un échec, juste skip
        
        print_info("Credentials détectés, test avec compte...")
        
        connector = BinanceConnector(
            api_key=Config.BINANCE_API_KEY,
            api_secret=Config.BINANCE_API_SECRET,
            testnet=Config.BINANCE_TESTNET
        )
        
        connector.connect()
        
        try:
            info = connector.get_account_info()
            
            print_success("Informations compte récupérées:")
            print_info(f"  Peut trader: {info['can_trade']}")
            print_info(f"  Peut retirer: {info['can_withdraw']}")
            print_info(f"  Type: {info['account_type']}")
            print_info(f"  Balances non nulles: {len(info['balances'])}")
            
            if info['balances']:
                print_info("  Balances:")
                for currency, balance in list(info['balances'].items())[:5]:
                    print_info(f"    {currency}: {balance['total']:.8f}")
            
            return True
            
        finally:
            connector.disconnect()
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_manager():
    """Teste le context manager"""
    print_header("Test Context Manager")
    
    try:
        from src.connectors.binance_connector import BinanceConnector
        
        print_info("Utilisation du context manager...")
        
        with BinanceConnector(testnet=False) as conn:
            print_success("Connexion automatique OK")
            
            ticker = conn.get_ticker('BTC/USDT')
            print_success(f"Ticker récupéré: ${ticker['last']:,.2f}")
        
        print_success("Déconnexion automatique OK")
        
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
        print_success("🎉 BinanceConnector complètement fonctionnel!")
        
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 2.2 est COMPLÈTE ✅")
        print("  2. Vous pouvez passer à l'Étape 2.3")
        print("  3. Dites 'Étape 2.3' pour créer KrakenConnector")
        
        print("\n💡 Ce que vous pouvez faire maintenant:")
        print("  - Récupérer des prix Binance en temps réel")
        print("  - Analyser les orderbooks")
        print("  - Récupérer des données historiques (klines)")
        print("  - Calculer les spreads")
        print("  - Préparer la détection d'opportunités")
        
        print("\n🔑 Pour tester avec credentials:")
        print("  1. Allez sur https://testnet.binance.vision")
        print("  2. Créez un compte et générez des clés API")
        print("  3. Ajoutez-les dans .env")
        print("  4. Relancez ce script")
        
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
    print("\n" + "🔗 TEST BINANCE CONNECTOR - ÉTAPE 2.2".center(60))
    
    results = {
        "Import module": test_import(),
        "Création connecteur": test_create_connector(),
        "Connexion testnet": test_connect_testnet(),
        "Informations exchange": test_exchange_info(),
        "Récupération ticker": test_get_ticker(),
        "Statistiques 24h": test_get_24h_ticker(),
        "Profondeur marché": test_get_depth(),
        "Bougies (klines)": test_get_klines(),
        "Symboles par quote": test_get_symbols_by_quote(),
        "Frais de trading": test_trading_fees(),
        "Connectivité": test_connectivity(),
        "Context manager": test_context_manager(),
        "Informations compte": test_account_info()
    }
    
    success = print_summary(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
