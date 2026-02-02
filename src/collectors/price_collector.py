"""
Price Collector
==============

Collecteur automatique de prix multi-exchanges.
Récupère les prix de plusieurs exchanges et détecte les opportunités d'arbitrage.

Usage:
    from src.collectors.price_collector import PriceCollector
    
    collector = PriceCollector(['binance', 'kraken'])
    prices = collector.collect_prices('BTC/USDT')
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.connectors.exchange_factory import ExchangeFactory
from src.utils.logger import get_logger
from src.utils.fee_calculator import FeeCalculator

# CORRECTION : Imports base de données
try:
    from src.models.database_models import PriceHistory, Session, engine
except ImportError:
    # Si la DB n'est pas disponible, on continue sans
    PriceHistory = None
    Session = None
    engine = None


class PriceCollector:
    """
    Collecteur de prix multi-exchanges
    
    Récupère les prix de plusieurs exchanges en parallèle
    et calcule les spreads automatiquement.
    """
    
    def __init__(
        self,
        exchange_names: List[str],
        auto_connect: bool = True
    ):
        """
        Initialise le collecteur
        
        Args:
            exchange_names: Liste des exchanges à surveiller
            auto_connect: Se connecter automatiquement ?
        """
        self.logger = get_logger(__name__)
        self.exchange_names = exchange_names
        # Calculateur de frais
        self.fee_calculator = FeeCalculator()
        
        # Créer les connecteurs
        self.logger.info(f"Création des connecteurs pour {len(exchange_names)} exchanges")
        self.exchanges = ExchangeFactory.create_all(exchange_names)
        
        # État
        self.is_running = False
        self.collection_count = 0
        self.error_count = 0
        
        # Statistiques
        self.stats = {
            'total_collections': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'opportunities_detected': 0
        }
        
        # Connexion automatique
        if auto_connect:
            self.connect_all()
        
        self.logger.info(
            f"PriceCollector initialisé avec {len(self.exchanges)} exchanges",
            extra={'context': {'exchanges': list(self.exchanges.keys())}}
        )
    
    def connect_all(self) -> Dict[str, bool]:
        """
        Connecte tous les exchanges
        
        Returns:
            Dict {exchange_name: success}
        """
        self.logger.info("Connexion aux exchanges...")
        results = ExchangeFactory.connect_all(self.exchanges)
        
        success_count = sum(results.values())
        self.logger.info(
            f"{success_count}/{len(results)} exchanges connectés",
            extra={'context': {'results': results}}
        )
        
        return results
    
    def disconnect_all(self):
        """Déconnecte tous les exchanges"""
        self.logger.info("Déconnexion des exchanges...")
        ExchangeFactory.disconnect_all(self.exchanges)
        self.logger.info("Tous les exchanges déconnectés")
    
    def collect_price(
        self,
        exchange_name: str,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Collecte le prix d'une paire sur un exchange
        
        Args:
            exchange_name: Nom de l'exchange
            symbol: Paire (ex: BTC/USDT)
        
        Returns:
            Données de prix ou None si erreur
        """
        try:
            connector = self.exchanges[exchange_name]
            
            if not connector.is_connected():
                self.logger.warning(f"{exchange_name} non connecté, tentative de connexion...")
                connector.connect()
            
            # Récupérer le ticker
            ticker = connector.get_ticker(symbol)
            
            # Formater les données
            price_data = {
                'exchange': exchange_name,
                'symbol': symbol,
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'last': ticker.get('last'),
                'volume': ticker.get('volume'),
                'timestamp': datetime.utcnow()
            }
            
            self.logger.debug(
                f"Prix collecté: {exchange_name} {symbol} = ${price_data['last']:,.2f}",
                extra={'context': price_data}
            )
            
            return price_data
            
        except Exception as e:
            self.logger.error(
                f"Erreur lors de la collecte {exchange_name} {symbol}: {e}",
                extra={'context': {
                    'exchange': exchange_name,
                    'symbol': symbol,
                    'error': str(e)
                }}
            )
            self.error_count += 1
            return None
    
    def collect_prices(
        self,
        symbol: str,
        parallel: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Collecte les prix d'une paire sur tous les exchanges
        
        Args:
            symbol: Paire (ex: BTC/USDT)
            parallel: Utiliser le traitement parallèle ?
        
        Returns:
            Dict {exchange_name: price_data}
        """
        self.logger.info(f"Collecte des prix pour {symbol}...")
        
        prices = {}
        
        if parallel:
            # Collecte parallèle (plus rapide)
            with ThreadPoolExecutor(max_workers=len(self.exchanges)) as executor:
                # Soumettre toutes les tâches
                future_to_exchange = {
                    executor.submit(self.collect_price, name, symbol): name
                    for name in self.exchanges.keys()
                }
                
                # Récupérer les résultats
                for future in as_completed(future_to_exchange):
                    exchange_name = future_to_exchange[future]
                    try:
                        price_data = future.result()
                        if price_data:
                            prices[exchange_name] = price_data
                    except Exception as e:
                        self.logger.error(f"Erreur future {exchange_name}: {e}")
        else:
            # Collecte séquentielle
            for exchange_name in self.exchanges.keys():
                price_data = self.collect_price(exchange_name, symbol)
                if price_data:
                    prices[exchange_name] = price_data
        
        self.collection_count += 1
        self.stats['total_collections'] += 1
        
        if prices:
            self.stats['successful_collections'] += 1
            self.logger.info(
                f"Prix collectés: {len(prices)}/{len(self.exchanges)} exchanges",
                extra={'context': {
                    'symbol': symbol,
                    'exchanges': list(prices.keys())
                }}
            )
        else:
            self.stats['failed_collections'] += 1
            self.logger.warning(f"Aucun prix collecté pour {symbol}")
        
        return prices
    
    def calculate_spreads(
        self,
        prices: Dict[str, Dict[str, Any]],
        trade_amount_usd: float = 1000  # Montant par défaut pour calculer les frais
    ) -> List[Dict[str, Any]]:
        """
        Calcule les spreads entre tous les exchanges AVEC calcul des frais
        
        Args:
            prices: Dict des prix par exchange
            trade_amount_usd: Montant du trade pour calculer les frais en USD
        
        Returns:
            Liste des spreads détectés avec profit NET
        """
        if len(prices) < 2:
            return []
        
        spreads = []
        exchange_names = list(prices.keys())
        
        # Comparer chaque paire d'exchanges
        for i, exchange_buy in enumerate(exchange_names):
            for exchange_sell in exchange_names[i+1:]:
                price_buy = prices[exchange_buy]
                price_sell = prices[exchange_sell]
                
                # Utiliser le prix 'ask' pour acheter et 'bid' pour vendre
                buy_price = price_buy.get('ask') or price_buy.get('last')
                sell_price = price_sell.get('bid') or price_sell.get('last')
                
                if buy_price and sell_price:
                    # Calculer le spread BRUT
                    spread_abs = sell_price - buy_price
                    spread_pct = (spread_abs / buy_price) * 100
                    
                    # NOUVEAU : Calculer le profit NET avec les frais
                    try:
                        fee_result = self.fee_calculator.calculate_arbitrage_profit(
                            buy_exchange=exchange_buy,
                            sell_exchange=exchange_sell,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            trade_amount_usd=trade_amount_usd
                        )
                        
                        net_profit_pct = fee_result['net_profit_pct']
                        net_profit_usd = fee_result['net_profit_usd']
                        total_fees_pct = fee_result['total_fees_pct']
                        is_profitable = fee_result['is_profitable']
                        
                    except Exception as e:
                        # Fallback si erreur dans le calcul des frais
                        self.logger.warning(
                            f"Erreur calcul frais: {e}",
                            extra={'context': {'error': str(e)}}
                        )
                        net_profit_pct = spread_pct  # Utiliser le spread brut
                        net_profit_usd = 0
                        total_fees_pct = 0
                        is_profitable = spread_pct > 0
                    
                    spread_data = {
                        'exchange_buy': exchange_buy,
                        'exchange_sell': exchange_sell,
                        'symbol': price_buy['symbol'],
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        
                        # Spread brut
                        'spread_abs': spread_abs,
                        'spread_pct': spread_pct,
                        
                        # NOUVEAU : Profit net
                        'net_profit_pct': net_profit_pct,
                        'net_profit_usd': net_profit_usd,
                        'total_fees_pct': total_fees_pct,
                        'is_profitable': is_profitable,
                        
                        'timestamp': datetime.utcnow()
                    }
                    
                    spreads.append(spread_data)
                    
                    # Logger si opportunité intéressante (profit NET > 0.5%)
                    if net_profit_pct > 0.5:
                        self.logger.info(
                            f"💰 Opportunité détectée: {spread_data['symbol']} "
                            f"{exchange_buy}→{exchange_sell} "
                            f"Spread: {spread_pct:+.2f}% | "
                            f"NET: {net_profit_pct:+.2f}%",
                            extra={'context': spread_data}
                        )
                        self.stats['opportunities_detected'] += 1
        
        return spreads

    def save_to_database(
        self,
        prices: Dict[str, Dict[str, Any]]
    ):
        """
        Sauvegarde les prix en base de données
        
        Args:
            prices: Dict des prix par exchange
        """
        # Vérifier si la DB est disponible
        if PriceHistory is None or Session is None or engine is None:
            self.logger.warning("Base de données non disponible, sauvegarde ignorée")
            return
        
        try:
            with Session() as session:
                for exchange_name, price_data in prices.items():
                    # Créer l'enregistrement
                    price_record = PriceHistory(
                        exchange=exchange_name,
                        symbol=price_data['symbol'],
                        bid=price_data.get('bid'),
                        ask=price_data.get('ask'),
                        last=price_data.get('last'),
                        volume_24h=price_data.get('volume'),
                        collected_at=price_data['timestamp']
                    )
                    
                    session.add(price_record)
                
                session.commit()
                
                self.logger.info(
                    f"✅ {len(prices)} prix sauvegardés en DB",
                    extra={'context': {'count': len(prices)}}
                )
                
        except Exception as e:
            self.logger.error(
                f"Erreur sauvegarde DB: {e}",
                exc_info=True
            )
    
    def collect_and_analyze(
        self,
        symbol: str,
        save_to_db: bool = True,
        trade_amount_usd: float = 1000  # NOUVEAU paramètre
    ) -> Dict[str, Any]:
        """
        Collecte les prix et analyse les opportunités
        
        Args:
            symbol: Paire à analyser
            save_to_db: Sauvegarder en DB ?
            trade_amount_usd: Montant pour calculer les frais
        
        Returns:
            Dict avec prices, spreads, et opportunities
        """
        # Collecter les prix
        prices = self.collect_prices(symbol)
        
        if not prices:
            return {
                'prices': {},
                'spreads': [],
                'opportunities': []
            }
        
        # Calculer les spreads AVEC les frais
        spreads = self.calculate_spreads(prices, trade_amount_usd)
        
        # Identifier les opportunités (profit NET > 0.5%)
        opportunities = [
            s for s in spreads
            if s.get('net_profit_pct', 0) > 0.5  # Utiliser profit NET
        ]
        
        # Sauvegarder en DB si demandé
        if save_to_db:
            self.save_to_database(prices)
        
        return {
            'prices': prices,
            'spreads': spreads,
            'opportunities': opportunities
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du collecteur
        
        Returns:
            Dict des statistiques
        """
        uptime = self.collection_count * 5  # Estimation si collecte toutes les 5s
        
        return {
            **self.stats,
            'collection_count': self.collection_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(self.collection_count, 1),
            'uptime_seconds': uptime,
            'exchanges_count': len(self.exchanges),
            'exchanges': list(self.exchanges.keys())
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect_all()
    
    def __repr__(self):
        """Représentation textuelle"""
        return (
            f"<PriceCollector("
            f"exchanges={len(self.exchanges)}, "
            f"collections={self.collection_count}, "
            f"opportunities={self.stats['opportunities_detected']}"
            f")>"
        )


# Exemple d'utilisation
if __name__ == "__main__":
    print("Test Price Collector")
    print("=" * 50)
    
    # Créer le collecteur
    collector = PriceCollector(['binance', 'kraken'])
    
    try:
        # Collecter les prix BTC
        print("\n1. Collecte des prix BTC...")
        result = collector.collect_and_analyze('BTC/USDT', save_to_db=False)
        
        print(f"\n✅ Prix collectés de {len(result['prices'])} exchanges:")
        for exchange, price_data in result['prices'].items():
            print(f"  {exchange}: ${price_data['last']:,.2f}")
        
        # Afficher les spreads
        print(f"\n✅ {len(result['spreads'])} spreads calculés:")
        for spread in result['spreads']:
            print(f"  {spread['exchange_buy']} → {spread['exchange_sell']}: "
                  f"{spread['spread_pct']:+.2f}%")
        
        # Afficher les opportunités
        if result['opportunities']:
            print(f"\n🎯 {len(result['opportunities'])} opportunités détectées:")
            for opp in result['opportunities']:
                print(f"  💰 {opp['symbol']} {opp['exchange_buy']}→{opp['exchange_sell']}: "
                      f"{opp['spread_pct']:+.2f}%")
        else:
            print("\n⚠️  Aucune opportunité > 0.5%")
        
        # Statistiques
        print("\n✅ Statistiques:")
        stats = collector.get_stats()
        for key, value in stats.items():
            if key not in ['exchanges']:
                print(f"  {key}: {value}")
        
    finally:
        collector.disconnect_all()
    
    print("\n🎉 Test terminé!")
