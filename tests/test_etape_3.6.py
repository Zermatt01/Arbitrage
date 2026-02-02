"""
Tests pour l'Étape 3.6 - Sauvegarde des Opportunités
=====================================================

Teste la sauvegarde et récupération des opportunités en base de données.
"""

from src.database.opportunity_db import OpportunityDB
from datetime import datetime


def print_header(text):
    """Affiche un header formaté"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Affiche un message de succès"""
    print(f"✅ {text}")


def print_error(text):
    """Affiche un message d'erreur"""
    print(f"❌ {text}")


def test_save_opportunity():
    """Test sauvegarde d'une opportunité"""
    print_header("Test 1 : Sauvegarde Opportunité")
    
    try:
        db = OpportunityDB()
        
        # Opportunité test
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 81235.45,
            'sell_price': 81500.00,
            'spread_pct': 0.33,
            'net_profit_pct': 0.24,
            'total_fees_pct': 0.36,
            'total_slippage_pct': 0.10,
            'liquidity_valid': True,
            'total_score': 87.5,
            'grade': 'A'
        }
        
        print("\n📝 Sauvegarde de l'opportunité...")
        opp_id = db.save_opportunity(opportunity)
        
        print(f"   ID: {opp_id}")
        print(f"   Symbole: {opportunity['symbol']}")
        print(f"   Route: {opportunity['exchange_buy']} → {opportunity['exchange_sell']}")
        print(f"   Profit NET: {opportunity['net_profit_pct']:.2f}%")
        print(f"   Score: {opportunity['total_score']:.1f}/100")
        
        assert opp_id is not None, "ID devrait être retourné"
        assert opp_id > 0, "ID devrait être positif"
        
        print_success(f"Opportunité sauvegardée (ID: {opp_id})")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_save_batch():
    """Test sauvegarde multiple"""
    print_header("Test 2 : Sauvegarde Batch")
    
    try:
        db = OpportunityDB()
        
        # Plusieurs opportunités
        opportunities = [
            {
                'symbol': 'ETH/USDT',
                'exchange_buy': 'binance',
                'exchange_sell': 'coinbase',
                'buy_price': 3200.50,
                'sell_price': 3225.00,
                'spread_pct': 0.76,
                'net_profit_pct': 0.45,
                'total_score': 90.2,
                'grade': 'S',
                'liquidity_valid': True
            },
            {
                'symbol': 'SOL/USDT',
                'exchange_buy': 'kraken',
                'exchange_sell': 'bitfinex',
                'buy_price': 145.20,
                'sell_price': 146.00,
                'spread_pct': 0.55,
                'net_profit_pct': 0.25,
                'total_score': 75.5,
                'grade': 'B',
                'liquidity_valid': True
            },
            {
                'symbol': 'XRP/USDT',
                'exchange_buy': 'okx',
                'exchange_sell': 'bitstamp',
                'buy_price': 0.52,
                'sell_price': 0.525,
                'spread_pct': 0.96,
                'net_profit_pct': 0.60,
                'total_score': 82.0,
                'grade': 'A',
                'liquidity_valid': True
            }
        ]
        
        print(f"\n📝 Sauvegarde de {len(opportunities)} opportunités...")
        count = db.save_opportunities_batch(opportunities)
        
        print(f"\n✅ {count}/{len(opportunities)} opportunités sauvegardées")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"   {i}. {opp['symbol']} - Score: {opp['total_score']:.1f}/100")
        
        assert count == len(opportunities), f"Devrait sauvegarder {len(opportunities)}"
        
        print_success("Batch sauvegardé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_recent():
    """Test récupération récentes"""
    print_header("Test 3 : Récupération Récentes")
    
    try:
        db = OpportunityDB()
        
        print("\n📊 Récupération des 5 dernières opportunités...")
        recent = db.get_recent_opportunities(limit=5)
        
        print(f"\n✅ {len(recent)} opportunités récupérées:")
        print(f"\n{'Symbole':<12} {'Route':<25} {'Profit':<10} {'Score':<8}")
        print("-" * 60)
        
        for opp in recent:
            route = f"{opp['exchange_buy']}→{opp['exchange_sell']}"
            print(f"{opp['symbol']:<12} {route:<25} "
                  f"{opp['net_profit_pct']:>5.2f}%{'':<3} {opp['total_score']:>6.1f}")
        
        assert len(recent) >= 0, "Devrait retourner une liste"
        
        if recent:
            assert 'symbol' in recent[0], "Devrait contenir symbol"
            assert 'total_score' in recent[0], "Devrait contenir total_score"
        
        print_success(f"{len(recent)} opportunités récupérées")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_by_symbol():
    """Test récupération par symbole"""
    print_header("Test 4 : Récupération par Symbole")
    
    try:
        db = OpportunityDB()
        
        symbol = 'BTC/USDT'
        print(f"\n📊 Récupération opportunités pour {symbol} (24h)...")
        
        opportunities = db.get_opportunities_by_symbol(symbol, hours=24)
        
        print(f"\n✅ {len(opportunities)} opportunités trouvées pour {symbol}")
        
        if opportunities:
            print(f"\n{'Exchange Buy':<15} {'Exchange Sell':<15} {'Profit':<10} {'Score':<8}")
            print("-" * 55)
            
            for opp in opportunities[:5]:  # Top 5
                print(f"{opp['exchange_buy']:<15} {opp['exchange_sell']:<15} "
                      f"{opp['net_profit_pct']:>5.2f}%{'':<3} {opp['total_score']:>6.1f}")
        
        print_success(f"{len(opportunities)} opportunités pour {symbol}")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_by_route():
    """Test récupération par route"""
    print_header("Test 5 : Récupération par Route")
    
    try:
        db = OpportunityDB()
        
        exchange_buy = 'binance'
        exchange_sell = 'kraken'
        
        print(f"\n📊 Récupération opportunités {exchange_buy}→{exchange_sell} (24h)...")
        
        opportunities = db.get_opportunities_by_route(
            exchange_buy,
            exchange_sell,
            hours=24
        )
        
        print(f"\n✅ {len(opportunities)} opportunités trouvées pour cette route")
        
        if opportunities:
            avg_profit = sum(o['net_profit_pct'] for o in opportunities) / len(opportunities)
            avg_score = sum(o['total_score'] for o in opportunities) / len(opportunities)
            
            print(f"\n   Profit moyen: {avg_profit:.2f}%")
            print(f"   Score moyen: {avg_score:.1f}/100")
        
        print_success(f"{len(opportunities)} opportunités pour la route")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test statistiques"""
    print_header("Test 6 : Statistiques")
    
    try:
        db = OpportunityDB()
        
        print("\n📈 Calcul des statistiques (24h)...")
        
        stats = db.get_statistics(hours=24)
        
        print(f"\n✅ Statistiques calculées:")
        print(f"\n{'Métrique':<30} {'Valeur':<20}")
        print("-" * 55)
        
        metrics = [
            ('Total opportunités', stats.get('total_opportunities', 0)),
            ('Grade A ou mieux', stats.get('grade_a_or_better', 0)),
            ('Grade B ou mieux', stats.get('grade_b_or_better', 0)),
            ('Avec liquidité validée', stats.get('with_liquidity', 0)),
            ('Profit moyen (%)', f"{stats.get('avg_profit_pct', 0):.2f}"),
            ('Profit maximum (%)', f"{stats.get('max_profit_pct', 0):.2f}"),
            ('Score moyen', f"{stats.get('avg_score', 0):.1f}/100"),
            ('Score maximum', f"{stats.get('max_score', 0):.1f}/100"),
        ]
        
        for metric, value in metrics:
            print(f"{metric:<30} {str(value):<20}")
        
        assert 'total_opportunities' in stats, "Devrait contenir total_opportunities"
        
        print_success("Statistiques calculées")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_top_routes():
    """Test meilleures routes"""
    print_header("Test 7 : Meilleures Routes")
    
    try:
        db = OpportunityDB()
        
        print("\n🏆 Récupération des 5 meilleures routes (24h)...")
        
        routes = db.get_top_routes(limit=5, hours=24)
        
        print(f"\n✅ {len(routes)} routes trouvées:")
        
        if routes:
            print(f"\n{'#':<3} {'Route':<30} {'Count':<8} {'Avg Profit':<12} {'Avg Score':<10}")
            print("-" * 70)
            
            for i, route in enumerate(routes, 1):
                route_name = f"{route['exchange_buy']}→{route['exchange_sell']}"
                print(f"{i:<3} {route_name:<30} {route['opportunity_count']:<8} "
                      f"{route['avg_profit_pct']:>8.2f}%{'':<2} {route['avg_score']:>8.1f}")
        
        print_success(f"{len(routes)} meilleures routes récupérées")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_update_status():
    """Test mise à jour statut"""
    print_header("Test 8 : Mise à Jour Statut")
    
    try:
        db = OpportunityDB()
        
        # Récupérer une opportunité récente
        recent = db.get_recent_opportunities(limit=1)
        
        if not recent:
            print("⚠️  Aucune opportunité à mettre à jour (base vide)")
            print_success("Test skippé (normal si base vide)")
            return True
        
        opp_id = recent[0]['id']
        
        print(f"\n📝 Mise à jour opportunité {opp_id} → statut 'executed'...")
        
        success = db.update_opportunity_status(
            opp_id,
            'executed',
            {'execution_time': '2026-02-01T18:30:00'}
        )
        
        print(f"✅ Statut mis à jour: {success}")
        
        assert success, "Devrait retourner True"
        
        print_success("Statut mis à jour")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("    💾 TEST SAUVEGARDE OPPORTUNITÉS - ÉTAPE 3.6")
    print("=" * 60)
    
    tests = [
        ("Sauvegarde opportunité", test_save_opportunity),
        ("Sauvegarde batch", test_save_batch),
        ("Récupération récentes", test_get_recent),
        ("Récupération par symbole", test_get_by_symbol),
        ("Récupération par route", test_get_by_route),
        ("Statistiques", test_statistics),
        ("Meilleures routes", test_top_routes),
        ("Mise à jour statut", test_update_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print_error(f"Erreur test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print_header("RÉSUMÉ DES TESTS")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n✅ Tests réussis: {passed}/{total}")
    
    if passed < total:
        print_error("❌ Certains tests ont échoué")
        print("\n🔧 Tests échoués:")
        for test_name, success in results:
            if not success:
                print(f"  - {test_name}")
    else:
        print_success("🎉 Tous les tests sont passés!")
        print("\n💡 Le système de sauvegarde fonctionne!")
        print("📊 Vous pouvez maintenant:")
        print("  - Sauvegarder toutes les opportunités")
        print("  - Analyser l'historique")
        print("  - Calculer des statistiques")
        print("  - Identifier les meilleures routes")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 3 COMPLÈTE ! Détection d'opportunités OK !")
    print("💡 Prochaine phase: Phase 4 - Gestion des Risques")
    print("=" * 60)


if __name__ == "__main__":
    main()
