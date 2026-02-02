"""
Tests pour l'Étape 4.1 - Configuration des Limites
===================================================

Teste la configuration et validation des limites.
"""

from src.risk.limits_config import LimitsConfig
import os


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


def test_default_limits():
    """Test chargement des limites par défaut"""
    print_header("Test 1 : Limites Par Défaut")
    
    try:
        limits = LimitsConfig()
        
        print(f"\n📊 Limites chargées:")
        print(f"   Max trade:           ${limits.max_trade_amount}")
        print(f"   Min trade:           ${limits.min_trade_amount}")
        print(f"   Max daily trades:    {limits.max_daily_trades}")
        print(f"   Max daily loss:      ${limits.max_daily_loss}")
        print(f"   Min profit:          {limits.min_profit_pct}%")
        print(f"   Min score:           {limits.min_score}/100")
        
        assert limits.max_trade_amount == 100.0
        assert limits.min_trade_amount == 10.0
        assert limits.max_daily_trades == 50
        
        print_success("Limites par défaut OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_update_limit():
    """Test modification d'une limite"""
    print_header("Test 2 : Modification de Limite")
    
    try:
        limits = LimitsConfig()
        
        # Modifier
        old_value = limits.max_trade_amount
        new_value = 500.0
        
        print(f"\n📝 Modification: max_trade_amount")
        print(f"   Ancienne valeur: ${old_value}")
        print(f"   Nouvelle valeur: ${new_value}")
        
        success = limits.update_limit('max_trade_amount', new_value)
        
        assert success
        assert limits.max_trade_amount == new_value
        
        print_success("Modification OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test validation des limites"""
    print_header("Test 3 : Validation")
    
    try:
        limits = LimitsConfig()
        
        # Config valide
        print("\n✅ Test config valide:")
        if limits.validate_limits():
            print("   ✅ Configuration valide")
        else:
            print("   ❌ Configuration invalide")
            return False
        
        # Config invalide (min > max)
        print("\n❌ Test config invalide (min > max):")
        limits.update_limit('min_trade_amount', 200.0)
        limits.update_limit('max_trade_amount', 100.0)
        
        if not limits.validate_limits():
            print("   ✅ Erreur bien détectée")
        else:
            print("   ❌ Erreur NON détectée")
            return False
        
        print_success("Validation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_save_load():
    """Test sauvegarde et rechargement"""
    print_header("Test 4 : Sauvegarde et Rechargement")
    
    try:
        # Créer config
        limits1 = LimitsConfig()
        
        # Modifier
        limits1.update_limit('max_trade_amount', 750.0)
        limits1.update_limit('max_daily_trades', 100)
        
        # Sauvegarder
        print("\n💾 Sauvegarde...")
        success = limits1.save_config()
        assert success
        print(f"   ✅ Sauvegardé dans {limits1.config_file}")
        
        # Recharger
        print("\n📂 Rechargement...")
        limits2 = LimitsConfig()
        
        print(f"   Max trade: ${limits2.max_trade_amount}")
        print(f"   Max daily: {limits2.max_daily_trades}")
        
        assert limits2.max_trade_amount == 750.0
        assert limits2.max_daily_trades == 100
        
        # Nettoyer
        if os.path.exists(limits1.config_file):
            os.remove(limits1.config_file)
        
        print_success("Sauvegarde/rechargement OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reset():
    """Test réinitialisation"""
    print_header("Test 5 : Réinitialisation")
    
    try:
        limits = LimitsConfig()
        
        # Modifier
        limits.update_limit('max_trade_amount', 999.0)
        print(f"\n📝 Modifié: ${limits.max_trade_amount}")
        
        # Reset
        print("\n🔄 Réinitialisation...")
        limits.reset_to_defaults()
        
        print(f"   Après reset: ${limits.max_trade_amount}")
        
        assert limits.max_trade_amount == 100.0
        
        print_success("Réinitialisation OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_properties():
    """Test accès via properties"""
    print_header("Test 6 : Properties")
    
    try:
        limits = LimitsConfig()
        
        print(f"\n📊 Accès via properties:")
        print(f"   max_trade_amount:    ${limits.max_trade_amount}")
        print(f"   min_trade_amount:    ${limits.min_trade_amount}")
        print(f"   max_daily_trades:    {limits.max_daily_trades}")
        print(f"   max_daily_loss:      ${limits.max_daily_loss}")
        print(f"   min_profit_pct:      {limits.min_profit_pct}%")
        print(f"   min_score:           {limits.min_score}/100")
        print(f"   max_slippage_pct:    {limits.max_slippage_pct}%")
        
        assert isinstance(limits.max_trade_amount, float)
        assert isinstance(limits.max_daily_trades, int)
        
        print_success("Properties OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_display():
    """Test affichage formaté"""
    print_header("Test 7 : Affichage")
    
    try:
        limits = LimitsConfig()
        
        print("\n📊 Affichage formaté:")
        limits.display_limits()
        
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
    print("    ⚙️  TEST CONFIGURATION LIMITES - ÉTAPE 4.1")
    print("=" * 60)
    
    tests = [
        ("Limites par défaut", test_default_limits),
        ("Modification", test_update_limit),
        ("Validation", test_validation),
        ("Sauvegarde/Rechargement", test_save_load),
        ("Réinitialisation", test_reset),
        ("Properties", test_properties),
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
        print("\n💡 Le système de limites fonctionne!")
        print("\n📊 Vous pouvez maintenant:")
        print("  - Définir des limites de trading")
        print("  - Modifier les limites dynamiquement")
        print("  - Sauvegarder la configuration")
        print("  - Valider la cohérence")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 4.2 - Risk Manager")
    print("=" * 60)


if __name__ == "__main__":
    main()
