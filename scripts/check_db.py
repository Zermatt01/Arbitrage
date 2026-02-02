from src.models.database_models import PriceHistory, Session

print('✅ Base de données connectée\n')

with Session() as session:
    count = session.query(PriceHistory).count()
    print(f'📊 {count} prix dans la base de données\n')
    
    # 10 derniers prix
    latest = session.query(PriceHistory).order_by(
        PriceHistory.collected_at.desc()
    ).limit(10).all()
    
    print('🕐 10 derniers prix collectés:')
    print('=' * 100)
    print('{:<10} {:<12} {:<12} {:<12} {:<12} {}'.format(
        'Exchange', 'Symbol', 'Bid', 'Ask', 'Last', 'Date/Heure'
    ))
    print('=' * 100)
    
    for price in latest:
        bid = f'\`${price.bid:,.2f}' if price.bid else 'N/A'
        ask = f'\`${price.ask:,.2f}' if price.ask else 'N/A'
        last = f'\`${price.last:,.2f}' if price.last else 'N/A'
        date = price.collected_at.strftime('%H:%M:%S') if price.collected_at else 'N/A'
        
        print(f'{price.exchange:<10} {price.symbol:<12} {bid:<12} {ask:<12} {last:<12} {date}')
    
    print('=' * 100)
    
    # CORRECTION: Calcul du spread avec BID/ASK
    print('\n📊 CALCUL DU SPREAD CORRECT (avec bid/ask):')
    
    binance_last = session.query(PriceHistory).filter(
        PriceHistory.exchange == 'binance'
    ).order_by(PriceHistory.collected_at.desc()).first()
    
    kraken_last = session.query(PriceHistory).filter(
        PriceHistory.exchange == 'kraken'
    ).order_by(PriceHistory.collected_at.desc()).first()
    
    if binance_last and kraken_last:
        print(f'\n  Binance:')
        print(f'    bid: \`${binance_last.bid:,.2f}' if binance_last.bid else '    bid: N/A')
        print(f'    ask: \`${binance_last.ask:,.2f}' if binance_last.ask else '    ask: N/A')
        print(f'    last: \`${binance_last.last:,.2f}' if binance_last.last else '    last: N/A')
        
        print(f'\n  Kraken:')
        print(f'    bid: \`${kraken_last.bid:,.2f}' if kraken_last.bid else '    bid: N/A')
        print(f'    ask: \`${kraken_last.ask:,.2f}' if kraken_last.ask else '    ask: N/A')
        print(f'    last: \`${kraken_last.last:,.2f}' if kraken_last.last else '    last: N/A')
        
        # Calcul spread CORRECT
        if binance_last.ask and kraken_last.bid:
            # Pour arbitrage: acheter sur Binance (ask), vendre sur Kraken (bid)
            buy_price = binance_last.ask
            sell_price = kraken_last.bid
            spread = sell_price - buy_price
            spread_pct = (spread / buy_price) * 100
            
            print(f'\n  💰 SPREAD RÉEL (bid/ask):')
            print(f'    Acheter sur Binance (ask): \`${buy_price:,.2f}')
            print(f'    Vendre sur Kraken (bid):   \`${sell_price:,.2f}')
            print(f'    Spread: \`${spread:,.2f} ({spread_pct:+.2f}%)')
            
            if spread_pct > 0.5:
                print(f'    🎯 OPPORTUNITÉ!')
            else:
                print(f'    ⚠️  Pas rentable (< 0.5%)')
        
        # Comparaison avec le mauvais calcul
        if binance_last.last and kraken_last.last:
            spread_wrong = kraken_last.last - binance_last.last
            spread_pct_wrong = (spread_wrong / binance_last.last) * 100
            
            print(f'\n  ⚠️  SPREAD FAUX (avec last):')
            print(f'    Binance last: \`${binance_last.last:,.2f}')
            print(f'    Kraken last:  \`${kraken_last.last:,.2f}')
            print(f'    Spread: \`${spread_wrong:,.2f} ({spread_pct_wrong:+.2f}%)')
            print(f'    ❌ Ce calcul est FAUX car le last de Kraken ne se met pas à jour!')

print('\n✅ Analyse terminée')