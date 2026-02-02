"""
Tests pour l'Étape 3.5 - Système de Scoring
============================================

Teste le scoring et classement des opportunités.
"""

from projet_arbitrage.src.analyzers.opportunity_scorer import OpportunityScorer


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


def test_score_profit():
    """Test scoring du profit"""
    print_header("Test 1 : Score Profit (0-40 points)")
    
    try:
        scorer = OpportunityScorer()
        
        test_cases = [
            (0.0, 0),
            (0.5, 10),
            (1.0, 20),
            (2.0, 40),
            (5.0, 40),
        ]
        
        print(f"\n{'Profit NET':<15} {'Score Attendu':<15} {'Score Réel':<15}")
        print("-" * 50)
        
        for profit_pct, expected in test_cases:
            score = scorer.score_profit(profit_pct)
            print(f"{profit_pct:<14.1f}% {expected:<15} {score:<15.1f}")
            
            # Vérifier
            assert abs(score - expected) < 2, f"Score {score} != {expected}"
        
        print_success("Score profit OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_score_liquidity():
    """Test scoring de la liquidité"""
    print_header("Test 2 : Score Liquidité (0-30 points)")
    
    try:
        scorer = OpportunityScorer()
        
        test_cases = [
            # (filled_pct, slippage_pct, volume_ratio, score_attendu_approx)
            (100, 0.0, 10.0, 30),    # Parfait
            (100, 0.25, 5.0, 22),    # Bon
            (100, 0.5, 1.0, 15),     # Moyen
            (50, 0.5, 1.0, 7.5),     # Faible
        ]
        
        print(f"\n{'Rempli':<10} {'Slippage':<12} {'Vol Ratio':<12} {'Score':<10}")
        print("-" * 50)
        
        for filled, slip, vol_ratio, _ in test_cases:
            score = scorer.score_liquidity(filled, slip, vol_ratio)
            print(f"{filled:<9.0f}% {slip:<11.2f}% {vol_ratio:<11.1f}x {score:<10.1f}")
        
        print_success("Score liquidité OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_score_reliability():
    """Test scoring de la fiabilité"""
    print_header("Test 3 : Score Fiabilité (0-20 points)")
    
    try:
        scorer = OpportunityScorer()
        
        test_cases = [
            ('binance', 'kraken', 18.5),
            ('binance', 'coinbase', 18.0),
            ('gate', 'kucoin', 14.5),
        ]
        
        print(f"\n{'Exchange Buy':<15} {'Exchange Sell':<15} {'Score':<10}")
        print("-" * 45)
        
        for buy, sell, expected in test_cases:
            score = scorer.score_reliability(buy, sell)
            print(f"{buy:<15} {sell:<15} {score:<10.1f}")
            
            assert abs(score - expected) < 2, f"Score {score} != {expected}"
        
        print_success("Score fiabilité OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_score_speed():
    """Test scoring de la vitesse"""
    print_header("Test 4 : Score Vitesse (0-10 points)")
    
    try:
        scorer = OpportunityScorer()
        
        test_cases = [
            ('binance', 'okx', 10),     # Très rapide
            ('kraken', 'coinbase', 6),  # Moyen
            ('huobi', 'kucoin', 0),     # Lent
        ]
        
        print(f"\n{'Exchange Buy':<15} {'Exchange Sell':<15} {'Score':<10}")
        print("-" * 45)
        
        for buy, sell, _ in test_cases:
            score = scorer.score_speed(buy, sell)
            print(f"{buy:<15} {sell:<15} {score:<10.1f}")
        
        print_success("Score vitesse OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_score_complete():
    """Test scoring complet"""
    print_header("Test 5 : Score Complet (0-100 points)")
    
    try:
        scorer = OpportunityScorer()
        
        # Opportunité excellente
        excellent = {
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'net_profit_pct': 1.5,
            'total_slippage_pct': 0.1,
            'liquidity_valid': True,
        }
        
        result = scorer.score_opportunity(excellent)
        
        print(f"\n📊 Opportunité: {result['exchange_buy']} → {result['exchange_sell']}")
        print(f"   Profit NET: {result['net_profit_pct']:.2f}%")
        print(f"\n   Scores détaillés:")
        print(f"     Profit:      {result['profit_score']:.1f}/40")
        print(f"     Liquidité:   {result['liquidity_score']:.1f}/30")
        print(f"     Fiabilité:   {result['reliability_score']:.1f}/20")
        print(f"     Vitesse:     {result['speed_score']:.1f}/10")
        print(f"\n   Score total: {result['total_score']:.1f}/100")
        print(f"   Grade: {result['grade']}")
        
        # Vérifications
        assert 'total_score' in result
        assert 'grade' in result
        assert result['total_score'] > 70, "Devrait être bon score"
        
        print_success("Score complet OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ranking():
    """Test classement multiple"""
    print_header("Test 6 : Classement Multiple")
    
    try:
        scorer = OpportunityScorer()
        
        opportunities = [
            {
                'exchange_buy': 'binance',
                'exchange_sell': 'kraken',
                'net_profit_pct': 0.8,
                'total_slippage_pct': 0.2,
                'liquidity_valid': True,
            },
            {
                'exchange_buy': 'kraken',
                'exchange_sell': 'coinbase',
                'net_profit_pct': 1.5,
                'total_slippage_pct': 0.1,
                'liquidity_valid': True,
            },
            {
                'exchange_buy': 'bitstamp',
                'exchange_sell': 'huobi',
                'net_profit_pct': 2.0,
                'total_slippage_pct': 0.8,
                'liquidity_valid': False,
            },
            {
                'exchange_buy': 'binance',
                'exchange_sell': 'okx',
                'net_profit_pct': 1.0,
                'total_slippage_pct': 0.1,
                'liquidity_valid': True,
            }
        ]
        
        ranked = scorer.rank_opportunities(opportunities)
        
        print(f"\n{'#':<3} {'Route':<25} {'Profit':<10} {'Score':<10} {'Grade':<7}")
        print("-" * 60)
        
        for i, opp in enumerate(ranked, 1):
            route = f"{opp['exchange_buy']}→{opp['exchange_sell']}"
            print(f"{i:<3} {route:<25} {opp['net_profit_pct']:>5.2f}%{'':<3} "
                  f"{opp['total_score']:>7.1f}{'':<3} {opp['grade']:<7}")
        
        # Vérifications
        assert len(ranked) == 4
        assert ranked[0]['total_score'] >= ranked[1]['total_score']
        assert ranked[1]['total_score'] >= ranked[2]['total_score']
        
        print_success("Classement OK")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filtering():
    """Test filtrage par score"""
    print_header("Test 7 : Filtrage par Score")
    
    try:
        scorer = OpportunityScorer()
        
        opportunities = [
            {
                'exchange_buy': 'binance',
                'exchange_sell': 'kraken',
                'net_profit_pct': 1.5,
                'total_slippage_pct': 0.1,
                'liquidity_valid': True,
            },
            {
                'exchange_buy': 'bitstamp',
                'exchange_sell': 'huobi',
                'net_profit_pct': 0.3,
                'total_slippage_pct': 0.8,
                'liquidity_valid': False,
            },
            {
                'exchange_buy': 'binance',
                'exchange_sell': 'okx',
                'net_profit_pct': 1.0,
                'total_slippage_pct': 0.2,
                'liquidity_valid': True,
            }
        ]
        
        # Scorer d'abord
        ranked = scorer.rank_opportunities(opportunities)
        
        # Filtrer score >= 70
        filtered = scorer.filter_by_score(ranked, min_score=70)
        
        print(f"\nOpportunités totales: {len(ranked)}")
        print(f"Opportunités >= 70 points: {len(filtered)}")
        
        print(f"\n✅ Opportunités retenues:")
        for opp in filtered:
            print(f"  - {opp['exchange_buy']}→{opp['exchange_sell']}: "
                  f"{opp['total_score']:.1f}/100")
        
        assert all(opp['total_score'] >= 70 for opp in filtered)
        
        print_success(f"{len(filtered)} opportunités filtrées")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_top_n():
    """Test récupération top N"""
    print_header("Test 8 : Top N Opportunités")
    
    try:
        scorer = OpportunityScorer()
        
        opportunities = [
            {'exchange_buy': 'binance', 'exchange_sell': 'kraken',
             'net_profit_pct': 1.5, 'total_slippage_pct': 0.1, 'liquidity_valid': True},
            {'exchange_buy': 'kraken', 'exchange_sell': 'coinbase',
             'net_profit_pct': 0.8, 'total_slippage_pct': 0.2, 'liquidity_valid': True},
            {'exchange_buy': 'bitfinex', 'exchange_sell': 'bitstamp',
             'net_profit_pct': 0.5, 'total_slippage_pct': 0.3, 'liquidity_valid': True},
            {'exchange_buy': 'binance', 'exchange_sell': 'okx',
             'net_profit_pct': 1.2, 'total_slippage_pct': 0.15, 'liquidity_valid': True},
        ]
        
        # Classer
        ranked = scorer.rank_opportunities(opportunities)
        
        # Top 2
        top = scorer.get_top_opportunities(ranked, top_n=2)
        
        print(f"\n🏆 Top 2 opportunités:")
        for i, opp in enumerate(top, 1):
            print(f"\n{i}. {opp['exchange_buy']} → {opp['exchange_sell']}")
            print(f"   Profit: {opp['net_profit_pct']:.2f}%")
            print(f"   Score: {opp['total_score']:.1f}/100 (Grade {opp['grade']})")
        
        assert len(top) == 2
        assert top[0]['total_score'] >= top[1]['total_score']
        
        print_success("Top 2 récupéré")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("       🎯 TEST SYSTÈME DE SCORING - ÉTAPE 3.5")
    print("=" * 60)
    
    tests = [
        ("Score profit", test_score_profit),
        ("Score liquidité", test_score_liquidity),
        ("Score fiabilité", test_score_reliability),
        ("Score vitesse", test_score_speed),
        ("Score complet", test_score_complete),
        ("Classement", test_ranking),
        ("Filtrage", test_filtering),
        ("Top N", test_top_n),
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
        print("\n💡 Le système de scoring fonctionne!")
        print("\n📊 Critères de scoring:")
        print("  - Profit NET (40 points)")
        print("  - Liquidité (30 points)")
        print("  - Fiabilité exchanges (20 points)")
        print("  - Vitesse exécution (10 points)")
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: 3.6 - Sauvegarde opportunités")
    print("=" * 60)


if __name__ == "__main__":
    main()
