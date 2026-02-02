"""
Tests pour l'Étape 3.3 - Analyseur d'Arbitrage Simple
======================================================

Teste l'analyseur d'arbitrage avec calcul des frais.
"""

from src.collectors.price_collector import PriceCollector
import time


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


def test_spreads_with_fees():
    """Test calcul des spreads avec frais"""
    print_header("Test 1 : Spreads avec Calcul des Frais")
    
    try:
        # Créer le collecteur
        collector = PriceCollector(['binance', 'kraken'])
        
        # Collecter et analyser
        print("\n📊 Collecte des prix BTC/USDT...")
        result = collector.collect_and_analyze('BTC/USDT', save_to_db=False, trade_amount_usd=1000)
        
        # Afficher les spreads
        print(f"\n📈 {len(result['spreads'])} spread(s) calculé(s):")
        print("-" * 60)
        
        for spread in result['spreads']:
            print(f"\n{spread['exchange_buy']} → {spread['exchange_sell']}")
            print(f"  Prix achat: ${spread['buy_price']:,.2f}")
            print(f"  Prix vente: ${spread['sell_price']:,.2f}")
            print(f"  Spread BRUT: {spread['spread_pct']:+.2f}%")
            print(f"  Frais: {spread.get('total_fees_pct', 0):.2f}%")
            print(f"  Profit NET: {spread.get('net_profit_pct', 0):+.2f}%")
            
            if spread.get('is_profitable', False):
                print(f"  ✅ RENTABLE (${spread.get('net_profit_usd', 0):.2f})")
            else:
                print(f"  ❌ PAS RENTABLE")
        
        # Vérifications
        assert len(result['spreads']) > 0, "Devrait avoir au moins 1 spread"
        
        # Vérifier que les nouveaux champs sont présents
        for spread in result['spreads']:
            assert 'net_profit_pct' in spread, "Manque net_profit_pct"
            assert 'total_fees_pct' in spread, "Manque total_fees_pct"
            assert 'is_profitable' in spread, "Manque is_profitable"
        
        collector.disconnect_all()
        print_success("Calcul des spreads avec frais OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_opportunities_detection():
    """Test détection d'opportunités rentables"""
    print_header("Test 2 : Détection d'Opportunités")
    
    try:
        collector = PriceCollector(['binance', 'kraken'])
        
        # Collecter plusieurs fois pour augmenter les chances
        print("\n🔍 Collecte de 3 échantillons...")
        
        all_opportunities = []
        
        for i in range(3):
            result = collector.collect_and_analyze('BTC/USDT', save_to_db=False, trade_amount_usd=10000)
            
            print(f"\nÉchantillon {i+1}:")
            print(f"  Spreads: {len(result['spreads'])}")
            print(f"  Opportunités (NET > 0.5%): {len(result['opportunities'])}")
            
            if result['opportunities']:
                for opp in result['opportunities']:
                    print(f"    💰 {opp['exchange_buy']}→{opp['exchange_sell']}: "
                          f"NET {opp['net_profit_pct']:+.2f}% (${opp['net_profit_usd']:,.2f})")
                    all_opportunities.append(opp)
            
            time.sleep(2)
        
        # Résumé
        print(f"\n📊 Résumé:")
        print(f"  Total opportunités détectées: {len(all_opportunities)}")
        
        if all_opportunities:
            avg_profit = sum(o['net_profit_pct'] for o in all_opportunities) / len(all_opportunities)
            print(f"  Profit NET moyen: {avg_profit:.2f}%")
            print_success("Opportunités détectées !")
        else:
            print(f"  ⚠️  Aucune opportunité > 0.5% (normal, les vraies opportunités sont rares)")
            print_success("Système de détection fonctionnel (pas d'opportunité pour l'instant)")
        
        collector.disconnect_all()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_amounts():
    """Test avec différents montants de trade"""
    print_header("Test 3 : Différents Montants")
    
    try:
        collector = PriceCollector(['binance', 'kraken'])
        
        amounts = [1000, 5000, 10000]
        
        print("\n📊 Analyse avec différents montants:")
        print("-" * 60)
        
        for amount in amounts:
            result = collector.collect_and_analyze('BTC/USDT', save_to_db=False, trade_amount_usd=amount)
            
            if result['spreads']:
                spread = result['spreads'][0]
                print(f"\nMontant: ${amount:,}")
                print(f"  Spread BRUT: {spread['spread_pct']:+.2f}%")
                print(f"  Profit NET: {spread['net_profit_pct']:+.2f}%")
                print(f"  Profit USD: ${spread['net_profit_usd']:,.2f}")
            
            time.sleep(1)
        
        collector.disconnect_all()
        print_success("Test avec différents montants OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison_before_after():
    """Test comparaison avant/après intégration des frais"""
    print_header("Test 4 : Impact des Frais")
    
    try:
        collector = PriceCollector(['binance', 'kraken'])
        
        result = collector.collect_and_analyze('BTC/USDT', save_to_db=False, trade_amount_usd=1000)
        
        if result['spreads']:
            print("\n💡 Impact des frais sur la rentabilité:")
            print("-" * 60)
            
            for spread in result['spreads']:
                spread_brut = spread['spread_pct']
                spread_net = spread['net_profit_pct']
                fees = spread['total_fees_pct']
                
                print(f"\n{spread['exchange_buy']} → {spread['exchange_sell']}")
                print(f"  AVANT (spread brut): {spread_brut:+.2f}%")
                print(f"  Frais: -{fees:.2f}%")
                print(f"  APRÈS (profit net): {spread_net:+.2f}%")
                
                impact = spread_brut - spread_net
                print(f"  Impact: -{impact:.2f}% ({impact/spread_brut*100:.1f}% du spread)")
                
                # Exemple concret
                if spread_brut > 0:
                    print(f"\n  📈 Exemple sur $10,000:")
                    print(f"     Profit apparent: ${spread_brut * 100:.2f}")
                    print(f"     Profit réel: ${spread_net * 100:.2f}")
        
        collector.disconnect_all()
        print_success("Comparaison avant/après OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stats():
    """Test statistiques du collecteur"""
    print_header("Test 5 : Statistiques")
    
    try:
        collector = PriceCollector(['binance', 'kraken'])
        
        # Faire plusieurs collectes
        for _ in range(3):
            collector.collect_and_analyze('BTC/USDT', save_to_db=False)
            time.sleep(1)
        
        # Récupérer les stats
        stats = collector.get_stats()
        
        print("\n📊 Statistiques du collecteur:")
        print(f"  Collections totales: {stats['total_collections']}")
        print(f"  Collections réussies: {stats['successful_collections']}")
        print(f"  Opportunités détectées: {stats['opportunities_detected']}")
        print(f"  Taux d'erreur: {stats['error_rate']:.2%}")
        
        assert stats['total_collections'] >= 3, "Devrait avoir au moins 3 collections"
        
        collector.disconnect_all()
        print_success("Statistiques OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("     📊 TEST ANALYSEUR D'ARBITRAGE - ÉTAPE 3.3")
    print("=" * 60)
    
    tests = [
        ("Spreads avec frais", test_spreads_with_fees),
        ("Détection opportunités", test_opportunities_detection),
        ("Différents montants", test_different_amounts),
        ("Impact des frais", test_comparison_before_after),
        ("Statistiques", test_stats),
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
        print("\n💡 L'analyseur d'arbitrage est prêt !")
        print("📊 Il calcule maintenant le profit NET après frais")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 3.4 - Validateur de liquidité")
    print("=" * 60)


if __name__ == "__main__":
    main()
