"""
Tests pour l'Étape 5.1 - Dry-Run Executor
==========================================

Teste l'exécution simulée des trades.
"""

from src.execution.dry_run_executor import DryRunExecutor


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
        executor = DryRunExecutor(initial_balance=10000.0)
        
        print(f"\n📊 DryRunExecutor créé:")
        print(f"   Balance initiale: ${executor.initial_balance:,.2f}")
        print(f"   Balance actuelle: ${executor.current_balance:,.2f}")
        print(f"   Trades exécutés: {executor.trades_executed}")
        
        assert executor.initial_balance == 10000.0
        assert executor.current_balance == 10000.0
        assert executor.trades_executed == 0
        
        print_success("Initialisation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execute_profitable_trade():
    """Test exécution trade profitable"""
    print_header("Test 2 : Trade Profitable")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        # Opportunité profitable
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 50000.0,
            'sell_price': 50500.0,  # +1% de spread
            'buy_fee_pct': 0.1,
            'sell_fee_pct': 0.1,
        }
        
        print("\n📊 Exécution trade:")
        print(f"   Achat: {opportunity['exchange_buy']} @ ${opportunity['buy_price']:,.2f}")
        print(f"   Vente: {opportunity['exchange_sell']} @ ${opportunity['sell_price']:,.2f}")
        
        result = executor.execute_arbitrage(opportunity, trade_amount_usd=1000.0)
        
        print(f"\n✅ Résultat:")
        print(f"   Succès: {result['success']}")
        print(f"   Dry-run: {result['dry_run']}")
        print(f"   Profit NET: ${result['net_profit_usd']:+.2f}")
        print(f"   Profit %: {result['net_profit_pct']:+.2f}%")
        print(f"   Temps: {result['execution_time_seconds']:.3f}s")
        print(f"   Balance: ${result['balance_after']:,.2f}")
        
        assert result['success'] == True
        assert result['dry_run'] == True
        assert result['net_profit_usd'] > 0  # Devrait être profitable
        assert executor.current_balance > 10000.0
        assert executor.trades_executed == 1
        
        print_success("Trade profitable exécuté")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execute_losing_trade():
    """Test exécution trade perdant"""
    print_header("Test 3 : Trade Perdant")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        # Opportunité perdante (spread négatif + frais)
        opportunity = {
            'symbol': 'ETH/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 3000.0,
            'sell_price': 2990.0,  # -0.33% de spread
            'buy_fee_pct': 0.1,
            'sell_fee_pct': 0.1,
        }
        
        print("\n📊 Exécution trade perdant:")
        
        result = executor.execute_arbitrage(opportunity, trade_amount_usd=500.0)
        
        print(f"\n❌ Résultat:")
        print(f"   Profit NET: ${result['net_profit_usd']:+.2f}")
        print(f"   Balance: ${result['balance_after']:,.2f}")
        
        assert result['success'] == True
        assert result['net_profit_usd'] < 0
        assert executor.current_balance < 10000.0
        
        print_success("Trade perdant exécuté")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_insufficient_balance():
    """Test balance insuffisante"""
    print_header("Test 4 : Balance Insuffisante")
    
    try:
        executor = DryRunExecutor(initial_balance=100.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 50000.0,
            'sell_price': 50500.0,
        }
        
        print("\n📊 Tentative avec balance insuffisante:")
        print(f"   Balance: ${executor.current_balance:,.2f}")
        print(f"   Montant demandé: $1000.00")
        
        result = executor.execute_arbitrage(opportunity, trade_amount_usd=1000.0)
        
        print(f"\n❌ Résultat:")
        print(f"   Succès: {result['success']}")
        print(f"   Erreur: {result.get('error', 'N/A')}")
        
        assert result['success'] == False
        assert 'balance' in result['error'].lower()
        
        print_success("Balance insuffisante détectée")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_slippage_simulation():
    """Test simulation du slippage"""
    print_header("Test 5 : Simulation Slippage")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 50000.0,
            'sell_price': 50500.0,
        }
        
        print("\n📊 Vérification du slippage:")
        
        result = executor.execute_arbitrage(opportunity, trade_amount_usd=1000.0)
        
        print(f"   Prix achat attendu: ${result['expected_buy_price']:,.2f}")
        print(f"   Prix achat réel:    ${result['actual_buy_price']:,.2f}")
        print(f"   Slippage achat:     {result['buy_slippage_pct']:.3f}%")
        
        print(f"\n   Prix vente attendu: ${result['expected_sell_price']:,.2f}")
        print(f"   Prix vente réel:    ${result['actual_sell_price']:,.2f}")
        print(f"   Slippage vente:     {result['sell_slippage_pct']:.3f}%")
        
        print(f"\n   Slippage total:     {result['total_slippage_pct']:.3f}%")
        
        # Vérifier que le slippage est présent et raisonnable
        assert result['buy_slippage_pct'] >= 0
        assert result['buy_slippage_pct'] <= 0.2
        assert result['sell_slippage_pct'] >= 0
        assert result['sell_slippage_pct'] <= 0.2
        
        print_success("Slippage simulé correctement")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fees_calculation():
    """Test calcul des frais"""
    print_header("Test 6 : Calcul des Frais")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 50000.0,
            'sell_price': 50500.0,
            'buy_fee_pct': 0.1,
            'sell_fee_pct': 0.1,
        }
        
        print("\n📊 Calcul des frais:")
        
        result = executor.execute_arbitrage(opportunity, trade_amount_usd=1000.0)
        
        print(f"   Frais achat:  ${result['buy_fee']:.2f}")
        print(f"   Frais vente:  ${result['sell_fee']:.2f}")
        print(f"   Total frais:  ${result['total_fees']:.2f}")
        
        # Vérifier que les frais sont calculés
        assert result['buy_fee'] > 0
        assert result['sell_fee'] > 0
        assert abs(result['total_fees'] - (result['buy_fee'] + result['sell_fee'])) < 0.01
        
        print_success("Frais calculés correctement")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_trades():
    """Test exécution de plusieurs trades"""
    print_header("Test 7 : Plusieurs Trades")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 50000.0,
            'sell_price': 50500.0,
        }
        
        print("\n📊 Exécution de 5 trades:")
        
        for i in range(5):
            result = executor.execute_arbitrage(opportunity, trade_amount_usd=500.0)
            print(f"   Trade {i+1}: ${result['net_profit_usd']:+.2f}")
        
        print(f"\n📊 Après 5 trades:")
        print(f"   Trades exécutés: {executor.trades_executed}")
        print(f"   Balance: ${executor.current_balance:,.2f}")
        
        assert executor.trades_executed == 5
        assert len(executor.trade_history) == 5
        
        print_success("Plusieurs trades exécutés")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test statistiques"""
    print_header("Test 8 : Statistiques")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        # Exécuter quelques trades
        opportunities = [
            {'symbol': 'BTC/USDT', 'exchange_buy': 'binance', 'exchange_sell': 'kraken',
             'buy_price': 50000, 'sell_price': 50500},  # Profitable
            {'symbol': 'ETH/USDT', 'exchange_buy': 'binance', 'exchange_sell': 'kraken',
             'buy_price': 3000, 'sell_price': 2990},    # Perdant
            {'symbol': 'BTC/USDT', 'exchange_buy': 'binance', 'exchange_sell': 'kraken',
             'buy_price': 50000, 'sell_price': 50600},  # Profitable
        ]
        
        print("\n📊 Exécution de 3 trades:")
        for opp in opportunities:
            executor.execute_arbitrage(opp, trade_amount_usd=1000.0)
        
        stats = executor.get_statistics()
        
        print(f"\n📊 Statistiques:")
        print(f"   Trades: {stats['trades_executed']}")
        print(f"   Gagnants: {stats['wins']}")
        print(f"   Perdants: {stats['losses']}")
        print(f"   Win rate: {stats['win_rate_pct']:.1f}%")
        print(f"   PnL: ${stats['net_pnl']:+.2f}")
        print(f"   ROI: {stats['roi_pct']:+.2f}%")
        
        assert stats['trades_executed'] == 3
        assert stats['wins'] + stats['losses'] == 3
        assert 'net_pnl' in stats
        assert 'roi_pct' in stats
        
        print_success("Statistiques calculées")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reset():
    """Test réinitialisation"""
    print_header("Test 9 : Réinitialisation")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        # Exécuter quelques trades
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 50000.0,
            'sell_price': 50500.0,
        }
        
        for _ in range(3):
            executor.execute_arbitrage(opportunity, trade_amount_usd=500.0)
        
        print(f"\n📊 Avant reset:")
        print(f"   Trades: {executor.trades_executed}")
        print(f"   Balance: ${executor.current_balance:,.2f}")
        
        # Reset
        executor.reset()
        
        print(f"\n📊 Après reset:")
        print(f"   Trades: {executor.trades_executed}")
        print(f"   Balance: ${executor.current_balance:,.2f}")
        
        assert executor.trades_executed == 0
        assert executor.current_balance == 10000.0
        assert len(executor.trade_history) == 0
        
        print_success("Reset OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_display():
    """Test affichage des statistiques"""
    print_header("Test 10 : Affichage")
    
    try:
        executor = DryRunExecutor(initial_balance=10000.0)
        
        # Quelques trades
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'buy_price': 50000.0,
            'sell_price': 50500.0,
        }
        
        for _ in range(5):
            executor.execute_arbitrage(opportunity, trade_amount_usd=500.0)
        
        print("\n📊 Affichage formaté:")
        executor.display_statistics()
        
        print_success("Affichage OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("      🎮 TEST DRY-RUN EXECUTOR - ÉTAPE 5.1")
    print("=" * 60)
    
    tests = [
        ("Initialisation", test_init),
        ("Trade profitable", test_execute_profitable_trade),
        ("Trade perdant", test_execute_losing_trade),
        ("Balance insuffisante", test_insufficient_balance),
        ("Simulation slippage", test_slippage_simulation),
        ("Calcul des frais", test_fees_calculation),
        ("Plusieurs trades", test_multiple_trades),
        ("Statistiques", test_statistics),
        ("Réinitialisation", test_reset),
        ("Affichage", test_display),
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
        print("\n💡 Le Dry-Run Executor fonctionne!")
        print("\n🎮 Fonctionnalités:")
        print("  - Simulation complète des trades")
        print("  - Calcul profit/perte NET")
        print("  - Simulation slippage réaliste")
        print("  - Calcul des frais")
        print("  - Suivi des balances virtuelles")
        print("  - Statistiques complètes")
        print("  - Sauvegarde en DB")
        print("\n⚠️  AUCUN ORDRE RÉEL PLACÉ - 100% SIMULATION")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 5.2 - Simulateur de Slippage")
    print("=" * 60)


if __name__ == "__main__":
    main()
