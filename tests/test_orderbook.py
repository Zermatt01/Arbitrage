"""
Tests pour l'Étape 2.6 - Récupération des Orderbooks
====================================================

Teste la récupération et l'analyse des carnets d'ordres.
"""

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


def print_info(text):
    """Affiche une info"""
    print(f"ℹ️  {text}")


def format_price(price):
    """Formate un prix"""
    return f"${price:,.2f}" if price else "N/A"


def format_volume(volume):
    """Formate un volume"""
    return f"{volume:.4f}" if volume else "N/A"


def test_orderbook_binance():
    """Test récupération orderbook Binance"""
    print_header("Test Orderbook Binance")
    
    try:
        # Créer le connecteur
        binance = ExchangeFactory.create('binance')
        binance.connect()
        
        # Récupérer l'orderbook
        print_info("Récupération orderbook BTC/USDT (10 niveaux)...")
        orderbook = binance.get_orderbook('BTC/USDT', limit=10)
        
        # Afficher les résultats
        print(f"\n📊 Orderbook {orderbook['symbol']} sur {orderbook['exchange']}")
        print(f"   Latence: {orderbook['latency_ms']:.2f}ms")
        print(f"   Timestamp: {orderbook['timestamp']}")
        
        # Statistiques
        stats = orderbook['stats']
        print(f"\n📈 Statistiques:")
        print(f"   Best bid: {format_price(stats['best_bid'])}")
        print(f"   Best ask: {format_price(stats['best_ask'])}")
        print(f"   Spread: {format_price(stats['spread'])} ({stats['spread_pct']:.4f}%)")
        print(f"   Volume total bids: {format_volume(stats['total_bid_volume'])} BTC")
        print(f"   Volume total asks: {format_volume(stats['total_ask_volume'])} BTC")
        
        # Afficher les 5 meilleurs niveaux
        print(f"\n💰 Top 5 Bids (ordres d'achat):")
        print(f"   {'Prix':<15} {'Volume (BTC)':<15} {'Total (USD)':<15}")
        print(f"   {'-'*15} {'-'*15} {'-'*15}")
        for i, (price, volume) in enumerate(orderbook['bids'][:5]):
            total_usd = price * volume
            print(f"   {format_price(price):<15} {format_volume(volume):<15} {format_price(total_usd):<15}")
        
        print(f"\n💵 Top 5 Asks (ordres de vente):")
        print(f"   {'Prix':<15} {'Volume (BTC)':<15} {'Total (USD)':<15}")
        print(f"   {'-'*15} {'-'*15} {'-'*15}")
        for i, (price, volume) in enumerate(orderbook['asks'][:5]):
            total_usd = price * volume
            print(f"   {format_price(price):<15} {format_volume(volume):<15} {format_price(total_usd):<15}")
        
        binance.disconnect()
        print_success("Test Binance réussi")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orderbook_kraken():
    """Test récupération orderbook Kraken"""
    print_header("Test Orderbook Kraken")
    
    try:
        # Créer le connecteur
        kraken = ExchangeFactory.create('kraken')
        kraken.connect()
        
        # Récupérer l'orderbook
        print_info("Récupération orderbook BTC/USDT (10 niveaux)...")
        orderbook = kraken.get_orderbook('BTC/USDT', limit=10)
        
        # Afficher les résultats
        print(f"\n📊 Orderbook {orderbook['symbol']} sur {orderbook['exchange']}")
        print(f"   Latence: {orderbook['latency_ms']:.2f}ms")
        
        # Statistiques
        stats = orderbook['stats']
        print(f"\n📈 Statistiques:")
        print(f"   Best bid: {format_price(stats['best_bid'])}")
        print(f"   Best ask: {format_price(stats['best_ask'])}")
        print(f"   Spread: {format_price(stats['spread'])} ({stats['spread_pct']:.4f}%)")
        
        kraken.disconnect()
        print_success("Test Kraken réussi")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_liquidity_analysis():
    """Test analyse de liquidité"""
    print_header("Test Analyse de Liquidité")
    
    try:
        # Connecter Binance
        binance = ExchangeFactory.create('binance')
        binance.connect()
        
        # Récupérer l'orderbook
        orderbook = binance.get_orderbook('BTC/USDT', limit=50)
        
        # Analyser liquidité pour différents montants
        amounts_usd = [1000, 5000, 10000, 50000, 100000]
        
        print(f"\n📊 Analyse de liquidité pour BTC/USDT")
        print(f"\n💰 Achat (asks):")
        print(f"   {'Montant USD':<15} {'BTC disponible':<20} {'Prix moyen':<15} {'Slippage':<10}")
        print(f"   {'-'*15} {'-'*20} {'-'*15} {'-'*10}")
        
        best_ask = orderbook['stats']['best_ask']
        
        for amount_usd in amounts_usd:
            # Calculer combien de BTC on peut acheter avec ce montant
            btc_available = 0
            total_cost = 0
            
            for price, volume in orderbook['asks']:
                cost_at_level = price * volume
                
                if total_cost + cost_at_level <= amount_usd:
                    # On peut prendre tout ce niveau
                    btc_available += volume
                    total_cost += cost_at_level
                else:
                    # On ne peut prendre qu'une partie
                    remaining = amount_usd - total_cost
                    btc_available += remaining / price
                    total_cost = amount_usd
                    break
            
            if total_cost > 0:
                avg_price = total_cost / btc_available
                slippage_pct = ((avg_price - best_ask) / best_ask) * 100
                
                print(f"   {format_price(amount_usd):<15} {format_volume(btc_available):<20} "
                      f"{format_price(avg_price):<15} {slippage_pct:>6.2f}%")
        
        print(f"\n💵 Vente (bids):")
        print(f"   {'BTC à vendre':<15} {'USD reçus':<20} {'Prix moyen':<15} {'Slippage':<10}")
        print(f"   {'-'*15} {'-'*20} {'-'*15} {'-'*10}")
        
        best_bid = orderbook['stats']['best_bid']
        amounts_btc = [0.1, 0.5, 1.0, 5.0, 10.0]
        
        for amount_btc in amounts_btc:
            # Calculer combien d'USD on reçoit en vendant ce montant de BTC
            usd_received = 0
            btc_sold = 0
            
            for price, volume in orderbook['bids']:
                if btc_sold + volume <= amount_btc:
                    # On peut vendre tout à ce niveau
                    usd_received += price * volume
                    btc_sold += volume
                else:
                    # On vend partiellement à ce niveau
                    remaining = amount_btc - btc_sold
                    usd_received += price * remaining
                    btc_sold = amount_btc
                    break
            
            if btc_sold > 0:
                avg_price = usd_received / btc_sold
                slippage_pct = ((best_bid - avg_price) / best_bid) * 100
                
                print(f"   {format_volume(amount_btc):<15} {format_price(usd_received):<20} "
                      f"{format_price(avg_price):<15} {slippage_pct:>6.2f}%")
        
        binance.disconnect()
        print_success("Test analyse de liquidité réussi")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_compare_orderbooks():
    """Test comparaison orderbooks entre exchanges"""
    print_header("Test Comparaison Orderbooks Multi-Exchanges")
    
    try:
        # Créer les connecteurs
        binance = ExchangeFactory.create('binance')
        kraken = ExchangeFactory.create('kraken')
        
        binance.connect()
        kraken.connect()
        
        # Récupérer les orderbooks
        print_info("Récupération des orderbooks...")
        ob_binance = binance.get_orderbook('BTC/USDT', limit=10)
        ob_kraken = kraken.get_orderbook('BTC/USDT', limit=10)
        
        # Comparer
        print(f"\n📊 Comparaison Binance vs Kraken")
        print(f"\n{'Métrique':<30} {'Binance':<20} {'Kraken':<20} {'Différence':<15}")
        print(f"{'-'*30} {'-'*20} {'-'*20} {'-'*15}")
        
        # Best bid
        bid_binance = ob_binance['stats']['best_bid']
        bid_kraken = ob_kraken['stats']['best_bid']
        bid_diff = bid_kraken - bid_binance
        print(f"{'Best Bid':<30} {format_price(bid_binance):<20} {format_price(bid_kraken):<20} "
              f"{format_price(bid_diff):<15}")
        
        # Best ask
        ask_binance = ob_binance['stats']['best_ask']
        ask_kraken = ob_kraken['stats']['best_ask']
        ask_diff = ask_kraken - ask_binance
        print(f"{'Best Ask':<30} {format_price(ask_binance):<20} {format_price(ask_kraken):<20} "
              f"{format_price(ask_diff):<15}")
        
        # Spread
        spread_binance = ob_binance['stats']['spread_pct']
        spread_kraken = ob_kraken['stats']['spread_pct']
        spread_diff = spread_kraken - spread_binance
        print(f"{'Spread %':<30} {spread_binance:>6.4f}%{'':<13} {spread_kraken:>6.4f}%{'':<13} "
              f"{spread_diff:>+6.4f}%{'':<7}")
        
        # Volume
        vol_binance = ob_binance['stats']['total_bid_volume']
        vol_kraken = ob_kraken['stats']['total_bid_volume']
        print(f"{'Volume Bids (BTC)':<30} {format_volume(vol_binance):<20} {format_volume(vol_kraken):<20}")
        
        # Opportunité d'arbitrage ?
        print(f"\n🎯 Analyse d'arbitrage:")
        
        # Acheter sur Binance, vendre sur Kraken
        profit_1 = bid_kraken - ask_binance
        profit_1_pct = (profit_1 / ask_binance) * 100
        print(f"   Acheter Binance ({format_price(ask_binance)}), "
              f"Vendre Kraken ({format_price(bid_kraken)})")
        print(f"   → Spread: {format_price(profit_1)} ({profit_1_pct:+.2f}%)")
        
        # Acheter sur Kraken, vendre sur Binance
        profit_2 = bid_binance - ask_kraken
        profit_2_pct = (profit_2 / ask_kraken) * 100
        print(f"   Acheter Kraken ({format_price(ask_kraken)}), "
              f"Vendre Binance ({format_price(bid_binance)})")
        print(f"   → Spread: {format_price(profit_2)} ({profit_2_pct:+.2f}%)")
        
        # Conclusion
        if profit_1_pct > 0.5:
            print(f"   💰 Opportunité détectée: Binance→Kraken {profit_1_pct:+.2f}%")
        elif profit_2_pct > 0.5:
            print(f"   💰 Opportunité détectée: Kraken→Binance {profit_2_pct:+.2f}%")
        else:
            print(f"   ⚠️  Pas d'opportunité (spreads < 0.5%)")
        
        binance.disconnect()
        kraken.disconnect()
        
        print_success("Test comparaison réussi")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("             💰 TEST ORDERBOOKS - ÉTAPE 2.6")
    print("=" * 60)
    
    tests = [
        ("Orderbook Binance", test_orderbook_binance),
        ("Orderbook Kraken", test_orderbook_kraken),
        ("Analyse Liquidité", test_liquidity_analysis),
        ("Comparaison Orderbooks", test_compare_orderbooks),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            time.sleep(1)  # Pause entre les tests
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
    
    print("\n" + "=" * 60)
    print("💡 Prochaine étape: Phase 3 - Détection d'opportunités")
    print("=" * 60)


if __name__ == "__main__":
    main()
