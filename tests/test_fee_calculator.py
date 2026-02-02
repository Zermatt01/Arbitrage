"""
Tests pour l'Étape 3.2 - Calculateur de Frais
==============================================

Teste le calcul des frais de trading et du profit net.
"""

from src.utils.fee_calculator import FeeCalculator


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


def test_get_trading_fee():
    """Test récupération des frais"""
    print_header("Test 1 : Récupération des Frais")
    
    try:
        calculator = FeeCalculator()
        
        # Test Binance
        binance_maker = calculator.get_trading_fee('binance', 'maker')
        binance_taker = calculator.get_trading_fee('binance', 'taker')
        
        print(f"Binance:")
        print(f"  Maker: {binance_maker}%")
        print(f"  Taker: {binance_taker}%")
        
        # Test Kraken
        kraken_maker = calculator.get_trading_fee('kraken', 'maker')
        kraken_taker = calculator.get_trading_fee('kraken', 'taker')
        
        print(f"\nKraken:")
        print(f"  Maker: {kraken_maker}%")
        print(f"  Taker: {kraken_taker}%")
        
        # Vérifications
        assert binance_maker == 0.10, "Frais Binance maker incorrect"
        assert binance_taker == 0.10, "Frais Binance taker incorrect"
        assert kraken_maker == 0.16, "Frais Kraken maker incorrect"
        assert kraken_taker == 0.26, "Frais Kraken taker incorrect"
        
        print_success("Récupération des frais OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calculate_trade_fees():
    """Test calcul des frais d'un trade"""
    print_header("Test 2 : Calcul Frais d'un Trade")
    
    try:
        calculator = FeeCalculator()
        
        # Test avec $1,000 sur Binance
        fees = calculator.calculate_trade_fees('binance', 1000, 'taker')
        
        print(f"Trade de $1,000 sur Binance (taker):")
        print(f"  Frais: {fees['fee_pct']}% = ${fees['fee_usd']:.2f}")
        print(f"  Montant net: ${fees['net_amount']:.2f}")
        
        # Vérifications
        assert fees['fee_pct'] == 0.10, "Frais % incorrect"
        assert abs(fees['fee_usd'] - 1.0) < 0.01, "Frais USD incorrect"
        assert abs(fees['net_amount'] - 999.0) < 0.01, "Montant net incorrect"
        
        # Test avec Kraken
        fees_kraken = calculator.calculate_trade_fees('kraken', 1000, 'taker')
        
        print(f"\nTrade de $1,000 sur Kraken (taker):")
        print(f"  Frais: {fees_kraken['fee_pct']}% = ${fees_kraken['fee_usd']:.2f}")
        print(f"  Montant net: ${fees_kraken['net_amount']:.2f}")
        
        assert fees_kraken['fee_pct'] == 0.26, "Frais Kraken incorrect"
        
        print_success("Calcul des frais OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arbitrage_profit_simple():
    """Test calcul profit d'arbitrage simple"""
    print_header("Test 3 : Profit d'Arbitrage Simple")
    
    try:
        calculator = FeeCalculator()
        
        # Scénario : Spread de 0.6%
        result = calculator.calculate_arbitrage_profit(
            buy_exchange='binance',
            sell_exchange='kraken',
            buy_price=83000,
            sell_price=83500,  # +0.6% de spread
            trade_amount_usd=1000
        )
        
        print(f"Scénario:")
        print(f"  Acheter Binance @ ${result['buy_price']:,.2f}")
        print(f"  Vendre Kraken   @ ${result['sell_price']:,.2f}")
        print(f"  Montant: ${result['trade_amount_usd']:,.2f}")
        
        print(f"\nCrypto:")
        print(f"  Quantité: {result['crypto_amount']:.6f} BTC")
        
        print(f"\nFrais:")
        print(f"  Achat (Binance): ${result['buy_fee_usd']:.2f} ({result['buy_fee_pct']}%)")
        print(f"  Vente (Kraken): ${result['sell_fee_usd']:.2f} ({result['sell_fee_pct']}%)")
        print(f"  Total: ${result['total_fees_usd']:.2f} ({result['total_fees_pct']:.2f}%)")
        
        print(f"\nProfit:")
        print(f"  BRUT: ${result['gross_profit_usd']:.2f} ({result['gross_profit_pct']:+.2f}%)")
        print(f"  NET:  ${result['net_profit_usd']:.2f} ({result['net_profit_pct']:+.2f}%)")
        
        print(f"\n{'✅ RENTABLE' if result['is_profitable'] else '❌ PAS RENTABLE'}")
        print(f"Spread minimum: {result['min_spread_needed_pct']:.2f}%")
        
        # Vérifications
        assert result['is_profitable'], "Devrait être rentable"
        assert result['net_profit_pct'] > 0, "Profit NET devrait être positif"
        
        print_success("Calcul arbitrage OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arbitrage_profit_scenarios():
    """Test différents scénarios d'arbitrage"""
    print_header("Test 4 : Différents Scénarios")
    
    try:
        calculator = FeeCalculator()
        
        scenarios = [
            {
                'name': 'Petit spread (0.3%) - PAS RENTABLE',
                'buy': 83000,
                'sell': 83250,
                'expected_profitable': False
            },
            {
                'name': 'Spread moyen (0.6%) - RENTABLE',
                'buy': 83000,
                'sell': 83500,
                'expected_profitable': True
            },
            {
                'name': 'Gros spread (1.5%) - TRÈS RENTABLE',
                'buy': 83000,
                'sell': 84245,
                'expected_profitable': True
            }
        ]
        
        print(f"\n{'Scénario':<35} {'Spread':<10} {'NET':<10} {'Rentable':<10}")
        print("-" * 70)
        
        for scenario in scenarios:
            result = calculator.calculate_arbitrage_profit(
                buy_exchange='binance',
                sell_exchange='kraken',
                buy_price=scenario['buy'],
                sell_price=scenario['sell'],
                trade_amount_usd=1000
            )
            
            spread_pct = ((scenario['sell'] - scenario['buy']) / scenario['buy']) * 100
            status = '✅' if result['is_profitable'] else '❌'
            
            print(f"{scenario['name']:<35} {spread_pct:<9.2f}% "
                  f"{result['net_profit_pct']:<9.2f}% {status:<10}")
            
            # Vérification
            assert result['is_profitable'] == scenario['expected_profitable'], \
                f"Rentabilité incorrecte pour {scenario['name']}"
        
        print_success("Scénarios testés OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_compare_exchanges():
    """Test comparaison des frais entre exchanges"""
    print_header("Test 5 : Comparaison Exchanges")
    
    try:
        calculator = FeeCalculator()
        
        comparison = calculator.compare_exchanges_fees()
        
        print(f"\n{'Exchange':<15} {'Maker':<10} {'Taker':<10} {'Moyenne':<10}")
        print("-" * 50)
        
        for exc in comparison[:5]:  # Top 5
            print(f"{exc['exchange']:<15} {exc['maker']:<9.2f}% "
                  f"{exc['taker']:<9.2f}% {exc['average']:<9.2f}%")
        
        # Vérifier que c'est bien trié
        for i in range(len(comparison) - 1):
            assert comparison[i]['average'] <= comparison[i+1]['average'], \
                "La liste n'est pas triée correctement"
        
        print_success("Comparaison OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_world_example():
    """Test avec un exemple du monde réel"""
    print_header("Test 6 : Exemple Réel")
    
    try:
        calculator = FeeCalculator()
        
        print("\n📊 Exemple: Opportunité détectée sur BTC/USDT")
        print("-" * 60)
        
        # Prix réels d'aujourd'hui
        result = calculator.calculate_arbitrage_profit(
            buy_exchange='binance',
            sell_exchange='kraken',
            buy_price=83204.56,  # Prix réel vu dans les tests
            sell_price=83197.20,  # Prix réel
            trade_amount_usd=10000  # Trade de $10k
        )
        
        print(f"\n💰 Trade de ${result['trade_amount_usd']:,.2f}:")
        print(f"   Acheter {result['crypto_amount']:.6f} BTC sur {result['buy_exchange']}")
        print(f"   @ ${result['buy_price']:,.2f}")
        print(f"   Vendre sur {result['sell_exchange']} @ ${result['sell_price']:,.2f}")
        
        print(f"\n💸 Frais:")
        print(f"   {result['buy_exchange']}: ${result['buy_fee_usd']:,.2f}")
        print(f"   {result['sell_exchange']}: ${result['sell_fee_usd']:,.2f}")
        print(f"   Total: ${result['total_fees_usd']:,.2f} ({result['total_fees_pct']:.2f}%)")
        
        print(f"\n📈 Résultat:")
        print(f"   Profit BRUT: ${result['gross_profit_usd']:,.2f} ({result['gross_profit_pct']:+.2f}%)")
        print(f"   Profit NET:  ${result['net_profit_usd']:,.2f} ({result['net_profit_pct']:+.2f}%)")
        
        if result['is_profitable']:
            print(f"\n✅ OPPORTUNITÉ RENTABLE!")
            print(f"   ROI: {result['net_profit_pct']:.2f}%")
        else:
            print(f"\n❌ PAS RENTABLE")
            print(f"   Il faudrait un spread de {result['min_spread_needed_pct']:.2f}%")
        
        print_success("Exemple réel OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("        💰 TEST FEE CALCULATOR - ÉTAPE 3.2")
    print("=" * 60)
    
    tests = [
        ("Récupération frais", test_get_trading_fee),
        ("Calcul frais trade", test_calculate_trade_fees),
        ("Profit arbitrage simple", test_arbitrage_profit_simple),
        ("Différents scénarios", test_arbitrage_profit_scenarios),
        ("Comparaison exchanges", test_compare_exchanges),
        ("Exemple réel", test_real_world_example),
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
        print("\n💡 Le calculateur de frais est prêt à l'emploi!")
        print("📊 Vous pouvez maintenant calculer le profit NET de vos trades")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 3.3 - Analyseur d'arbitrage (déjà fait)")
    print("=" * 60)


if __name__ == "__main__":
    main()
