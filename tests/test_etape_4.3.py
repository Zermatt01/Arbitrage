"""
Tests pour l'Étape 4.3 - Daily Tracker
=======================================

Teste le suivi des performances quotidiennes.
"""

from src.risk.daily_tracker import DailyTracker


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
        tracker = DailyTracker()
        
        print(f"\n📊 DailyTracker créé:")
        print(f"   Trades: {tracker.trades_count}")
        print(f"   Wins: {tracker.wins_count}")
        print(f"   Losses: {tracker.losses_count}")
        print(f"   Total profit: ${tracker.total_profit_usd:.2f}")
        
        assert tracker.trades_count >= 0
        assert tracker.wins_count >= 0
        assert tracker.losses_count >= 0
        
        print_success("Initialisation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_record_win():
    """Test enregistrement trade gagnant"""
    print_header("Test 2 : Trade Gagnant")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()  # Reset pour test propre
        
        print("\n📊 Enregistrement trade gagnant +$25:")
        tracker.record_trade(25.0, True, 'BTC/USDT')
        
        print(f"   Trades: {tracker.trades_count}")
        print(f"   Wins: {tracker.wins_count}")
        print(f"   Total profit: ${tracker.total_profit_usd:.2f}")
        print(f"   Best trade: ${tracker.best_trade_usd:.2f}")
        print(f"   Win streak: {tracker.current_win_streak}")
        
        assert tracker.trades_count == 1
        assert tracker.wins_count == 1
        assert tracker.losses_count == 0
        assert tracker.total_profit_usd == 25.0
        assert tracker.best_trade_usd == 25.0
        assert tracker.current_win_streak == 1
        
        print_success("Trade gagnant enregistré")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_record_loss():
    """Test enregistrement trade perdant"""
    print_header("Test 3 : Trade Perdant")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        print("\n📊 Enregistrement trade perdant -$15:")
        tracker.record_trade(-15.0, False, 'ETH/USDT')
        
        print(f"   Trades: {tracker.trades_count}")
        print(f"   Losses: {tracker.losses_count}")
        print(f"   Total loss: ${tracker.total_loss_usd:.2f}")
        print(f"   Worst trade: ${tracker.worst_trade_usd:.2f}")
        print(f"   Loss streak: {tracker.current_loss_streak}")
        
        assert tracker.trades_count == 1
        assert tracker.wins_count == 0
        assert tracker.losses_count == 1
        assert tracker.total_loss_usd == 15.0
        assert tracker.worst_trade_usd == -15.0
        assert tracker.current_loss_streak == 1
        
        print_success("Trade perdant enregistré")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_trades():
    """Test plusieurs trades"""
    print_header("Test 4 : Plusieurs Trades")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        print("\n📊 Enregistrement de 5 trades:")
        trades = [
            (24.50, True),
            (-12.00, False),
            (18.75, True),
            (32.00, True),
            (-8.50, False),
        ]
        
        for profit, is_win in trades:
            tracker.record_trade(profit, is_win)
            status = "✅" if is_win else "❌"
            print(f"   {status} ${profit:+.2f}")
        
        print(f"\n📊 Statistiques:")
        print(f"   Total trades: {tracker.trades_count}")
        print(f"   Wins: {tracker.wins_count}")
        print(f"   Losses: {tracker.losses_count}")
        
        assert tracker.trades_count == 5
        assert tracker.wins_count == 3
        assert tracker.losses_count == 2
        
        print_success("Plusieurs trades enregistrés")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_win_rate():
    """Test calcul win rate"""
    print_header("Test 5 : Win Rate")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        # 7 trades: 5 wins, 2 losses
        trades = [
            (10, True), (15, True), (-5, False),
            (20, True), (12, True), (-8, False),
            (18, True)
        ]
        
        for profit, is_win in trades:
            tracker.record_trade(profit, is_win)
        
        stats = tracker.get_stats()
        
        print(f"\n📊 Résultats:")
        print(f"   Trades: {stats['trades_count']}")
        print(f"   Wins: {stats['wins_count']}")
        print(f"   Losses: {stats['losses_count']}")
        print(f"   Win rate: {stats['win_rate_pct']:.1f}%")
        
        expected_win_rate = (5 / 7) * 100
        assert abs(stats['win_rate_pct'] - expected_win_rate) < 0.1
        
        print_success(f"Win rate calculé: {stats['win_rate_pct']:.1f}%")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pnl_calculation():
    """Test calcul PnL net"""
    print_header("Test 6 : Calcul PnL")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        trades = [
            (25.50, True),
            (-12.00, False),
            (18.75, True),
            (-8.25, False),
        ]
        
        for profit, is_win in trades:
            tracker.record_trade(profit, is_win)
        
        stats = tracker.get_stats()
        
        print(f"\n📊 PnL:")
        print(f"   Total profit: +${stats['total_profit_usd']:.2f}")
        print(f"   Total loss:   -${stats['total_loss_usd']:.2f}")
        print(f"   NET:          ${stats['net_pnl_usd']:+.2f}")
        
        expected_profit = 25.50 + 18.75
        expected_loss = 12.00 + 8.25
        expected_net = expected_profit - expected_loss
        
        assert abs(stats['total_profit_usd'] - expected_profit) < 0.01
        assert abs(stats['total_loss_usd'] - expected_loss) < 0.01
        assert abs(stats['net_pnl_usd'] - expected_net) < 0.01
        
        print_success(f"PnL net: ${stats['net_pnl_usd']:+.2f}")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_best_worst():
    """Test meilleur/pire trade"""
    print_header("Test 7 : Meilleur/Pire Trade")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        trades = [
            (10.0, True),
            (25.0, True),  # Meilleur
            (-5.0, False),
            (-15.0, False),  # Pire
            (12.0, True),
        ]
        
        for profit, is_win in trades:
            tracker.record_trade(profit, is_win)
        
        stats = tracker.get_stats()
        
        print(f"\n📊 Extrêmes:")
        print(f"   Meilleur: +${stats['best_trade_usd']:.2f}")
        print(f"   Pire:     ${stats['worst_trade_usd']:.2f}")
        
        assert stats['best_trade_usd'] == 25.0
        assert stats['worst_trade_usd'] == -15.0
        
        print_success("Meilleur/pire identifiés")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_win_streak():
    """Test série de gains"""
    print_header("Test 8 : Série de Gains")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        print("\n📊 Simulation série de 4 gains:")
        
        for i in range(4):
            tracker.record_trade(10.0, True)
            print(f"   Win #{i+1}: Streak = {tracker.current_win_streak}")
        
        # Perte pour casser la série
        tracker.record_trade(-5.0, False)
        print(f"   Loss: Streak = {tracker.current_win_streak}")
        
        stats = tracker.get_stats()
        
        print(f"\n📊 Résultats:")
        print(f"   Max win streak: {stats['max_win_streak']}")
        print(f"   Current win streak: {stats['current_win_streak']}")
        
        assert stats['max_win_streak'] == 4
        assert stats['current_win_streak'] == 0
        
        print_success("Série de gains trackée")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_loss_streak():
    """Test série de pertes"""
    print_header("Test 9 : Série de Pertes")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        print("\n📊 Simulation série de 3 pertes:")
        
        for i in range(3):
            tracker.record_trade(-10.0, False)
            print(f"   Loss #{i+1}: Streak = {tracker.current_loss_streak}")
        
        # Gain pour casser la série
        tracker.record_trade(20.0, True)
        print(f"   Win: Streak = {tracker.current_loss_streak}")
        
        stats = tracker.get_stats()
        
        print(f"\n📊 Résultats:")
        print(f"   Max loss streak: {stats['max_loss_streak']}")
        print(f"   Current loss streak: {stats['current_loss_streak']}")
        
        assert stats['max_loss_streak'] == 3
        assert stats['current_loss_streak'] == 0
        
        print_success("Série de pertes trackée")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_display():
    """Test affichage des stats"""
    print_header("Test 10 : Affichage Stats")
    
    try:
        tracker = DailyTracker()
        tracker.reset_stats()
        
        # Quelques trades
        trades = [
            (25.0, True), (-10.0, False), (18.0, True),
            (30.0, True), (-5.0, False)
        ]
        
        for profit, is_win in trades:
            tracker.record_trade(profit, is_win)
        
        print("\n📊 Affichage formaté:")
        tracker.display_stats()
        
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
    print("      📊 TEST DAILY TRACKER - ÉTAPE 4.3")
    print("=" * 60)
    
    tests = [
        ("Initialisation", test_init),
        ("Trade gagnant", test_record_win),
        ("Trade perdant", test_record_loss),
        ("Plusieurs trades", test_multiple_trades),
        ("Win rate", test_win_rate),
        ("Calcul PnL", test_pnl_calculation),
        ("Meilleur/Pire", test_best_worst),
        ("Série gains", test_win_streak),
        ("Série pertes", test_loss_streak),
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
        print("\n💡 Le Daily Tracker fonctionne!")
        print("\n📊 Métriques suivies:")
        print("  - Nombre de trades (wins/losses)")
        print("  - Profit/perte total et net")
        print("  - Win rate")
        print("  - Meilleur/pire trade")
        print("  - Moyennes par trade")
        print("  - Séries de gains/pertes")
        print("  - Sauvegarde automatique en DB")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 4.4 - Circuit Breaker")
    print("=" * 60)


if __name__ == "__main__":
    main()
