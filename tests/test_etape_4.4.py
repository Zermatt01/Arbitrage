"""
Tests pour l'Étape 4.4 - Circuit Breaker
=========================================

Teste le système d'arrêt d'urgence.
"""

from src.risk.circuit_breaker import CircuitBreaker
import time


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
        cb = CircuitBreaker()
        
        print(f"\n📊 CircuitBreaker créé:")
        print(f"   État: {'OUVERT' if cb.is_open() else 'FERMÉ'}")
        print(f"   Erreurs consécutives: {cb.consecutive_errors}")
        print(f"   Pertes récentes: {len(cb.loss_history)}")
        
        assert cb.is_open() == False
        assert cb.consecutive_errors == 0
        assert len(cb.loss_history) == 0
        
        print_success("Initialisation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_normal_operation():
    """Test fonctionnement normal"""
    print_header("Test 2 : Fonctionnement Normal")
    
    try:
        cb = CircuitBreaker()
        
        print("\n📊 Enregistrement de pertes normales:")
        
        # Pertes normales (en dessous du seuil)
        for i in range(3):
            cb.check_and_trip(loss_usd=20.0)
            print(f"   Perte #{i+1}: $20")
        
        print(f"\n   État circuit: {'OUVERT' if cb.is_open() else 'FERMÉ'}")
        
        assert cb.is_open() == False
        
        print_success("Fonctionnement normal OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_excessive_loss():
    """Test déclenchement sur perte excessive"""
    print_header("Test 3 : Perte Excessive")
    
    try:
        cb = CircuitBreaker({
            'max_loss_in_minutes': 100.0,
            'loss_window_minutes': 15
        })
        
        print("\n📊 Simulation pertes excessives:")
        
        # Pertes qui dépassent le seuil
        for i in range(3):
            cb.check_and_trip(loss_usd=40.0)
            print(f"   Perte #{i+1}: $40 (total: ${(i+1)*40})")
            
            if cb.is_open():
                print(f"   🚨 CIRCUIT DÉCLENCHÉ!")
                break
        
        status = cb.get_status()
        print(f"\n   Raison: {status['trip_reason']}")
        
        assert cb.is_open() == True
        assert status['recent_loss_usd'] >= 100.0
        
        print_success("Déclenchement sur perte OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_consecutive_errors():
    """Test déclenchement sur erreurs consécutives"""
    print_header("Test 4 : Erreurs Consécutives")
    
    try:
        cb = CircuitBreaker({
            'max_consecutive_errors': 3
        })
        
        print("\n📊 Simulation erreurs consécutives:")
        
        for i in range(5):
            cb.check_and_trip(error_occurred=True, error_type='NetworkError')
            print(f"   Erreur #{i+1}: Consécutives = {cb.consecutive_errors}")
            
            if cb.is_open():
                print(f"   🚨 CIRCUIT DÉCLENCHÉ!")
                break
        
        status = cb.get_status()
        print(f"\n   Raison: {status['trip_reason']}")
        
        assert cb.is_open() == True
        assert cb.consecutive_errors >= 3
        
        print_success("Déclenchement sur erreurs OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_reset():
    """Test reset des erreurs consécutives sur succès"""
    print_header("Test 5 : Reset Erreurs")
    
    try:
        cb = CircuitBreaker({
            'max_consecutive_errors': 5
        })
        
        print("\n📊 Erreurs puis succès:")
        
        # 2 erreurs
        cb.check_and_trip(error_occurred=True)
        cb.check_and_trip(error_occurred=True)
        print(f"   Après 2 erreurs: {cb.consecutive_errors}")
        
        # Succès (pas d'erreur)
        cb.check_and_trip(error_occurred=False)
        print(f"   Après succès: {cb.consecutive_errors}")
        
        assert cb.consecutive_errors == 0
        assert cb.is_open() == False
        
        print_success("Reset erreurs OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_balance_threshold():
    """Test déclenchement sur balance trop basse"""
    print_header("Test 6 : Balance Trop Basse")
    
    try:
        cb = CircuitBreaker({
            'min_balance_threshold_pct': 50
        })
        
        # Balance initiale
        cb.check_and_trip(current_balance=5000.0)
        print(f"\n📊 Balance initiale: $5000")
        
        # Balance descend progressivement
        balances = [4500, 4000, 3500, 2900, 2400]
        
        for balance in balances:
            cb.check_and_trip(current_balance=balance)
            pct = (balance / 5000.0) * 100
            print(f"   Balance: ${balance} ({pct:.1f}%)")
            
            if cb.is_open():
                print(f"   🚨 CIRCUIT DÉCLENCHÉ!")
                break
        
        status = cb.get_status()
        print(f"\n   Raison: {status['trip_reason']}")
        
        assert cb.is_open() == True
        assert status['balance_pct'] < 50
        
        print_success("Déclenchement sur balance OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_manual_reset():
    """Test reset manuel"""
    print_header("Test 7 : Reset Manuel")
    
    try:
        cb = CircuitBreaker({
            'max_consecutive_errors': 2
        })
        
        # Déclencher le circuit
        print("\n📊 Déclenchement:")
        cb.check_and_trip(error_occurred=True)
        cb.check_and_trip(error_occurred=True)
        
        print(f"   État: {'OUVERT' if cb.is_open() else 'FERMÉ'}")
        assert cb.is_open() == True
        
        # Reset manuel
        print("\n📊 Reset manuel:")
        cb.reset()
        
        print(f"   État: {'OUVERT' if cb.is_open() else 'FERMÉ'}")
        assert cb.is_open() == False
        
        print_success("Reset manuel OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_reset():
    """Test auto-reset après délai"""
    print_header("Test 8 : Auto-Reset")
    
    try:
        cb = CircuitBreaker({
            'max_consecutive_errors': 2,
            'auto_reset_minutes': 0.01  # 0.6 secondes pour test rapide
        })
        
        # Déclencher
        print("\n📊 Déclenchement:")
        cb.check_and_trip(error_occurred=True)
        cb.check_and_trip(error_occurred=True)
        
        print(f"   État: {'OUVERT' if cb.is_open() else 'FERMÉ'}")
        assert cb.is_open() == True
        
        # Attendre auto-reset
        print("\n⏳ Attente auto-reset (1s)...")
        time.sleep(1)
        
        # Vérifier état
        is_open = cb.is_open()
        print(f"   État après attente: {'OUVERT' if is_open else 'FERMÉ'}")
        
        assert is_open == False
        
        print_success("Auto-reset OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_status():
    """Test récupération du statut"""
    print_header("Test 9 : Récupération Statut")
    
    try:
        cb = CircuitBreaker()
        cb.check_and_trip(current_balance=5000.0)
        
        # Quelques actions
        cb.check_and_trip(loss_usd=30.0)
        cb.check_and_trip(error_occurred=True)
        cb.check_and_trip(current_balance=4800.0)
        
        # Récupérer statut
        status = cb.get_status()
        
        print(f"\n📊 Statut:")
        print(f"   État: {'OUVERT' if status['is_open'] else 'FERMÉ'}")
        print(f"   Perte récente: ${status['recent_loss_usd']:.2f}")
        print(f"   Erreurs consécutives: {status['consecutive_errors']}")
        print(f"   Erreurs/heure: {status['errors_in_hour']}")
        print(f"   Balance: ${status['current_balance']:.2f} ({status['balance_pct']:.1f}%)")
        
        assert 'is_open' in status
        assert 'recent_loss_usd' in status
        assert 'consecutive_errors' in status
        
        print_success("Statut récupéré")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_display():
    """Test affichage du statut"""
    print_header("Test 10 : Affichage Statut")
    
    try:
        cb = CircuitBreaker()
        cb.check_and_trip(current_balance=5000.0)
        
        # Quelques actions
        cb.check_and_trip(loss_usd=25.0)
        cb.check_and_trip(error_occurred=True)
        
        print("\n📊 Affichage formaté:")
        cb.display_status()
        
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
    print("      🚨 TEST CIRCUIT BREAKER - ÉTAPE 4.4")
    print("=" * 60)
    
    tests = [
        ("Initialisation", test_init),
        ("Fonctionnement normal", test_normal_operation),
        ("Perte excessive", test_excessive_loss),
        ("Erreurs consécutives", test_consecutive_errors),
        ("Reset erreurs", test_error_reset),
        ("Balance trop basse", test_balance_threshold),
        ("Reset manuel", test_manual_reset),
        ("Auto-reset", test_auto_reset),
        ("Récupération statut", test_get_status),
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
        print("\n💡 Le Circuit Breaker fonctionne!")
        print("\n🚨 Protection automatique:")
        print("  - Arrêt sur perte excessive")
        print("  - Arrêt sur erreurs consécutives")
        print("  - Arrêt sur balance trop basse")
        print("  - Reset manuel possible")
        print("  - Auto-reset après délai")
    
    print("\n" + "=" * 60)
    print("🎉 PHASE 4 COMPLÈTE ! Gestion des risques OK !")
    print("💡 Prochaine phase: Phase 5 - Exécution des Trades")
    print("=" * 60)


if __name__ == "__main__":
    main()
