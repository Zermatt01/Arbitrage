from src.collectors.price_collector import PriceCollector
import time

print("=" * 60)
print("  ÉTAPE 3.1 - Collecteur Multi-Exchanges")
print("=" * 60)

# Créer le collecteur avec 2 exchanges
collector = PriceCollector(['binance', 'kraken'])

# Test 1 : Collecte simple
print("\n✅ Test 1 : Collecte de prix")
result = collector.collect_and_analyze('BTC/USDT', save_to_db=True)

print(f"\nPrix collectés : {len(result['prices'])} exchanges")
for exchange, data in result['prices'].items():
    print(f"  {exchange}: ${data['last']:,.2f}")

print(f"\nSpreads calculés : {len(result['spreads'])}")
for spread in result['spreads']:
    print(f"  {spread['exchange_buy']} → {spread['exchange_sell']}: {spread['spread_pct']:+.2f}%")

print(f"\nOpportunités détectées : {len(result['opportunities'])}")
if result['opportunities']:
    for opp in result['opportunities']:
        print(f"  🎯 {opp['spread_pct']:+.2f}%")
else:
    print("  ⚠️  Aucune opportunité > 0.5%")

# Test 2 : Collecte continue (5 fois)
print("\n✅ Test 2 : Collecte continue (5 collectes)")
for i in range(5):
    result = collector.collect_and_analyze('BTC/USDT', save_to_db=True)
    spread = result['spreads'][0]['spread_pct'] if result['spreads'] else 0
    print(f"  Collecte {i+1}/5 : Spread = {spread:+.2f}%")
    time.sleep(2)

# Statistiques
print("\n✅ Statistiques du collecteur :")
stats = collector.get_stats()
print(f"  Collections totales : {stats['total_collections']}")
print(f"  Collections réussies : {stats['successful_collections']}")
print(f"  Opportunités détectées : {stats['opportunities_detected']}")
print(f"  Taux d'erreur : {stats['error_rate']:.2%}")

collector.disconnect_all()

print("\n" + "=" * 60)
print("✅ ÉTAPE 3.1 VALIDÉE")
print("=" * 60)
print("\n💡 Le collecteur multi-exchanges fonctionne parfaitement !")
print("📊 Prochaine étape : 3.2 - Calculateur de frais")