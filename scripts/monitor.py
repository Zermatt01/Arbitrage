from src.collectors.price_collector import PriceCollector
import time

print("🚀 MONITORING D'ARBITRAGE 24/7")
print("Appuyez sur Ctrl+C pour arrêter\n")

collector = PriceCollector(['binance', 'kraken'])

try:
    while True:
        result = collector.collect_and_analyze('BTC/USDT', save_to_db=True)
        
        # Afficher les prix
        print(f"\n⏰ {time.strftime('%H:%M:%S')}")
        for exchange, data in result['prices'].items():
            print(f"  {exchange:8}: ${data['last']:>10,.2f}")
        
        # Alerter si opportunité
        if result['opportunities']:
            print("\n🚨 OPPORTUNITÉ DÉTECTÉE!")
            for opp in result['opportunities']:
                print(f"💰 {opp['spread_pct']:+.2f}% - "
                      f"Acheter {opp['exchange_buy']}, "
                      f"Vendre {opp['exchange_sell']}")
        else:
            spread = result['spreads'][0]['spread_pct'] if result['spreads'] else 0
            print(f"  Spread: {spread:+.2f}%")
        
        time.sleep(5)  # Attendre 5 secondes
        
except KeyboardInterrupt:
    print("\n\n✅ Arrêt du monitoring")
    collector.disconnect_all()