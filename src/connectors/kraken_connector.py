"""
Connecteur Kraken
================

Connecteur spécifique pour l'exchange Kraken.
Gère les spécificités de Kraken (frais, paires fiat).

Usage:
    from src.connectors.kraken_connector import KrakenConnector
    
    # Mode public (sans credentials)
    connector = KrakenConnector()
    
    # Avec credentials
    connector = KrakenConnector(
        api_key='your_key',
        api_secret='your_secret'
    )
"""

from typing import Optional, Dict, Any, List
from src.connectors.base_connector import BaseConnector
from src.utils.logger import get_logger


class KrakenConnector(BaseConnector):
    """
    Connecteur pour Kraken
    
    Supporte :
    - Mode production (pas de testnet officiel)
    - Spot trading
    - Multiples devises fiat (EUR, USD, GBP, CAD, JPY)
    """
    
    # URLs officielles
    PRODUCTION_URL = 'https://api.kraken.com'
    
    # Frais par défaut (peuvent varier selon le volume)
    DEFAULT_MAKER_FEE = 0.0016  # 0.16%
    DEFAULT_TAKER_FEE = 0.0026  # 0.26%
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        enable_rate_limit: bool = True,
        timeout: int = 30000
    ):
        """
        Initialise le connecteur Kraken
        
        Args:
            api_key: Clé API Kraken
            api_secret: Secret API Kraken
            enable_rate_limit: Activer le rate limiting ?
            timeout: Timeout en millisecondes
        
        Note:
            Kraken n'a pas de testnet officiel
        """
        # Initialiser la classe parent
        super().__init__(
            exchange_name='kraken',
            api_key=api_key,
            api_secret=api_secret,
            testnet=False,  # Pas de testnet pour Kraken
            enable_rate_limit=enable_rate_limit,
            timeout=timeout
        )
        
        self.logger = get_logger(__name__)
        
        # Configuration spécifique Kraken
        self.maker_fee = self.DEFAULT_MAKER_FEE
        self.taker_fee = self.DEFAULT_TAKER_FEE
        
        self.logger.info(
            "Connecteur Kraken initialisé",
            extra={'context': {
                'url': self.PRODUCTION_URL,
                'has_credentials': bool(api_key and api_secret)
            }}
        )
    
    def get_trading_fees(self, symbol: Optional[str] = None) -> Dict[str, float]:
        """
        Récupère les frais de trading
        
        Args:
            symbol: Paire spécifique (optionnel)
        
        Returns:
            Dictionnaire des frais
        """
        try:
            # Si on a des credentials, on peut récupérer les vrais frais
            if self.api_key and self.api_secret:
                trading_fee = self._execute_request('fetch_trading_fee', symbol)
                
                if symbol:
                    return {
                        'maker': trading_fee.get('maker', self.DEFAULT_MAKER_FEE),
                        'taker': trading_fee.get('taker', self.DEFAULT_TAKER_FEE)
                    }
                else:
                    return trading_fee
            else:
                # Pas de credentials, retourner les frais par défaut
                return {
                    'maker': self.DEFAULT_MAKER_FEE,
                    'taker': self.DEFAULT_TAKER_FEE
                }
                
        except Exception as e:
            self.logger.warning(
                f"Impossible de récupérer les frais de trading: {e}",
                extra={'context': {'symbol': symbol}}
            )
            
            return {
                'maker': self.DEFAULT_MAKER_FEE,
                'taker': self.DEFAULT_TAKER_FEE
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Récupère les informations du compte
        
        Returns:
            Dictionnaire avec les infos du compte
        
        Raises:
            ExchangeError si pas de credentials
        """
        if not (self.api_key and self.api_secret):
            raise Exception("Credentials requis pour récupérer les infos du compte")
        
        balance = self._execute_request('fetch_balance')
        
        # Extraire les infos utiles
        info = {
            'balances': {},
            'timestamp': balance.get('timestamp')
        }
        
        # Ajouter les balances non nulles
        for currency, balance_data in balance.items():
            if currency != 'info' and isinstance(balance_data, dict):
                total = balance_data.get('total', 0)
                if total > 0:
                    info['balances'][currency] = {
                        'free': balance_data.get('free', 0),
                        'used': balance_data.get('used', 0),
                        'total': total
                    }
        
        self.logger.info(
            "Informations compte récupérées",
            extra={'context': {
                'currencies_count': len(info['balances'])
            }}
        )
        
        return info
    
    def get_24h_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère les statistiques 24h pour une paire
        
        Args:
            symbol: Paire (ex: BTC/USD)
        
        Returns:
            Statistiques 24h
        """
        ticker = self._execute_request('fetch_ticker', symbol)
        
        # Extraire les données 24h
        stats = {
            'symbol': ticker.get('symbol', symbol),
            'price_change': ticker.get('change'),
            'price_change_percent': ticker.get('percentage'),
            'high': ticker.get('high'),
            'low': ticker.get('low'),
            'volume': ticker.get('baseVolume'),
            'quote_volume': ticker.get('quoteVolume'),
            'open': ticker.get('open'),
            'close': ticker.get('close'),
            'last': ticker.get('last'),
            'bid': ticker.get('bid'),
            'ask': ticker.get('ask'),
            'vwap': ticker.get('vwap'),  # Volume-weighted average price
            'timestamp': ticker.get('timestamp')
        }
        
        return stats
    
    def get_klines(
        self,
        symbol: str,
        interval: str = '1m',
        limit: int = 100
    ) -> List[List]:
        """
        Récupère les bougies (klines/candlesticks)
        
        Args:
            symbol: Paire (ex: BTC/USD)
            interval: Intervalle (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Nombre de bougies
        
        Returns:
            Liste de bougies [timestamp, open, high, low, close, volume]
        """
        # Convertir l'intervalle au format Kraken si nécessaire
        # CCXT gère déjà cette conversion
        ohlcv = self._execute_request('fetch_ohlcv', symbol, interval, None, limit)
        
        self.logger.debug(
            f"Klines récupérées: {symbol}",
            extra={'context': {
                'interval': interval,
                'count': len(ohlcv)
            }}
        )
        
        return ohlcv
    
    def get_depth(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        Récupère la profondeur du marché (orderbook détaillé)
        
        Args:
            symbol: Paire (ex: BTC/USD)
            limit: Nombre de niveaux
        
        Returns:
            Orderbook détaillé
        """
        orderbook = self.get_orderbook(symbol, limit)
        
        # Calculer des stats supplémentaires
        if orderbook['bids'] and orderbook['asks']:
            # Volume total sur les X premiers niveaux
            bid_volume = sum(level[1] for level in orderbook['bids'][:10])
            ask_volume = sum(level[1] for level in orderbook['asks'][:10])
            
            orderbook['bid_volume_10'] = bid_volume
            orderbook['ask_volume_10'] = ask_volume
            
            if (bid_volume + ask_volume) > 0:
                orderbook['volume_imbalance'] = (bid_volume - ask_volume) / (bid_volume + ask_volume)
            else:
                orderbook['volume_imbalance'] = 0
        
        return orderbook
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur l'exchange
        
        Returns:
            Informations complètes sur Kraken
        """
        self._ensure_connected()
        
        # Utiliser les markets chargés
        info = {
            'name': 'Kraken',
            'url': self.PRODUCTION_URL,
            'markets_count': len(self.exchange.markets),
            'currencies': list(self.exchange.currencies.keys()),
            'has': {
                'spot': True,
                'margin': True,
                'futures': True,
                'swap': False,
                'option': False
            },
            'rate_limit': self.exchange.rateLimit,
            'precision': {
                'price': 8,
                'amount': 8
            },
            'fiat_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'JPY', 'CHF']
        }
        
        return info
    
    def get_symbols_by_quote(self, quote: str = 'USD') -> List[str]:
        """
        Récupère toutes les paires avec une devise de quote spécifique
        
        Args:
            quote: Devise de quote (USD, EUR, BTC, ETH, etc.)
        
        Returns:
            Liste des symboles
        """
        markets = self.get_markets()
        
        # Filtrer par devise de quote
        symbols = [
            market for market in markets
            if market.endswith(f'/{quote}')
        ]
        
        self.logger.debug(
            f"Symboles {quote} récupérés",
            extra={'context': {'count': len(symbols)}}
        )
        
        return symbols
    
    def get_fiat_pairs(self, fiat: str = 'EUR') -> List[str]:
        """
        Récupère toutes les paires crypto/fiat
        
        Args:
            fiat: Devise fiat (EUR, USD, GBP, etc.)
        
        Returns:
            Liste des paires crypto/fiat
        """
        return self.get_symbols_by_quote(fiat)
    
    def test_connectivity(self) -> bool:
        """
        Teste la connectivité à Kraken
        
        Returns:
            True si OK, False sinon
        """
        try:
            # Test simple : récupérer le temps serveur
            server_time = self._execute_request('fetch_time')
            
            self.logger.info(
                "Test de connectivité réussi",
                extra={'context': {'server_time': server_time}}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Test de connectivité échoué: {e}",
                exc_info=True
            )
            return False
    
    def get_server_time(self) -> int:
        """
        Récupère le temps serveur de Kraken
        
        Returns:
            Timestamp en millisecondes
        """
        return self._execute_request('fetch_time')
    
    def __repr__(self):
        """Représentation textuelle"""
        status = "connected" if self.is_connected() else "disconnected"
        return f"<KrakenConnector({status})>"


# Exemple d'utilisation
if __name__ == "__main__":
    # Mode public (sans credentials)
    print("Test Kraken Connector (mode public)")
    print("=" * 50)
    
    with KrakenConnector() as conn:
        # Test connectivité
        if conn.test_connectivity():
            print("✅ Connectivité OK")
        
        # Informations exchange
        info = conn.get_exchange_info()
        print(f"✅ {info['markets_count']} marchés disponibles")
        
        # Ticker BTC/USD
        ticker = conn.get_ticker('BTC/USD')
        print(f"✅ BTC/USD: ${ticker['last']:,.2f}")
        
        # Stats 24h
        stats = conn.get_24h_ticker('BTC/USD')
        print(f"✅ Variation 24h: {stats['price_change_percent']:.2f}%")
        
        # Orderbook
        depth = conn.get_depth('BTC/USD', limit=10)
        print(f"✅ Orderbook: {len(depth['bids'])} bids, {len(depth['asks'])} asks")
        
        # Symboles USD
        usd_pairs = conn.get_symbols_by_quote('USD')
        print(f"✅ {len(usd_pairs)} paires USD")
        
        # Paires EUR
        eur_pairs = conn.get_fiat_pairs('EUR')
        print(f"✅ {len(eur_pairs)} paires EUR")
        
        # Frais
        fees = conn.get_trading_fees()
        print(f"✅ Frais: {fees['maker']:.2%} maker, {fees['taker']:.2%} taker")
        
        print("\n🎉 Tous les tests réussis!")
