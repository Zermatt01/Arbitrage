"""
Tests pour l'Étape 3.4 - Validateur de Liquidité
=================================================

Teste la validation de liquidité et le calcul du slippage.
"""

from src.validators.liquidity_validator import LiquidityValidator
from src.connectors.exchange_factory import ExchangeFactory
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


def test_execution_price_calculation():
    """Test calcul du prix d'exécution"""
    print_header("Test 1 : Calcul Prix d'Exécution")
    
    try:
        validator = LiquidityValidator()
        
        # Orderbook simulé
        asks = [
            [81235.45, 0.5],   # Niveau 1
            [81240.00, 1.2],   # Niveau 2
            [81250.00, 2.0],   # Niveau 3
            [81300.00, 3.5],   # Niveau 4
        ]
        
        # Test avec différents montants
        test_amounts = [0.3, 1.0, 3.0, 10.0]
        
        print(f"\n{'Montant (BTC)':<15} {'Prix Moyen':<15} {'Slippage':<12} {'Niveaux':<10}")
        print("-" * 55)
        
        for amount in test_amounts:
            result = validator.calculate_execution_price(asks, amount)
            
            print(f"{amount:<15.2f} "
                  f"${result['avg_price']:<14,.2f} "
                  f"{result['slippage_pct']:<11.2f}% "
                  f"{result['levels_used']:<10}")
            
            # Vérifications
            if amount <= 0.5:
                # Devrait prendre seulement le premier niveau
                assert result['levels_used'] == 1, "Devrait utiliser 1 niveau"
                assert result['slippage_pct'] == 0, "Pas de slippage"
            
            if amount == 1.0:
                # Devrait prendre niveaux 1 et 2
                assert result['levels_used'] == 2, "Devrait utiliser 2 niveaux"
                assert result['slippage_pct'] > 0, "Devrait avoir du slippage"
        
        print_success("Calcul prix d'exécution OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_buy_liquidity_validation():
    """Test validation liquidité achat"""
    print_header("Test 2 : Validation Liquidité Achat")
    
    try:
        validator = LiquidityValidator(max_slippage_pct=0.5)
        
        orderbook = {
            'asks': [
                [81235.45, 0.5],
                [81240.00, 1.2],
                [81250.00, 2.0],
            ]
        }
        
        # Test 1 : Petit montant (devrait passer)
        print("\n📊 Test avec $1,000:")
        result = validator.validate_buy_liquidity(orderbook, 1000)
        
        print(f"  Valide: {result['valid']}")
        print(f"  Prix moyen: ${result.get('avg_price', 0):,.2f}")
        print(f"  Slippage: {result.get('slippage_pct', 0):.2f}%")
        print(f"  Raison: {result['reason']}")
        
        assert result['valid'], "Petit montant devrait être valide"
        assert result['slippage_pct'] < 0.5, "Slippage devrait être faible"
        
        # Test 2 : Gros montant (devrait échouer - liquidité insuffisante)
        print("\n📊 Test avec $1,000,000:")
        result = validator.validate_buy_liquidity(orderbook, 1000000)
        
        print(f"  Valide: {result['valid']}")
        print(f"  Raison: {result['reason']}")
        
        assert not result['valid'], "Gros montant devrait échouer"
        
        print_success("Validation liquidité achat OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sell_liquidity_validation():
    """Test validation liquidité vente"""
    print_header("Test 3 : Validation Liquidité Vente")
    
    try:
        validator = LiquidityValidator(max_slippage_pct=0.5)
        
        orderbook = {
            'bids': [
                [81200.00, 0.8],
                [81195.00, 1.5],
                [81190.00, 2.2],
            ]
        }
        
        # Test 1 : Petit montant
        print("\n📊 Test vente de 0.5 BTC:")
        result = validator.validate_sell_liquidity(orderbook, 0.5)
        
        print(f"  Valide: {result['valid']}")
        print(f"  Prix moyen: ${result.get('avg_price', 0):,.2f}")
        print(f"  Slippage: {result.get('slippage_pct', 0):.2f}%")
        
        assert result['valid'], "Petit montant devrait être valide"
        
        # Test 2 : Gros montant
        print("\n📊 Test vente de 10 BTC:")
        result = validator.validate_sell_liquidity(orderbook, 10)
        
        print(f"  Valide: {result['valid']}")
        print(f"  Raison: {result['reason']}")
        
        assert not result['valid'], "Gros montant devrait échouer"
        
        print_success("Validation liquidité vente OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arbitrage_validation():
    """Test validation arbitrage complet"""
    print_header("Test 4 : Validation Arbitrage Complet")
    
    try:
        validator = LiquidityValidator(max_slippage_pct=0.5)
        
        # Orderbooks simulés
        buy_orderbook = {
            'asks': [
                [81235.45, 1.0],
                [81240.00, 2.0],
                [81250.00, 3.0],
            ]
        }
        
        sell_orderbook = {
            'bids': [
                [81300.00, 1.0],  # Meilleur prix (spread positif)
                [81295.00, 2.0],
                [81290.00, 3.0],
            ]
        }
        
        print("\n📊 Validation arbitrage $10,000:")
        result = validator.validate_arbitrage_liquidity(
            buy_orderbook,
            sell_orderbook,
            10000
        )
        
        print(f"\n{'Détail':<25} {'Valeur':<20}")
        print("-" * 50)
        print(f"{'Valide':<25} {result['valid']}")
        
        if result['valid']:
            print(f"{'Prix achat moyen':<25} ${result['buy_avg_price']:,.2f}")
            print(f"{'Slippage achat':<25} {result['buy_slippage_pct']:.2f}%")
            print(f"{'Prix vente moyen':<25} ${result['sell_avg_price']:,.2f}")
            print(f"{'Slippage vente':<25} {result['sell_slippage_pct']:.2f}%")
            print(f"{'Slippage total':<25} {result['total_slippage_pct']:.2f}%")
            print(f"{'Profit brut':<25} {result['gross_profit_pct']:+.2f}%")
            print(f"{'Profit USD':<25} ${result['gross_profit_usd']:,.2f}")
        else:
            print(f"{'Raison':<25} {result['reason']}")
        
        print_success("Validation arbitrage OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_orderbooks():
    """Test avec orderbooks réels"""
    print_header("Test 5 : Orderbooks Réels")
    
    try:
        validator = LiquidityValidator(max_slippage_pct=0.5)
        
        # Créer les connecteurs
        binance = ExchangeFactory.create('binance')
        kraken = ExchangeFactory.create('kraken')
        
        binance.connect()
        kraken.connect()
        
        print("\n📊 Récupération orderbooks BTC/USDT...")
        
        # Récupérer les orderbooks réels
        ob_binance = binance.get_orderbook('BTC/USDT', limit=20)
        ob_kraken = kraken.get_orderbook('BTC/USDT', limit=20)
        
        print(f"\nBinance - Best ask: ${ob_binance['stats']['best_ask']:,.2f}")
        print(f"Kraken  - Best bid: ${ob_kraken['stats']['best_bid']:,.2f}")
        
        # Test avec différents montants
        amounts = [1000, 5000, 10000]
        
        print(f"\n{'Montant':<12} {'Buy Slip':<12} {'Sell Slip':<12} {'Total Slip':<12} {'Valide':<10}")
        print("-" * 60)
        
        for amount in amounts:
            result = validator.validate_arbitrage_liquidity(
                ob_binance,
                ob_kraken,
                amount
            )
            
            if result['valid']:
                status = "✅"
                buy_slip = result['buy_slippage_pct']
                sell_slip = result['sell_slippage_pct']
                total_slip = result['total_slippage_pct']
            else:
                status = "❌"
                buy_slip = result.get('buy_validation', {}).get('slippage_pct', 0)
                sell_slip = result.get('sell_validation', {}).get('slippage_pct', 0) if result.get('sell_validation') else 0
                total_slip = buy_slip + sell_slip
            
            print(f"${amount:<11,} {buy_slip:<11.2f}% {sell_slip:<11.2f}% {total_slip:<11.2f}% {status:<10}")
        
        binance.disconnect()
        kraken.disconnect()
        
        print_success("Test orderbooks réels OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_liquidity_depth():
    """Test analyse profondeur liquidité"""
    print_header("Test 6 : Profondeur de Liquidité")
    
    try:
        validator = LiquidityValidator()
        
        binance = ExchangeFactory.create('binance')
        binance.connect()
        
        print("\n📊 Analyse profondeur Binance BTC/USDT...")
        
        orderbook = binance.get_orderbook('BTC/USDT', limit=20)
        depth = validator.get_liquidity_depth(orderbook, depth_levels=10)
        
        print(f"\nProfondeur sur 10 niveaux:")
        print(f"  Volume asks: {depth['ask_volume']:.4f} BTC")
        print(f"  Valeur asks: ${depth['ask_value_usd']:,.2f}")
        print(f"  Volume bids: {depth['bid_volume']:.4f} BTC")
        print(f"  Valeur bids: ${depth['bid_value_usd']:,.2f}")
        print(f"  Volume total: {depth['total_volume']:.4f} BTC")
        print(f"  Valeur totale: ${depth['total_value_usd']:,.2f}")
        
        binance.disconnect()
        
        print_success("Analyse profondeur OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("      🔍 TEST VALIDATEUR DE LIQUIDITÉ - ÉTAPE 3.4")
    print("=" * 60)
    
    tests = [
        ("Calcul prix d'exécution", test_execution_price_calculation),
        ("Validation achat", test_buy_liquidity_validation),
        ("Validation vente", test_sell_liquidity_validation),
        ("Validation arbitrage", test_arbitrage_validation),
        ("Orderbooks réels", test_real_orderbooks),
        ("Profondeur liquidité", test_liquidity_depth),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            time.sleep(1)
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
        print("\n💡 Le validateur de liquidité fonctionne parfaitement!")
        print("📊 Il calcule maintenant:")
        print("  - Le prix moyen d'exécution RÉEL")
        print("  - Le slippage exact")
        print("  - La liquidité disponible")
        print("  - La faisabilité de chaque trade")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: Intégrer au PriceCollector")
    print("=" * 60)


if __name__ == "__main__":
    main()
