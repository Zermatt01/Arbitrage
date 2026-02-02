"""
Tests pour l'Étape 5.2 - Slippage Simulator
============================================

Teste le calcul réaliste du slippage.
"""

from src.execution.slippage_simulator import SlippageSimulator


def print_header(text):
    """Affiche un header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Affiche un succès"""
    print(f"✅ {text}")


def print_error(text):
    """Affiche une erreur"""
    print(f"❌ {text}")


def test_init():
    """Test initialisation"""
    print_header("Test 1 : Initialisation")
    
    try:
        simulator = SlippageSimulator()
        
        print(f"\n📊 SlippageSimulator créé")
        
        assert simulator is not None
        
        print_success("Initialisation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_small_order():
    """Test ordre petit (faible slippage)"""
    print_header("Test 2 : Petit Ordre")
    
    try:
        simulator = SlippageSimulator()
        
        # Orderbook avec bonne liquidité
        orderbook = {
            'asks': [
                [50010, 2.0],
                [50020, 3.0],
                [50030, 5.0],
            ]
        }
        
        print("\n📊 Achat de $500 (petit ordre):")
        
        result = simulator.calculate_slippage(orderbook, 'buy', 500.0)
        
        print(f"   Prix référence: $50,010")
        print(f"   Prix moyen: ${result['average_price']:,.2f}")
        print(f"   Slippage: {result['slippage_pct']:.3f}%")
        print(f"   Rempli: {result['filled_pct']:.1f}%")
        print(f"   Niveaux: {result['levels_consumed']}")
        
        # Petit ordre devrait avoir faible slippage
        assert result['slippage_pct'] < 0.1
        assert result['filled_pct'] == 100
        assert result['levels_consumed'] == 1
        
        print_success("Petit ordre OK (faible slippage)")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_large_order():
    """Test ordre gros (fort slippage)"""
    print_header("Test 3 : Gros Ordre")
    
    try:
        simulator = SlippageSimulator()
        
        orderbook = {
            'asks': [
                [50010, 0.05],   # Peu de liquidité (seulement $2,500)
                [50020, 0.05],   # Encore peu ($2,501)
                [50030, 0.05],   # Encore peu ($2,502)
            ]
        }
        
        print("\n📊 Achat de $5,000 (gros ordre):")
        
        result = simulator.calculate_slippage(orderbook, 'buy', 5000.0)
        
        print(f"   Prix référence: $50,010")
        print(f"   Prix moyen: ${result['average_price']:,.2f}")
        print(f"   Slippage: {result['slippage_pct']:.3f}%")
        print(f"   Rempli: {result['filled_pct']:.1f}%")
        print(f"   Niveaux: {result['levels_consumed']}")
        
        # Gros ordre devrait consommer plusieurs niveaux
        assert result['levels_consumed'] > 1
        assert result['slippage_pct'] > 0  # Doit avoir du slippage
        
        print_success("Gros ordre OK (fort slippage)")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_insufficient_liquidity():
    """Test liquidité insuffisante"""
    print_header("Test 4 : Liquidité Insuffisante")
    
    try:
        simulator = SlippageSimulator()
        
        # Orderbook avec peu de liquidité
        orderbook = {
            'asks': [
                [50010, 0.01],  # Très peu
            ]
        }
        
        print("\n📊 Achat de $10,000 (liquidité insuffisante):")
        
        result = simulator.calculate_slippage(orderbook, 'buy', 10000.0)
        
        print(f"   Rempli: {result['filled_pct']:.1f}%")
        print(f"   Restant: ${result['remaining_usd']:,.2f}")
        
        # Ne devrait pas être complètement rempli
        assert result['filled_pct'] < 100
        assert result['remaining_usd'] > 0
        
        print_success("Liquidité insuffisante détectée")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sell_order():
    """Test ordre de vente"""
    print_header("Test 5 : Ordre de Vente")
    
    try:
        simulator = SlippageSimulator()
        
        orderbook = {
            'bids': [
                [49990, 1.0],
                [49980, 2.0],
                [49970, 3.0],
            ]
        }
        
        print("\n📊 Vente de $1,000:")
        
        result = simulator.calculate_slippage(orderbook, 'sell', 1000.0)
        
        print(f"   Prix référence: $49,990")
        print(f"   Prix moyen: ${result['average_price']:,.2f}")
        print(f"   Slippage: {result['slippage_pct']:.3f}%")
        print(f"   Rempli: {result['filled_pct']:.1f}%")
        
        # Vérifier que le prix moyen est calculé
        assert result['average_price'] > 0
        assert result['filled_pct'] == 100
        
        print_success("Vente OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_average_price_calculation():
    """Test calcul du prix moyen"""
    print_header("Test 6 : Calcul Prix Moyen")
    
    try:
        simulator = SlippageSimulator()
        
        # Orderbook simple pour vérifier le calcul
        orderbook = {
            'asks': [
                [100, 1.0],  # 1 @ $100
                [110, 1.0],  # 1 @ $110
            ]
        }
        
        # Acheter pour $200 (devrait acheter les 2 niveaux)
        result = simulator.calculate_slippage(orderbook, 'buy', 210.0)
        
        print(f"\n📊 Calcul:")
        print(f"   Niveau 1: 1 @ $100")
        print(f"   Niveau 2: 1 @ $110")
        print(f"   Prix moyen attendu: $105")
        print(f"   Prix moyen calculé: ${result['average_price']:.2f}")
        
        # Prix moyen devrait être 105 (moyenne de 100 et 110)
        expected_avg = 105.0
        assert abs(result['average_price'] - expected_avg) < 1.0
        
        print_success("Prix moyen correct")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_market_impact():
    """Test estimation d'impact sur le marché"""
    print_header("Test 7 : Impact Marché")
    
    try:
        simulator = SlippageSimulator()
        
        orderbook = {
            'asks': [
                [50010, 0.2],   # $10,002
                [50020, 0.3],   # $15,006
                [50030, 0.5],   # $25,015
            ]
        }
        
        print("\n📊 Estimation d'impact:")
        
        # Petit ordre
        impact_small = simulator.estimate_market_impact(orderbook, 'buy', 500.0)
        print(f"\n   Petit ordre ($500):")
        print(f"     Impact: {impact_small['impact_level']}")
        print(f"     Exécutable: {impact_small['is_executable']}")
        
        # Gros ordre
        impact_large = simulator.estimate_market_impact(orderbook, 'buy', 100000.0)
        print(f"\n   Gros ordre ($100,000):")
        print(f"     Impact: {impact_large['impact_level']}")
        print(f"     Exécutable: {impact_large['is_executable']}")
        
        # Vérifier classifications
        assert impact_small['impact_level'] in ['MINIMAL', 'LOW', 'MEDIUM']
        assert impact_large['impact_level'] in ['MEDIUM', 'HIGH', 'CRITICAL']
        
        print_success("Impact marché calculé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_executable_amount():
    """Test montant maximum exécutable"""
    print_header("Test 8 : Montant Maximum")
    
    try:
        simulator = SlippageSimulator()
        
        orderbook = {
            'asks': [
                [50010, 1.0],   # $50,010
                [50020, 2.0],   # $100,040
                [50030, 3.0],   # $150,090
            ]
        }
        
        print("\n📊 Montant max avec slippage < 0.5%:")
        
        result = simulator.get_executable_amount(
            orderbook, 'buy', max_slippage_pct=0.5
        )
        
        print(f"   Max USD: ${result['max_amount_usd']:,.2f}")
        print(f"   Max quantité: {result['max_quantity']:.4f}")
        print(f"   Slippage: {result['slippage_pct']:.3f}%")
        print(f"   Niveaux: {result['levels_available']}")
        print(f"   Meilleur prix: ${result['best_price']:,.2f}")
        print(f"   Pire prix: ${result['worst_price']:,.2f}")
        
        # Vérifier que le slippage respecte la limite
        assert result['slippage_pct'] <= 0.5
        assert result['max_amount_usd'] > 0
        
        print_success("Montant maximum calculé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_levels_consumed():
    """Test nombre de niveaux consommés"""
    print_header("Test 9 : Niveaux Consommés")
    
    try:
        simulator = SlippageSimulator()
        
        orderbook = {
            'asks': [
                [50010, 0.005],  # Très peu: ~$250
                [50020, 0.015],  # ~$750
                [50030, 0.015],  # ~$750
            ]
        }
        
        print("\n📊 Consommation de niveaux:")
        
        # Petit ordre (1 niveau)
        result1 = simulator.calculate_slippage(orderbook, 'buy', 200.0)
        print(f"   $200: {result1['levels_consumed']} niveau(x)")
        assert result1['levels_consumed'] == 1
        
        # Moyen ordre (2 niveaux)
        result2 = simulator.calculate_slippage(orderbook, 'buy', 500.0)
        print(f"   $500: {result2['levels_consumed']} niveau(x)")
        assert result2['levels_consumed'] == 2
        
        # Gros ordre (3 niveaux)
        result3 = simulator.calculate_slippage(orderbook, 'buy', 1200.0)
        print(f"   $1,200: {result3['levels_consumed']} niveau(x)")
        assert result3['levels_consumed'] == 3
        
        print_success("Niveaux consommés corrects")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_realistic_scenario():
    """Test scénario réaliste BTC"""
    print_header("Test 10 : Scénario Réaliste")
    
    try:
        simulator = SlippageSimulator()
        
        # Orderbook réaliste BTC/USDT
        orderbook = {
            'asks': [
                [50000.00, 0.5],
                [50000.50, 0.8],
                [50001.00, 1.2],
                [50002.00, 1.5],
                [50003.50, 2.0],
                [50005.00, 3.0],
            ]
        }
        
        print("\n📊 Trade réaliste: Achat de $1,000 en BTC")
        
        result = simulator.calculate_slippage(orderbook, 'buy', 1000.0)
        
        print(f"\n   Prix référence: $50,000.00")
        print(f"   Prix moyen: ${result['average_price']:,.2f}")
        print(f"   Slippage: {result['slippage_pct']:.4f}%")
        print(f"   Slippage USD: ${result['slippage_usd']:.2f}")
        print(f"   Quantité: {result['average_price'] and 1000/result['average_price'] or 0:.6f} BTC")
        print(f"   Rempli: {result['filled_pct']:.1f}%")
        print(f"   Niveaux: {result['levels_consumed']}")
        
        # Impact
        impact = simulator.estimate_market_impact(orderbook, 'buy', 1000.0)
        print(f"\n   Impact marché: {impact['impact_level']}")
        print(f"   Ratio liquidité: {impact['liquidity_ratio']:.2%}")
        
        # Vérifications
        assert result['filled_pct'] == 100
        assert result['slippage_pct'] < 0.5  # Devrait être faible
        assert impact['is_executable'] == True
        
        print_success("Scénario réaliste OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("      📉 TEST SLIPPAGE SIMULATOR - ÉTAPE 5.2")
    print("=" * 60)
    
    tests = [
        ("Initialisation", test_init),
        ("Petit ordre", test_small_order),
        ("Gros ordre", test_large_order),
        ("Liquidité insuffisante", test_insufficient_liquidity),
        ("Ordre de vente", test_sell_order),
        ("Calcul prix moyen", test_average_price_calculation),
        ("Impact marché", test_market_impact),
        ("Montant maximum", test_executable_amount),
        ("Niveaux consommés", test_levels_consumed),
        ("Scénario réaliste", test_realistic_scenario),
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
    else:
        print_success("🎉 Tous les tests sont passés!")
        print("\n💡 Le Slippage Simulator fonctionne!")
        print("\n📉 Fonctionnalités:")
        print("  - Analyse de l'orderbook réel")
        print("  - Calcul du prix moyen d'exécution")
        print("  - Estimation du slippage précis")
        print("  - Détection de liquidité insuffisante")
        print("  - Estimation d'impact marché")
        print("  - Calcul du montant maximum tradable")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 5.3 - Orchestrateur de Trading")
    print("=" * 60)


if __name__ == "__main__":
    main()
