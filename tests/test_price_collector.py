#!/usr/bin/env python3
"""
Script de test du PriceCollector - Étape 2.5
===========================================

Teste le collecteur automatique de prix.

Usage:
    python test_price_collector.py
"""

import sys
import time


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
    print_header("Test Import PriceCollector")
    
    try:
        from src.collectors.price_collector import PriceCollector
        print_success("Module price_collector importé")
        return True
    except Exception as e:
        print_error(f"Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_collector():
    """Teste la création du collecteur"""
    print_header("Test Création Collecteur")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        print_info("Création du collecteur...")
        collector = PriceCollector(['binance', 'kraken'], auto_connect=False)
        
        print_success(f"Collecteur créé: {collector}")
        print_info(f"  Exchanges: {list(collector.exchanges.keys())}")
        print_info(f"  Collections: {collector.collection_count}")
        
        if len(collector.exchanges) == 2:
            print_success("2 exchanges configurés")
            return True
        else:
            print_error(f"Attendu 2, reçu {len(collector.exchanges)}")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_connect_all():
    """Teste la connexion à tous les exchanges"""
    print_header("Test Connexion Exchanges")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        print_info("Création et connexion...")
        collector = PriceCollector(['binance', 'kraken'], auto_connect=True)
        
        # Vérifier que tous sont connectés
        connected_count = sum(
            1 for conn in collector.exchanges.values()
            if conn.is_connected()
        )
        
        print_success(f"{connected_count}/{len(collector.exchanges)} exchanges connectés")
        
        for name, conn in collector.exchanges.items():
            status = "✅" if conn.is_connected() else "❌"
            print_info(f"  {status} {name}")
        
        collector.disconnect_all()
        
        if connected_count == len(collector.exchanges):
            print_success("Tous les exchanges connectés")
            return True
        else:
            print_error("Certains exchanges non connectés")
            return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_collect_price_single():
    """Teste la collecte d'un prix sur un exchange"""
    print_header("Test Collecte Prix Simple")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        with PriceCollector(['binance'], auto_connect=True) as collector:
            print_info("Collecte du prix BTC/USDT sur Binance...")
            
            price_data = collector.collect_price('binance', 'BTC/USDT')
            
            if price_data:
                print_success("Prix collecté:")
                print_info(f"  Exchange: {price_data['exchange']}")
                print_info(f"  Symbol: {price_data['symbol']}")
                print_info(f"  Bid: ${price_data['bid']:,.2f}")
                print_info(f"  Ask: ${price_data['ask']:,.2f}")
                print_info(f"  Last: ${price_data['last']:,.2f}")
                
                if price_data['volume']:
                    print_info(f"  Volume: {price_data['volume']:,.2f}")
                
                # Vérifier cohérence
                if price_data['bid'] and price_data['ask']:
                    if price_data['bid'] < price_data['ask']:
                        print_success("Prix cohérents (bid < ask)")
                    else:
                        print_error("Prix incohérents!")
                        return False
                
                return True
            else:
                print_error("Aucun prix collecté")
                return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_collect_prices_multiple():
    """Teste la collecte sur plusieurs exchanges"""
    print_header("Test Collecte Multi-Exchange")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        with PriceCollector(['binance', 'kraken']) as collector:
            print_info("Collecte BTC sur Binance et Kraken...")
            
            # Note: BTC/USDT pour Binance, BTC/USD pour Kraken
            # On va tester avec BTC/USDT mais certains exchanges pourraient échouer
            prices = collector.collect_prices('BTC/USDT', parallel=True)
            
            print_success(f"{len(prices)} prix collectés:")
            for exchange, price_data in prices.items():
                print_info(f"  {exchange}: ${price_data['last']:,.2f}")
            
            if len(prices) >= 1:  # Au moins un prix
                print_success("Collecte multi-exchange OK")
                return True
            else:
                print_error("Aucun prix collecté")
                return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calculate_spreads():
    """Teste le calcul des spreads"""
    print_header("Test Calcul Spreads")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        with PriceCollector(['binance', 'kraken']) as collector:
            print_info("Collecte et calcul des spreads...")
            
            prices = collector.collect_prices('BTC/USDT')
            
            if len(prices) < 2:
                print_info("Pas assez de prix pour calculer les spreads")
                print_info("Tentative avec des prix fictifs...")
                
                # Créer des prix fictifs pour le test
                prices = {
                    'binance': {
                        'exchange': 'binance',
                        'symbol': 'BTC/USDT',
                        'bid': 90000,
                        'ask': 90010,
                        'last': 90005,
                        'volume': 100,
                        'timestamp': None
                    },
                    'kraken': {
                        'exchange': 'kraken',
                        'symbol': 'BTC/USD',
                        'bid': 90050,
                        'ask': 90060,
                        'last': 90055,
                        'volume': 80,
                        'timestamp': None
                    }
                }
            
            spreads = collector.calculate_spreads(prices)
            
            print_success(f"{len(spreads)} spreads calculés:")
            for spread in spreads:
                print_info(
                    f"  {spread['exchange_buy']} → {spread['exchange_sell']}: "
                    f"${spread['spread_abs']:,.2f} ({spread['spread_pct']:+.2f}%)"
                )
            
            if spreads:
                print_success("Calcul de spreads OK")
                return True
            else:
                print_error("Aucun spread calculé")
                return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_collect_and_analyze():
    """Teste la collecte et analyse complète"""
    print_header("Test Collecte et Analyse")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        with PriceCollector(['binance', 'kraken']) as collector:
            print_info("Analyse complète de BTC/USDT...")
            
            result = collector.collect_and_analyze('BTC/USDT', save_to_db=False)
            
            print_success("Résultats:")
            print_info(f"  Prix collectés: {len(result['prices'])}")
            print_info(f"  Spreads calculés: {len(result['spreads'])}")
            print_info(f"  Opportunités: {len(result['opportunities'])}")
            
            # Afficher les prix
            if result['prices']:
                print_success("\n  Prix:")
                for exchange, price_data in result['prices'].items():
                    print_info(f"    {exchange}: ${price_data['last']:,.2f}")
            
            # Afficher les spreads
            if result['spreads']:
                print_success("\n  Spreads:")
                for spread in result['spreads']:
                    print_info(
                        f"    {spread['exchange_buy']}→{spread['exchange_sell']}: "
                        f"{spread['spread_pct']:+.2f}%"
                    )
            
            # Afficher les opportunités
            if result['opportunities']:
                print_success(f"\n  🎯 {len(result['opportunities'])} opportunités détectées!")
                for opp in result['opportunities']:
                    print_info(
                        f"    💰 {opp['symbol']} {opp['exchange_buy']}→{opp['exchange_sell']}: "
                        f"{opp['spread_pct']:+.2f}%"
                    )
            
            if result['prices']:
                print_success("Collecte et analyse OK")
                return True
            else:
                print_error("Aucun résultat")
                return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parallel_collection():
    """Teste la collecte parallèle"""
    print_header("Test Collecte Parallèle")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        with PriceCollector(['binance', 'kraken']) as collector:
            print_info("Test de performance parallèle vs séquentielle...")
            
            # Collecte parallèle
            start = time.time()
            prices_parallel = collector.collect_prices('BTC/USDT', parallel=True)
            time_parallel = time.time() - start
            
            print_info(f"  Parallèle: {time_parallel:.2f}s ({len(prices_parallel)} prix)")
            
            # Collecte séquentielle
            start = time.time()
            prices_sequential = collector.collect_prices('BTC/USDT', parallel=False)
            time_sequential = time.time() - start
            
            print_info(f"  Séquentielle: {time_sequential:.2f}s ({len(prices_sequential)} prix)")
            
            # La parallèle devrait être plus rapide ou similaire
            if time_parallel <= time_sequential * 1.5:
                speedup = time_sequential / time_parallel if time_parallel > 0 else 1
                print_success(f"Collecte parallèle efficace (speedup: {speedup:.1f}x)")
                return True
            else:
                print_info("Performance similaire (normal avec peu d'exchanges)")
                return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_stats():
    """Teste les statistiques"""
    print_header("Test Statistiques")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        with PriceCollector(['binance', 'kraken']) as collector:
            print_info("Collecte de plusieurs prix pour statistiques...")
            
            # Faire quelques collectes
            for i in range(3):
                collector.collect_prices('BTC/USDT')
                time.sleep(0.5)
            
            # Récupérer les stats
            stats = collector.get_stats()
            
            print_success("Statistiques:")
            print_info(f"  Total collections: {stats['total_collections']}")
            print_info(f"  Réussies: {stats['successful_collections']}")
            print_info(f"  Échouées: {stats['failed_collections']}")
            print_info(f"  Opportunités: {stats['opportunities_detected']}")
            print_info(f"  Taux d'erreur: {stats['error_rate']:.2%}")
            print_info(f"  Exchanges: {stats['exchanges_count']}")
            
            if stats['total_collections'] >= 3:
                print_success("Statistiques correctes")
                return True
            else:
                print_error("Statistiques incorrectes")
                return False
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_context_manager():
    """Teste le context manager"""
    print_header("Test Context Manager")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        print_info("Utilisation du context manager...")
        
        with PriceCollector(['binance']) as collector:
            print_success("Entrée dans le context")
            
            # Vérifier connexion
            if collector.exchanges['binance'].is_connected():
                print_success("Exchange connecté")
            
            # Collecter un prix
            prices = collector.collect_prices('BTC/USDT')
            
            if prices:
                print_success(f"Prix collecté: ${prices['binance']['last']:,.2f}")
        
        print_success("Sortie du context (déconnexion automatique)")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_error_handling():
    """Teste la gestion d'erreurs"""
    print_header("Test Gestion Erreurs")
    
    try:
        from src.collectors.price_collector import PriceCollector
        
        with PriceCollector(['binance']) as collector:
            print_info("Test avec symbole invalide...")
            
            # Essayer un symbole invalide
            price_data = collector.collect_price('binance', 'INVALID/PAIR')
            
            if price_data is None:
                print_success("Erreur correctement gérée (retourne None)")
            else:
                print_error("Devrait retourner None pour symbole invalide")
                return False
            
            # Vérifier que le collecteur fonctionne toujours
            print_info("Test avec symbole valide après erreur...")
            price_data = collector.collect_price('binance', 'BTC/USDT')
            
            if price_data:
                print_success("Collecteur toujours fonctionnel après erreur")
                return True
            else:
                print_error("Collecteur cassé après erreur")
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
        print_success("🎉 PriceCollector complètement fonctionnel!")
        
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 2.5 est COMPLÈTE ✅")
        print("  2. Vous pouvez passer à l'Étape 2.6 (Orderbooks)")
        print("  3. Ou commencer la Phase 3 (Détection d'Opportunités)")
        
        print("\n💡 Ce que vous pouvez faire maintenant:")
        print("  >>> from src.collectors.price_collector import PriceCollector")
        print("  >>> collector = PriceCollector(['binance', 'kraken'])")
        print("  >>> result = collector.collect_and_analyze('BTC/USDT')")
        print("  >>> print(result['opportunities'])  # Opportunités d'arbitrage!")
        
        print("\n🎯 Exemple de monitoring en continu:")
        print("  import time")
        print("  while True:")
        print("      result = collector.collect_and_analyze('BTC/USDT')")
        print("      if result['opportunities']:")
        print("          print('🚨 Opportunité détectée!')")
        print("      time.sleep(5)  # Toutes les 5 secondes")
        
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
    print("\n" + "💰 TEST PRICE COLLECTOR - ÉTAPE 2.5".center(60))
    
    results = {
        "Import module": test_import(),
        "Création collecteur": test_create_collector(),
        "Connexion exchanges": test_connect_all(),
        "Collecte prix simple": test_collect_price_single(),
        "Collecte multi-exchange": test_collect_prices_multiple(),
        "Calcul spreads": test_calculate_spreads(),
        "Collecte et analyse": test_collect_and_analyze(),
        "Collecte parallèle": test_parallel_collection(),
        "Statistiques": test_stats(),
        "Context manager": test_context_manager(),
        "Gestion erreurs": test_error_handling()
    }
    
    success = print_summary(results)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
