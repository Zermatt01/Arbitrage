"""
Connecteur Binance
=================

Connecteur spécifique pour l'exchange Binance.
Support du testnet pour tester sans risque.

Usage:
    from src.connectors.binance_connector import BinanceConnector
    
    # Mode testnet (recommandé pour développement)
    connector = BinanceConnector(
        api_key='your_testnet_key',
        api_secret='your_testnet_secret',
        testnet=True
    )
    
    # Mode production (argent réel)
    connector = BinanceConnector(
        api_key='your_real_key',
        api_secret='your_real_secret',
        testnet=False
    )
"""

from typing import Optional, Dict, Any, List
from src.connectors.base_connector import BaseConnector
from src.utils.logger import get_logger


class BinanceConnector(BaseConnector):
    """
    Connecteur pour Binance
    
    Supporte :
    - Mode testnet (testnet.binance.vision)
    - Mode production (api.binance.com)
    - Spot trading
    - Futures trading (optionnel)
    """
    
    # URLs officielles
    TESTNET_URL = 'https://testnet.binance.vision'
    PRODUCTION_URL = 'https://api.binance.com'
    
    # Frais par défaut (peuvent varier selon le niveau VIP)
    DEFAULT_MAKER_FEE = 0.001  # 0.1%
    DEFAULT_TAKER_FEE = 0.001  # 0.1%
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = True,
        enable_rate_limit: bool = True,
        timeout: int = 30000
    ):
        """
        Initialise le connecteur Binance
        
        Args:
            api_key: Clé API Binance
            api_secret: Secret API Binance
            testnet: Utiliser le testnet ? (True recommandé pour développement)
            enable_rate_limit: Activer le rate limiting ?
            timeout: Timeout en millisecondes
        """
        # Initialiser la classe parent
        super().__init__(
            exchange_name='binance',
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
            enable_rate_limit=enable_rate_limit,
            timeout=timeout
        )
        
        self.logger = get_logger(__name__)
        
        # Configuration spécifique Binance
        self.maker_fee = self.DEFAULT_MAKER_FEE
        self.taker_fee = self.DEFAULT_TAKER_FEE
        
        # Mode testnet
        if testnet:
            self.logger.info(
                "Connecteur Binance en mode TESTNET",
                extra={'context': {'url': self.TESTNET_URL}}
            )
        else:
            self.logger.warning(
                "⚠️  Connecteur Binance en mode PRODUCTION (argent réel!)",
                extra={'context': {'url': self.PRODUCTION_URL}}
            )
    
    def connect(self) -> bool:
        """
        Se connecte à Binance
        
        Returns:
            True si succès, False sinon
        """
        # Appeler la méthode parent
        success = super().connect()
        
        if success and self.testnet:
            # Configuration spécifique au testnet
            if self.exchange:
                # URL du testnet
                self.exchange.urls['api'] = self.TESTNET_URL
                
                self.logger.info(
                    "Connecté au testnet Binance",
                    extra={'context': {
                        'url': self.TESTNET_URL,
                        'has_credentials': bool(self.api_key and self.api_secret)
                    }}
                )
        
        return success
    
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
        
        account = self._execute_request('fetch_balance')
        
        # Extraire les infos utiles
        info = {
            'can_trade': account.get('info', {}).get('canTrade', False),
            'can_withdraw': account.get('info', {}).get('canWithdraw', False),
            'can_deposit': account.get('info', {}).get('canDeposit', False),
            'update_time': account.get('info', {}).get('updateTime'),
            'account_type': account.get('info', {}).get('accountType', 'SPOT'),
            'balances': {}
        }
        
        # Ajouter les balances non nulles
        for currency, balance in account.items():
            if currency != 'info' and isinstance(balance, dict):
                total = balance.get('total', 0)
                if total > 0:
                    info['balances'][currency] = {
                        'free': balance.get('free', 0),
                        'used': balance.get('used', 0),
                        'total': total
                    }
        
        self.logger.info(
            "Informations compte récupérées",
            extra={'context': {
                'can_trade': info['can_trade'],
                'currencies_count': len(info['balances'])
            }}
        )
        
        return info
    
    def get_24h_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère les statistiques 24h pour une paire
        
        Args:
            symbol: Paire (ex: BTC/USDT)
        
        Returns:
            Statistiques 24h
        """
        ticker = self._execute_request('fetch_ticker', symbol)
        
        # Extraire les données 24h
        stats = {
            'symbol': symbol,
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
            'ask': ticker.get('ask')
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
            symbol: Paire (ex: BTC/USDT)
            interval: Intervalle (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Nombre de bougies
        
        Returns:
            Liste de bougies [timestamp, open, high, low, close, volume]
        """
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
            symbol: Paire (ex: BTC/USDT)
            limit: Nombre de niveaux (5, 10, 20, 50, 100, 500, 1000)
        
        Returns:
            Orderbook détaillé
        """
        # Binance supporte des limites spécifiques
        valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
        
        # Trouver la limite valide la plus proche
        limit = min(valid_limits, key=lambda x: abs(x - limit))
        
        orderbook = self.get_orderbook(symbol, limit)
        
        # Calculer des stats supplémentaires
        if orderbook['bids'] and orderbook['asks']:
            # Volume total sur les X premiers niveaux
            bid_volume = sum(level[1] for level in orderbook['bids'][:10])
            ask_volume = sum(level[1] for level in orderbook['asks'][:10])
            
            orderbook['bid_volume_10'] = bid_volume
            orderbook['ask_volume_10'] = ask_volume
            orderbook['volume_imbalance'] = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        
        return orderbook
    
    def test_connectivity(self) -> bool:
        """
        Teste la connectivité à Binance
        
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
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur l'exchange
        
        Returns:
            Informations complètes sur Binance
        """
        self._ensure_connected()
        
        # Utiliser les markets chargés
        info = {
            'name': 'Binance',
            'testnet': self.testnet,
            'url': self.TESTNET_URL if self.testnet else self.PRODUCTION_URL,
            'markets_count': len(self.exchange.markets),
            'currencies': list(self.exchange.currencies.keys()),
            'has': {
                'spot': True,
                'margin': True,
                'futures': True,
                'swap': True,
                'option': False
            },
            'rate_limit': self.exchange.rateLimit,
            'precision': {
                'price': 8,
                'amount': 8
            }
        }
        
        return info
    
    def get_symbols_by_quote(self, quote: str = 'USDT') -> List[str]:
        """
        Récupère toutes les paires avec une devise de quote spécifique
        
        Args:
            quote: Devise de quote (USDT, BTC, ETH, etc.)
        
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
    
    def __repr__(self):
        """Représentation textuelle"""
        mode = "TESTNET" if self.testnet else "PRODUCTION"
        status = "connected" if self.is_connected() else "disconnected"
        return f"<BinanceConnector({mode}, {status})>"


# Exemple d'utilisation
if __name__ == "__main__":
    # Mode testnet (sans credentials)
    print("Test Binance Connector (mode public)")
    print("=" * 50)
    
    with BinanceConnector(testnet=True) as conn:
        # Test connectivité
        if conn.test_connectivity():
            print("✅ Connectivité OK")
        
        # Informations exchange
        info = conn.get_exchange_info()
        print(f"✅ {info['markets_count']} marchés disponibles")
        
        # Ticker BTC/USDT
        ticker = conn.get_ticker('BTC/USDT')
        print(f"✅ BTC/USDT: ${ticker['last']:,.2f}")
        
        # Stats 24h
        stats = conn.get_24h_ticker('BTC/USDT')
        print(f"✅ Variation 24h: {stats['price_change_percent']:.2f}%")
        
        # Orderbook
        depth = conn.get_depth('BTC/USDT', limit=10)
        print(f"✅ Orderbook: {len(depth['bids'])} bids, {len(depth['asks'])} asks")
        
        # Symboles USDT
        usdt_pairs = conn.get_symbols_by_quote('USDT')
        print(f"✅ {len(usdt_pairs)} paires USDT")
        
        print("\n🎉 Tous les tests réussis!")
