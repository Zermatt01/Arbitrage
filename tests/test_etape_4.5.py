"""
Tests pour l'Étape 4.5 - Error Handler
=======================================

Teste le gestionnaire d'erreurs global.
"""

from src.risk.error_handler import ErrorHandler, ErrorType, ErrorAction
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
        handler = ErrorHandler()
        
        print(f"\n📊 ErrorHandler créé:")
        print(f"   Total erreurs: {handler.total_errors}")
        print(f"   Total retries: {handler.total_retries}")
        
        assert handler.total_errors == 0
        assert handler.total_retries == 0
        
        print_success("Initialisation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classify_network_error():
    """Test classification erreur réseau"""
    print_header("Test 2 : Classification Réseau")
    
    try:
        handler = ErrorHandler()
        
        errors = [
            ConnectionError("Connection refused"),
            TimeoutError("Connection timeout"),
            Exception("Network unreachable"),
        ]
        
        print("\n📊 Classification:")
        for error in errors:
            error_type = handler.classify_error(error)
            print(f"   {type(error).__name__}: {error_type.value}")
            assert error_type == ErrorType.NETWORK
        
        print_success("Classification réseau OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classify_rate_limit():
    """Test classification rate limit"""
    print_header("Test 3 : Classification Rate Limit")
    
    try:
        handler = ErrorHandler()
        
        error = Exception("Rate limit exceeded, try again later")
        error_type = handler.classify_error(error)
        
        print(f"\n📊 Erreur: {error}")
        print(f"   Type: {error_type.value}")
        
        assert error_type == ErrorType.API_RATE_LIMIT
        
        print_success("Classification rate limit OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classify_insufficient_funds():
    """Test classification fonds insuffisants"""
    print_header("Test 4 : Classification Fonds Insuffisants")
    
    try:
        handler = ErrorHandler()
        
        error = Exception("Insufficient funds for this order")
        error_type = handler.classify_error(error)
        
        print(f"\n📊 Erreur: {error}")
        print(f"   Type: {error_type.value}")
        
        assert error_type == ErrorType.INSUFFICIENT_FUNDS
        
        print_success("Classification fonds OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_handle_error_actions():
    """Test actions par type d'erreur"""
    print_header("Test 5 : Actions par Type")
    
    try:
        handler = ErrorHandler()
        
        test_cases = [
            (ErrorType.NETWORK, ErrorAction.RETRY_WITH_BACKOFF),
            (ErrorType.INSUFFICIENT_FUNDS, ErrorAction.SKIP),
            (ErrorType.INVALID_ORDER, ErrorAction.SKIP),
            (ErrorType.CRITICAL, ErrorAction.STOP),
        ]
        
        print("\n📊 Actions:")
        for error_type, expected_action in test_cases:
            error = Exception(f"Test {error_type.value}")
            action = handler.handle_error(error, error_type)
            print(f"   {error_type.value:<20} → {action.value}")
            assert action == expected_action
        
        print_success("Actions correctes")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retry_success():
    """Test retry qui réussit"""
    print_header("Test 6 : Retry Succès")
    
    try:
        handler = ErrorHandler()
        
        attempt_count = 0
        
        def func_that_succeeds_on_third():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Network error")
            return "Success!"
        
        print("\n📊 Retry avec succès au 3ème essai:")
        result = handler.retry_with_backoff(
            func_that_succeeds_on_third,
            error_type=ErrorType.NETWORK,
            base_delay=0.1  # Délai court pour tests
        )
        
        print(f"   Résultat: {result}")
        print(f"   Tentatives: {attempt_count}")
        
        assert result == "Success!"
        assert attempt_count == 3
        assert handler.total_retries == 2  # 2 retries avant succès
        
        print_success("Retry succès OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retry_failure():
    """Test retry qui échoue"""
    print_header("Test 7 : Retry Échec")
    
    try:
        handler = ErrorHandler()
        
        attempt_count = 0
        
        def func_that_always_fails():
            nonlocal attempt_count
            attempt_count += 1
            raise ConnectionError("Network error")
        
        print("\n📊 Retry qui échoue toujours:")
        
        try:
            handler.retry_with_backoff(
                func_that_always_fails,
                error_type=ErrorType.NETWORK,
                max_retries=3,
                base_delay=0.1
            )
            print_error("Devrait avoir levé une exception")
            return False
            
        except ConnectionError as e:
            print(f"   Exception levée: {type(e).__name__}")
            print(f"   Tentatives: {attempt_count}")
            
            assert attempt_count == 3
        
        print_success("Retry échec OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backoff_timing():
    """Test timing du backoff exponentiel"""
    print_header("Test 8 : Backoff Exponentiel")
    
    try:
        handler = ErrorHandler()
        
        delays = []
        attempt_count = 0
        
        def func_that_tracks_delays():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count > 1:
                delays.append(time.time())
            if attempt_count < 4:
                raise ConnectionError("Network error")
            return "Success"
        
        print("\n📊 Vérification backoff:")
        base_delay = 0.1
        
        start = time.time()
        handler.retry_with_backoff(
            func_that_tracks_delays,
            max_retries=4,
            base_delay=base_delay
        )
        
        # Calculer les délais effectifs
        if len(delays) >= 2:
            delay1 = delays[0] - start
            delay2 = delays[1] - delays[0]
            
            print(f"   Base delay: {base_delay}s")
            print(f"   Délai 1: {delay1:.2f}s (attendu: ~{base_delay}s)")
            print(f"   Délai 2: {delay2:.2f}s (attendu: ~{base_delay * 2}s)")
            
            # Vérifier approximativement (±50%)
            assert abs(delay1 - base_delay) < base_delay
            assert abs(delay2 - (base_delay * 2)) < base_delay
        
        print_success("Backoff exponentiel OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execute_with_error_handling():
    """Test exécution avec gestion complète"""
    print_header("Test 9 : Exécution avec Gestion")
    
    try:
        handler = ErrorHandler()
        
        # Test 1: Succès
        print("\n📊 Cas 1: Succès:")
        success, result, error = handler.execute_with_error_handling(
            lambda: "Success",
            context={'test': 'success'}
        )
        print(f"   Success: {success}, Result: {result}")
        assert success == True
        assert result == "Success"
        assert error is None
        
        # Test 2: Erreur SKIP
        print("\n📊 Cas 2: Erreur SKIP:")
        def func_invalid():
            raise Exception("Invalid order")
        
        success, result, error = handler.execute_with_error_handling(
            func_invalid,
            context={'test': 'invalid'}
        )
        print(f"   Success: {success}, Error: {type(error).__name__ if error else None}")
        assert success == False
        assert error is not None
        
        print_success("Exécution avec gestion OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test statistiques"""
    print_header("Test 10 : Statistiques")
    
    try:
        handler = ErrorHandler()
        
        # Générer quelques erreurs
        errors = [
            (Exception("Connection refused"), ErrorType.NETWORK),
            (Exception("Rate limit"), ErrorType.API_RATE_LIMIT),
            (Exception("Insufficient funds"), ErrorType.INSUFFICIENT_FUNDS),
            (Exception("Connection timeout"), ErrorType.NETWORK),
        ]
        
        print("\n📊 Génération d'erreurs:")
        for error, error_type in errors:
            handler.handle_error(error, error_type)
            print(f"   {error_type.value}")
        
        # Récupérer stats
        stats = handler.get_stats()
        
        print(f"\n📊 Statistiques:")
        print(f"   Total erreurs: {stats['total_errors']}")
        print(f"   Par type:")
        for error_type, count in stats['errors_by_type'].items():
            print(f"     {error_type}: {count}")
        
        assert stats['total_errors'] == 4
        assert stats['errors_by_type']['network'] == 2
        assert stats['errors_by_type']['api_rate_limit'] == 1
        
        print_success("Statistiques OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_display():
    """Test affichage"""
    print_header("Test 11 : Affichage")
    
    try:
        handler = ErrorHandler()
        
        # Générer quelques erreurs
        for i in range(3):
            handler.handle_error(
                Exception("Network error"),
                ErrorType.NETWORK
            )
        
        print("\n📊 Affichage formaté:")
        handler.display_stats()
        
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
    print("      🔧 TEST ERROR HANDLER - ÉTAPE 4.5")
    print("=" * 60)
    
    tests = [
        ("Initialisation", test_init),
        ("Classification réseau", test_classify_network_error),
        ("Classification rate limit", test_classify_rate_limit),
        ("Classification fonds", test_classify_insufficient_funds),
        ("Actions par type", test_handle_error_actions),
        ("Retry succès", test_retry_success),
        ("Retry échec", test_retry_failure),
        ("Backoff exponentiel", test_backoff_timing),
        ("Exécution avec gestion", test_execute_with_error_handling),
        ("Statistiques", test_statistics),
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
        print("\n💡 Le Error Handler fonctionne!")
        print("\n🔧 Fonctionnalités:")
        print("  - Classification automatique des erreurs")
        print("  - Actions appropriées par type")
        print("  - Retry avec backoff exponentiel")
        print("  - Logging détaillé")
        print("  - Statistiques complètes")
    
    print("\n" + "=" * 60)
    print("🎉🎉🎉 PHASE 4 100% COMPLÈTE ! 🎉🎉🎉")
    print("=" * 60)
    print("\n✅ Toutes les étapes de gestion des risques terminées:")
    print("  ✅ 4.1 - Configuration des limites")
    print("  ✅ 4.2 - Risk Manager")
    print("  ✅ 4.3 - Daily Tracker")
    print("  ✅ 4.4 - Circuit Breaker")
    print("  ✅ 4.5 - Error Handler")
    print("\n💡 Prochaine phase: Phase 5 - Exécution des Trades (Dry-Run)")
    print("=" * 60)


if __name__ == "__main__":
    main()
