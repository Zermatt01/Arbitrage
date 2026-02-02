from src.collectors.price_collector import PriceCollector

print("=" * 60)
print("🚀 TEST DU BOT D'ARBITRAGE EN TEMPS RÉEL")
print("=" * 60)

# Créer le collecteur
print("\n📡 Connexion à Binance et Kraken...")
collector = PriceCollector(['binance', 'kraken'])

# Collecter les prix BTC
print("\n💰 Collecte des prix BTC/USDT...")
result = collector.collect_and_analyze('BTC/USDT', save_to_db=True)

# Afficher les prix
print("\n" + "=" * 60)
print("📊 PRIX ACTUELS")
print("=" * 60)
for exchange, price_data in result['prices'].items():
    print(f"{exchange:10} | ${price_data['last']:>12,.2f}")

# Afficher les spreads
print("\n" + "=" * 60)
print("📈 SPREADS CALCULÉS")
print("=" * 60)
for spread in result['spreads']:
    emoji = "🎯" if abs(spread['spread_pct']) > 0.5 else "  "
    print(f"{emoji} {spread['exchange_buy']:8} → {spread['exchange_sell']:8} | "
          f"${spread['spread_abs']:>8,.2f} ({spread['spread_pct']:>+6.2f}%)")

# Opportunités
print("\n" + "=" * 60)
if result['opportunities']:
    print(f"🚨 {len(result['opportunities'])} OPPORTUNITÉ(S) D'ARBITRAGE DÉTECTÉE(S)!")
    print("=" * 60)
    for opp in result['opportunities']:
        profit_per_btc = opp['spread_abs']
        print(f"\n💰 OPPORTUNITÉ:")
        print(f"   Acheter sur : {opp['exchange_buy']}")
        print(f"   Vendre sur  : {opp['exchange_sell']}")
        print(f"   Spread      : {opp['spread_pct']:+.2f}%")
        print(f"   Profit/BTC  : ${profit_per_btc:,.2f}")
        print(f"   📈 Avec 1 BTC, profit potentiel : ${profit_per_btc:,.2f}")
else:
    print("⚠️  AUCUNE OPPORTUNITÉ > 0.5%")
    print("=" * 60)
    print("💡 C'est normal ! Les vraies opportunités sont rares.")

# Statistiques
print("\n" + "=" * 60)
print("📊 STATISTIQUES DU COLLECTEUR")
print("=" * 60)
stats = collector.get_stats()
print(f"Collections totales    : {stats['total_collections']}")
print(f"Collections réussies   : {stats['successful_collections']}")
print(f"Opportunités détectées : {stats['opportunities_detected']}")

# Déconnexion
collector.disconnect_all()

print("\n✅ TEST TERMINÉ")
print("\n💡 Votre bot fonctionne !")