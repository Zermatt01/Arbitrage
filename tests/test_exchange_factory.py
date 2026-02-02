#!/usr/bin/env python3
"""
Script de test du ExchangeFactory - Étape 2.4
============================================

Teste le Factory Pattern pour les connecteurs d'exchanges.

Usage:
    python test_exchange_factory.py
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


def test_import():
    """Teste l'import du module"""
    print_header("Test Import ExchangeFactory")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        print_success("Module exchange_factory importé")
        return True
    except Exception as e:
        print_error(f"Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_available_exchanges():
    """Teste get_available_exchanges"""
    print_header("Test Exchanges Disponibles")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        exchanges = ExchangeFactory.get_available_exchanges()
        
        print_success(f"{len(exchanges)} exchanges disponibles:")
        for exchange in exchanges:
            print_info(f"  - {exchange}")
        
        if 'binance' in exchanges and 'kraken' in exchanges:
            print_success("Binance et Kraken disponibles")
            return True
        else:
            print_error("Binance ou Kraken manquant")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_is_supported():
    """Teste is_supported"""
    print_header("Test Vérification Support")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        # Exchanges supportés
        print_info("Vérification exchanges supportés...")
        for exchange in ['binance', 'kraken']:
            if ExchangeFactory.is_supported(exchange):
                print_success(f"  {exchange} supporté")
            else:
                print_error(f"  {exchange} non supporté")
                return False
        
        # Exchange non supporté
        print_info("Vérification exchange non supporté...")
        if not ExchangeFactory.is_supported('coinbase'):
            print_success("  coinbase correctement identifié comme non supporté")
        else:
            print_error("  coinbase incorrectement identifié")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_create_binance():
    """Teste création Binance"""
    print_header("Test Création Binance")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        print_info("Création Binance...")
        binance = ExchangeFactory.create('binance')
        
        print_success(f"Binance créé: {binance}")
        print_info(f"  Type: {type(binance).__name__}")
        print_info(f"  Exchange: {binance.exchange_name}")
        
        from src.connectors.binance_connector import BinanceConnector
        if isinstance(binance, BinanceConnector):
            print_success("Instance de BinanceConnector confirmée")
            return True
        else:
            print_error("Type incorrect")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_kraken():
    """Teste création Kraken"""
    print_header("Test Création Kraken")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        print_info("Création Kraken...")
        kraken = ExchangeFactory.create('kraken')
        
        print_success(f"Kraken créé: {kraken}")
        print_info(f"  Type: {type(kraken).__name__}")
        print_info(f"  Exchange: {kraken.exchange_name}")
        
        from src.connectors.kraken_connector import KrakenConnector
        if isinstance(kraken, KrakenConnector):
            print_success("Instance de KrakenConnector confirmée")
            return True
        else:
            print_error("Type incorrect")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_create_invalid():
    """Teste création exchange invalide"""
    print_header("Test Exchange Invalide")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        print_info("Tentative de création d'exchange invalide...")
        
        try:
            invalid = ExchangeFactory.create('invalid_exchange')
            print_error("Devrait avoir levé une ValueError!")
            return False
        except ValueError as e:
            print_success("ValueError levée correctement")
            print_info(f"  Message: {str(e)[:50]}...")
            return True
        
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return False


def test_create_all():
    """Teste create_all"""
    print_header("Test Création Multiple")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        print_info("Création de plusieurs exchanges...")
        exchanges = ExchangeFactory.create_all(['binance', 'kraken'])
        
        print_success(f"{len(exchanges)} exchanges créés:")
        for name, connector in exchanges.items():
            print_info(f"  {name}: {type(connector).__name__}")
        
        if len(exchanges) == 2:
            print_success("Nombre correct d'exchanges")
        else:
            print_error(f"Attendu 2, reçu {len(exchanges)}")
            return False
        
        if 'binance' in exchanges and 'kraken' in exchanges:
            print_success("Binance et Kraken présents")
            return True
        else:
            print_error("Exchanges manquants")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_case_insensitive():
    """Teste insensibilité à la casse"""
    print_header("Test Insensibilité Casse")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        print_info("Test avec différentes casses...")
        
        variants = ['binance', 'Binance', 'BINANCE', 'BiNaNcE']
        
        for variant in variants:
            try:
                conn = ExchangeFactory.create(variant)
                print_success(f"  '{variant}' accepté")
            except Exception as e:
                print_error(f"  '{variant}' refusé: {e}")
                return False
        
        print_success("Insensibilité à la casse confirmée")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_connect_all():
    """Teste connect_all"""
    print_header("Test Connexion Multiple")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        print_info("Création et connexion des exchanges...")
        exchanges = ExchangeFactory.create_all(['binance', 'kraken'])
        results = ExchangeFactory.connect_all(exchanges)
        
        print_success("Résultats de connexion:")
        for name, success in results.items():
            status = "✅" if success else "❌"
            print_info(f"  {status} {name}: {'OK' if success else 'Échec'}")
        
        if all(results.values()):
            print_success("Tous les exchanges connectés")
            
            # Déconnecter
            ExchangeFactory.disconnect_all(exchanges)
            print_success("Tous les exchanges déconnectés")
            
            return True
        else:
            print_error("Certaines connexions ont échoué")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_prices():
    """Teste récupération de prix via factory"""
    print_header("Test Récupération Prix")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        
        print_info("Récupération des prix BTC...")
        exchanges = ExchangeFactory.create_all(['binance', 'kraken'])
        ExchangeFactory.connect_all(exchanges)
        
        prices = {}
        
        for name, connector in exchanges.items():
            try:
                symbol = 'BTC/USDT' if name == 'binance' else 'BTC/USD'
                ticker = connector.get_ticker(symbol)
                prices[name] = ticker['last']
                print_success(f"  {name}: ${ticker['last']:,.2f}")
            except Exception as e:
                print_error(f"  {name}: Erreur - {e}")
                return False
        
        # Calculer le spread
        if len(prices) == 2:
            spread = abs(prices['binance'] - prices['kraken'])
            spread_pct = (spread / prices['binance']) * 100
            print_info(f"  Spread: ${spread:,.2f} ({spread_pct:.2f}%)")
            
            if spread_pct > 0.5:
                print_success("  🎯 Opportunité d'arbitrage potentielle!")
        
        ExchangeFactory.disconnect_all(exchanges)
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_register():
    """Teste enregistrement de nouveaux exchanges"""
    print_header("Test Enregistrement Exchange")
    
    try:
        from src.connectors.exchange_factory import ExchangeFactory
        from src.connectors.base_connector import BaseConnector
        
        # Créer classe de test
        class TestConnector(BaseConnector):
            def __init__(self, **kwargs):
                super().__init__('test_exchange', **kwargs)
        
        print_info("Enregistrement d'un nouvel exchange...")
        ExchangeFactory.register('testexchange', TestConnector)
        
        if ExchangeFactory.is_supported('testexchange'):
            print_success("Exchange enregistré")
        else:
            print_error("Exchange non trouvé après enregistrement")
            return False
        
        print_info("Création de l'exchange enregistré...")
        test_conn = ExchangeFactory.create('testexchange')
        
        if isinstance(test_conn, TestConnector):
            print_success("Exchange créé correctement")
            return True
        else:
            print_error("Type incorrect")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def print_summary(results):
    """Affiche le résumé"""
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n✅ Tests réussis: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 ExchangeFactory complètement fonctionnel!")
        
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 2.4 est COMPLÈTE ✅")
        print("  2. Passez à l'Étape 2.5")
        print("  3. Dites 'Étape 2.5' pour le Collecteur de Prix")
        
        print("\n💡 Ce que vous pouvez faire maintenant:")
        print("  >>> from src.connectors.exchange_factory import ExchangeFactory")
        print("  >>> exchanges = ExchangeFactory.create_all(['binance', 'kraken'])")
        print("  >>> ExchangeFactory.connect_all(exchanges)")
        print("  >>> # Récupérer les prix facilement...")
        
        return True
    else:
        print_error("❌ Certains tests ont échoué")
        print("\n🔧 Tests échoués:")
        for test_name, result in results.items():
            if not result:
                print(f"  - {test_name}")
        return False


def main():
    """Fonction principale"""
    print("\n" + "🏭 TEST EXCHANGE FACTORY - ÉTAPE 2.4".center(60))
    
    results = {
        "Import module": test_import(),
        "Exchanges disponibles": test_available_exchanges(),
        "Vérification support": test_is_supported(),
        "Création Binance": test_create_binance(),
        "Création Kraken": test_create_kraken(),
        "Exchange invalide": test_create_invalid(),
        "Création multiple": test_create_all(),
        "Insensibilité casse": test_case_insensitive(),
        "Connexion multiple": test_connect_all(),
        "Récupération prix": test_get_prices(),
        "Enregistrement": test_register()
    }
    
    success = print_summary(results)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
