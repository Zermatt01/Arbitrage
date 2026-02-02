"""
Tests pour l'Étape 4.2 - Risk Manager
======================================

Teste la validation pre-trade et la gestion des risques.
"""

from src.risk.risk_manager import RiskManager
from src.risk.limits_config import LimitsConfig


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
        rm = RiskManager()
        
        print(f"\n📊 RiskManager créé:")
        print(f"   Trades today: {rm.daily_trades_count}")
        print(f"   PnL today: ${rm.daily_profit_loss:.2f}")
        print(f"   Consecutive losses: {rm.consecutive_losses}")
        
        assert rm.daily_trades_count == 0
        assert rm.daily_profit_loss == 0.0
        assert rm.consecutive_losses == 0
        
        print_success("Initialisation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_valid_trade():
    """Test trade valide"""
    print_header("Test 2 : Trade Valide")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'net_profit_pct': 0.8,
            'total_score': 87.5,
            'total_slippage_pct': 0.1,
            'liquidity_valid': True
        }
        
        print("\n📊 Validation trade $100:")
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        
        print(f"   Autorisé: {can_trade}")
        print(f"   Raison: {reason}")
        
        assert can_trade == True
        assert reason == "OK"
        
        print_success("Trade valide accepté")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_amount_too_low():
    """Test montant trop faible"""
    print_header("Test 3 : Montant Trop Faible")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.8,
            'total_score': 90.0
        }
        
        print("\n📊 Validation trade $5 (min: $10):")
        can_trade, reason = rm.can_trade(opportunity, 5.0)
        
        print(f"   Autorisé: {can_trade}")
        print(f"   Raison: {reason}")
        
        assert can_trade == False
        assert "trop faible" in reason.lower()
        
        print_success("Montant trop faible refusé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_amount_too_high():
    """Test montant trop élevé"""
    print_header("Test 4 : Montant Trop Élevé")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.8,
            'total_score': 90.0
        }
        
        print("\n📊 Validation trade $500 (max: $100):")
        can_trade, reason = rm.can_trade(opportunity, 500.0)
        
        print(f"   Autorisé: {can_trade}")
        print(f"   Raison: {reason}")
        
        assert can_trade == False
        assert "trop élevé" in reason.lower()
        
        print_success("Montant trop élevé refusé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_profit_too_low():
    """Test profit insuffisant"""
    print_header("Test 5 : Profit Insuffisant")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.2,  # Min requis: 0.5%
            'total_score': 90.0
        }
        
        print("\n📊 Validation trade avec profit 0.2% (min: 0.5%):")
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        
        print(f"   Autorisé: {can_trade}")
        print(f"   Raison: {reason}")
        
        assert can_trade == False
        assert "profit" in reason.lower()
        
        print_success("Profit insuffisant refusé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_score_too_low():
    """Test score trop faible"""
    print_header("Test 6 : Score Trop Faible")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.8,
            'total_score': 50.0  # Min requis: 70
        }
        
        print("\n📊 Validation trade avec score 50/100 (min: 70):")
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        
        print(f"   Autorisé: {can_trade}")
        print(f"   Raison: {reason}")
        
        assert can_trade == False
        assert "score" in reason.lower()
        
        print_success("Score trop faible refusé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_slippage_too_high():
    """Test slippage trop élevé"""
    print_header("Test 7 : Slippage Trop Élevé")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.8,
            'total_score': 90.0,
            'total_slippage_pct': 0.8  # Max: 0.5%
        }
        
        print("\n📊 Validation trade avec slippage 0.8% (max: 0.5%):")
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        
        print(f"   Autorisé: {can_trade}")
        print(f"   Raison: {reason}")
        
        assert can_trade == False
        assert "slippage" in reason.lower()
        
        print_success("Slippage trop élevé refusé")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_no_liquidity():
    """Test liquidité insuffisante"""
    print_header("Test 8 : Liquidité Insuffisante")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.8,
            'total_score': 90.0,
            'liquidity_valid': False
        }
        
        print("\n📊 Validation trade avec liquidité invalide:")
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        
        print(f"   Autorisé: {can_trade}")
        print(f"   Raison: {reason}")
        
        assert can_trade == False
        assert "liquidité" in reason.lower()
        
        print_success("Liquidité insuffisante refusée")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_daily_limit():
    """Test limite quotidienne"""
    print_header("Test 9 : Limite Quotidienne")
    
    try:
        # Config avec limite basse pour test
        limits = LimitsConfig()
        limits.update_limit('max_daily_trades', 3)
        
        rm = RiskManager(limits)
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.8,
            'total_score': 90.0
        }
        
        print("\n📊 Simulation de 4 trades (max: 3):")
        
        # Trades 1-3 : OK
        for i in range(1, 4):
            can_trade, reason = rm.can_trade(opportunity, 100.0)
            rm.record_trade_result(10.0, True)
            print(f"   Trade {i}: {can_trade} - {reason}")
        
        # Trade 4 : Refusé
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        print(f"   Trade 4: {can_trade} - {reason}")
        
        assert can_trade == False
        assert "limite quotidienne" in reason.lower()
        
        print_success("Limite quotidienne respectée")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_consecutive_losses():
    """Test pertes consécutives"""
    print_header("Test 10 : Pertes Consécutives")
    
    try:
        # Config avec limite basse pour test
        limits = LimitsConfig()
        limits.update_limit('max_consecutive_losses', 3)
        
        rm = RiskManager(limits)
        rm.update_balance(5000.0)
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'net_profit_pct': 0.8,
            'total_score': 90.0
        }
        
        print("\n📊 Simulation de 3 pertes consécutives:")
        
        # 3 pertes
        for i in range(1, 4):
            rm.record_trade_result(-10.0, False)
            print(f"   Perte {i}: Consécutives = {rm.consecutive_losses}")
        
        # Trade suivant refusé
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        print(f"   Trade suivant: {can_trade} - {reason}")
        
        assert can_trade == False
        assert "consécutives" in reason.lower()
        
        # Reset avec un profit
        print("\n   🔄 Profit pour reset:")
        rm.record_trade_result(10.0, True)
        print(f"   Consécutives après profit: {rm.consecutive_losses}")
        
        # Trade OK maintenant
        can_trade, reason = rm.can_trade(opportunity, 100.0)
        print(f"   Trade après profit: {can_trade} - {reason}")
        
        assert can_trade == True
        
        print_success("Pertes consécutives gérées")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_daily_stats():
    """Test statistiques quotidiennes"""
    print_header("Test 11 : Statistiques Quotidiennes")
    
    try:
        rm = RiskManager()
        rm.update_balance(5000.0)
        
        # Enregistrer quelques trades
        rm.record_trade_result(24.50, True)
        rm.record_trade_result(-12.00, False)
        rm.record_trade_result(18.75, True)
        
        # Récupérer stats
        stats = rm.get_daily_stats()
        
        print(f"\n📊 Statistiques:")
        print(f"   Date: {stats['date']}")
        print(f"   Trades: {stats['trades_count']}")
        print(f"   Restants: {stats['trades_remaining']}")
        print(f"   PnL: ${stats['profit_loss_usd']:.2f}")
        print(f"   Balance: ${stats['current_balance_usd']:.2f}")
        
        assert stats['trades_count'] == 3
        assert abs(stats['profit_loss_usd'] - 31.25) < 0.01
        
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
    print("      🛡️  TEST RISK MANAGER - ÉTAPE 4.2")
    print("=" * 60)
    
    tests = [
        ("Initialisation", test_init),
        ("Trade valide", test_valid_trade),
        ("Montant trop faible", test_amount_too_low),
        ("Montant trop élevé", test_amount_too_high),
        ("Profit insuffisant", test_profit_too_low),
        ("Score trop faible", test_score_too_low),
        ("Slippage trop élevé", test_slippage_too_high),
        ("Liquidité insuffisante", test_no_liquidity),
        ("Limite quotidienne", test_daily_limit),
        ("Pertes consécutives", test_consecutive_losses),
        ("Statistiques", test_daily_stats),
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
        print("\n💡 Le Risk Manager fonctionne!")
        print("\n🛡️ Protection activée:")
        print("  - Limites de montants respectées")
        print("  - Limites quotidiennes respectées")
        print("  - Pertes consécutives bloquées")
        print("  - Score minimum validé")
        print("  - Profit minimum validé")
        print("  - Slippage contrôlé")
        print("  - Liquidité vérifiée")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 4.3 - Tracker de Performance")
    print("=" * 60)


if __name__ == "__main__":
    main()
