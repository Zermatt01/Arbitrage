"""
Classe de Base pour les Connecteurs d'Exchanges
==============================================

Classe abstraite qui définit l'interface commune pour tous les exchanges.

Usage:
    from src.connectors.base_connector import BaseConnector
    
    class BinanceConnector(BaseConnector):
        def __init__(self, api_key, api_secret):
            super().__init__('binance', api_key, api_secret)
"""

import ccxt
import time
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from src.utils.logger import get_logger


class ExchangeError(Exception):
    """Erreur générique d'exchange"""
    pass


class ConnectionError(ExchangeError):
    """Erreur de connexion à l'exchange"""
    pass


class RateLimitError(ExchangeError):
    """Rate limit atteint"""
    pass


class InsufficientFundsError(ExchangeError):
    """Fonds insuffisants"""
    pass


class BaseConnector(ABC):
    """
    Classe de base abstraite pour tous les connecteurs d'exchanges
    
    Fournit :
    - Connexion via CCXT
    - Gestion d'erreurs standardisée
    - Rate limiting
    - Reconnexion automatique
    - Logging intégré
    """
    
    def __init__(
        self,
        exchange_name: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False,
        enable_rate_limit: bool = True,
        timeout: int = 30000  # 30 secondes en ms
    ):
        """
        Initialise le connecteur
        
        Args:
            exchange_name: Nom de l'exchange (binance, kraken, etc.)
            api_key: Clé API (optionnel pour lecture publique)
            api_secret: Secret API (optionnel pour lecture publique)
            testnet: Utiliser le testnet ?
            enable_rate_limit: Activer le rate limiting CCXT ?
            timeout: Timeout en millisecondes
        """
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.enable_rate_limit = enable_rate_limit
        self.timeout = timeout
        
        # Logger
        self.logger = get_logger(f"{__name__}.{exchange_name}")
        
        # Exchange CCXT
        self.exchange: Optional[ccxt.Exchange] = None
        
        # Statistiques
        self.stats = {
            'requests_count': 0,
            'errors_count': 0,
            'last_request_time': None,
            'connection_time': None,
            'is_connected': False
        }
        
        # Rate limiting manuel (backup)
        self.min_request_interval = 0.1  # 100ms entre chaque requête
        self.last_request_timestamp = 0
        
        self.logger.info(f"Connecteur {exchange_name} initialisé", extra={
            'context': {
                'testnet': testnet,
                'has_credentials': bool(api_key and api_secret)
            }
        })
    
    def connect(self) -> bool:
        """
        Se connecte à l'exchange
        
        Returns:
            True si succès, False sinon
        """
        try:
            self.logger.info(f"Connexion à {self.exchange_name}...")
            
            # Récupérer la classe CCXT pour cet exchange
            exchange_class = getattr(ccxt, self.exchange_name)
            
            # Configuration
            config = {
                'enableRateLimit': self.enable_rate_limit,
                'timeout': self.timeout,
            }
            
            # Ajouter les credentials si fournis
            if self.api_key and self.api_secret:
                config['apiKey'] = self.api_key
                config['secret'] = self.api_secret
            
            # Mode testnet
            if self.testnet:
                config['options'] = {'defaultType': 'future'}
                if hasattr(exchange_class, 'set_sandbox_mode'):
                    config['sandbox'] = True
            
            # Créer l'instance
            self.exchange = exchange_class(config)
            
            # Tester la connexion
            start_time = time.time()
            markets = self.exchange.load_markets()
            connection_time = (time.time() - start_time) * 1000  # en ms
            
            # Mettre à jour les stats
            self.stats['is_connected'] = True
            self.stats['connection_time'] = connection_time
            
            self.logger.info(
                f"Connecté à {self.exchange_name}",
                extra={'context': {
                    'markets_count': len(markets),
                    'connection_time_ms': round(connection_time, 2),
                    'testnet': self.testnet
                }}
            )
            
            return True
            
        except ccxt.NetworkError as e:
            self.logger.error(
                f"Erreur réseau lors de la connexion à {self.exchange_name}",
                exc_info=True,
                extra={'context': {'error': str(e)}}
            )
            self.stats['errors_count'] += 1
            return False
            
        except ccxt.ExchangeError as e:
            self.logger.error(
                f"Erreur d'exchange lors de la connexion à {self.exchange_name}",
                exc_info=True,
                extra={'context': {'error': str(e)}}
            )
            self.stats['errors_count'] += 1
            return False
            
        except Exception as e:
            self.logger.error(
                f"Erreur inattendue lors de la connexion à {self.exchange_name}",
                exc_info=True,
                extra={'context': {'error': str(e)}}
            )
            self.stats['errors_count'] += 1
            return False
    
    def disconnect(self):
        """Déconnecte de l'exchange"""
        if self.exchange:
            try:
                # CCXT n'a pas vraiment de méthode disconnect
                # On met juste à jour le statut
                self.stats['is_connected'] = False
                self.exchange = None
                
                self.logger.info(f"Déconnecté de {self.exchange_name}")
                
            except Exception as e:
                self.logger.error(
                    f"Erreur lors de la déconnexion de {self.exchange_name}",
                    exc_info=True
                )
    
    def is_connected(self) -> bool:
        """
        Vérifie si connecté à l'exchange
        
        Returns:
            True si connecté, False sinon
        """
        return self.stats['is_connected'] and self.exchange is not None
    
    def _ensure_connected(self):
        """
        S'assure que la connexion est active, reconnecte si nécessaire
        
        Raises:
            ConnectionError si impossible de se connecter
        """
        if not self.is_connected():
            self.logger.warning(f"Pas connecté à {self.exchange_name}, reconnexion...")
            
            if not self.connect():
                raise ConnectionError(f"Impossible de se connecter à {self.exchange_name}")
    
    def _wait_rate_limit(self):
        """Attend si nécessaire pour respecter le rate limit"""
        now = time.time()
        elapsed = now - self.last_request_timestamp
        
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            time.sleep(wait_time)
        
        self.last_request_timestamp = time.time()
    
    def _execute_request(
        self,
        method_name: str,
        *args,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ) -> Any:
        """
        Exécute une requête avec gestion d'erreurs et retry
        
        Args:
            method_name: Nom de la méthode CCXT à appeler
            *args: Arguments positionnels
            retry_count: Nombre de tentatives
            retry_delay: Délai entre les tentatives (secondes)
            **kwargs: Arguments nommés
        
        Returns:
            Résultat de la requête
        
        Raises:
            ExchangeError en cas d'échec après toutes les tentatives
        """
        self._ensure_connected()
        
        last_error = None
        
        for attempt in range(retry_count):
            try:
                # Rate limiting
                self._wait_rate_limit()
                
                # Récupérer la méthode
                method = getattr(self.exchange, method_name)
                
                # Exécuter
                start_time = time.time()
                result = method(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000
                
                # Mettre à jour les stats
                self.stats['requests_count'] += 1
                self.stats['last_request_time'] = datetime.now()
                
                # Logger
                self.logger.debug(
                    f"{method_name} réussi",
                    extra={'context': {
                        'exchange': self.exchange_name,
                        'duration_ms': round(elapsed_ms, 2),
                        'attempt': attempt + 1
                    }}
                )
                
                return result
                
            except ccxt.RateLimitExceeded as e:
                last_error = e
                self.logger.warning(
                    f"Rate limit atteint sur {self.exchange_name}",
                    extra={'context': {
                        'attempt': attempt + 1,
                        'retry_in': retry_delay
                    }}
                )
                
                if attempt < retry_count - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Backoff exponentiel
                
            except ccxt.NetworkError as e:
                last_error = e
                self.logger.warning(
                    f"Erreur réseau sur {self.exchange_name}",
                    extra={'context': {
                        'attempt': attempt + 1,
                        'error': str(e)
                    }}
                )
                
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
                
            except ccxt.ExchangeNotAvailable as e:
                last_error = e
                self.logger.error(
                    f"{self.exchange_name} non disponible",
                    extra={'context': {
                        'attempt': attempt + 1,
                        'error': str(e)
                    }}
                )
                
                if attempt < retry_count - 1:
                    time.sleep(retry_delay * 2)
                
            except ccxt.InsufficientFunds as e:
                # Pas de retry pour fonds insuffisants
                self.logger.error(f"Fonds insuffisants sur {self.exchange_name}")
                raise InsufficientFundsError(str(e))
                
            except ccxt.ExchangeError as e:
                last_error = e
                self.logger.error(
                    f"Erreur d'exchange sur {self.exchange_name}",
                    exc_info=True,
                    extra={'context': {
                        'attempt': attempt + 1,
                        'error': str(e)
                    }}
                )
                
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
            
            except Exception as e:
                last_error = e
                self.logger.error(
                    f"Erreur inattendue sur {self.exchange_name}",
                    exc_info=True,
                    extra={'context': {
                        'method': method_name,
                        'error': str(e)
                    }}
                )
                break  # Pas de retry pour erreurs inconnues
        
        # Toutes les tentatives ont échoué
        self.stats['errors_count'] += 1
        
        error_msg = f"Échec de {method_name} après {retry_count} tentatives: {last_error}"
        self.logger.error(error_msg)
        
        raise ExchangeError(error_msg)
    
    def get_balance(self, currency: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère la balance
        
        Args:
            currency: Devise spécifique (optionnel)
        
        Returns:
            Dictionnaire des balances
        """
        balance = self._execute_request('fetch_balance')
        
        if currency:
            return {
                'free': balance.get(currency, {}).get('free', 0),
                'used': balance.get(currency, {}).get('used', 0),
                'total': balance.get(currency, {}).get('total', 0)
            }
        
        return balance
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère le ticker pour une paire
        
        Args:
            symbol: Paire (ex: BTC/USDT)
        
        Returns:
            Dictionnaire du ticker
        """
        ticker = self._execute_request('fetch_ticker', symbol)
        
        # Normaliser le format
        return {
            'symbol': symbol,
            'exchange': self.exchange_name,
            'bid': ticker.get('bid'),
            'ask': ticker.get('ask'),
            'last': ticker.get('last'),
            'volume': ticker.get('baseVolume'),
            'quote_volume': ticker.get('quoteVolume'),
            'timestamp': ticker.get('timestamp'),
            'datetime': ticker.get('datetime')
        }
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Récupère le carnet d'ordres (orderbook) pour une paire
        
        Args:
            symbol: Paire de trading (ex: BTC/USDT)
            limit: Nombre de niveaux à récupérer (défaut: 20)
        
        Returns:
            Dict avec bids, asks, et métadonnées
            {
                'symbol': 'BTC/USDT',
                'bids': [[price, volume], ...],
                'asks': [[price, volume], ...],
                'timestamp': datetime,
                'exchange': 'binance'
            }
        """
        if not self.is_connected():
            raise ConnectionError(f"Non connecté à {self.exchange_name}")
        
        try:
            start_time = time.time()
            
            self.logger.debug(
                f"Récupération orderbook {symbol} (limit={limit})...",
                extra={'context': {'symbol': symbol, 'limit': limit}}
            )
            
            # Récupérer l'orderbook via CCXT
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            
            # Calculer latence
            latency_ms = (time.time() - start_time) * 1000
            
            # Formater les données
            result = {
                'symbol': symbol,
                'exchange': self.exchange_name,
                'bids': orderbook['bids'],  # [[price, volume], ...]
                'asks': orderbook['asks'],  # [[price, volume], ...]
                'timestamp': datetime.utcnow(),
                'nonce': orderbook.get('nonce'),
                'latency_ms': latency_ms
            }
            
            # Calculer statistiques
            total_bid_volume = sum(bid[1] for bid in orderbook['bids']) if orderbook['bids'] else 0
            total_ask_volume = sum(ask[1] for ask in orderbook['asks']) if orderbook['asks'] else 0
            
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else None
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else None
            
            result['stats'] = {
                'total_bid_volume': total_bid_volume,
                'total_ask_volume': total_ask_volume,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': (best_ask - best_bid) if (best_bid and best_ask) else None,
                'spread_pct': ((best_ask - best_bid) / best_bid * 100) if (best_bid and best_ask) else None
            }
            
            self.logger.debug(
                f"Orderbook {symbol} récupéré: {len(orderbook['bids'])} bids, {len(orderbook['asks'])} asks",
                extra={'context': {
                    'symbol': symbol,
                    'bid_levels': len(orderbook['bids']),
                    'ask_levels': len(orderbook['asks']),
                    'latency_ms': latency_ms
                }}
            )
            
            return result
            
        except ccxt.BaseError as e:
            error_msg = f"Erreur CCXT lors de la récupération orderbook {symbol}: {e}"
            self.logger.error(error_msg, extra={'context': {'symbol': symbol, 'error': str(e)}})
            raise
        except Exception as e:
            error_msg = f"Erreur lors de la récupération orderbook {symbol}: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise
    
    def get_markets(self) -> List[str]:
        """
        Récupère la liste des paires disponibles
        
        Returns:
            Liste des symboles
        """
        if not self.is_connected():
            self._ensure_connected()
        
        return list(self.exchange.markets.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du connecteur
        
        Returns:
            Dictionnaire de statistiques
        """
        return {
            'exchange': self.exchange_name,
            'is_connected': self.stats['is_connected'],
            'requests_count': self.stats['requests_count'],
            'errors_count': self.stats['errors_count'],
            'error_rate': self.stats['errors_count'] / max(self.stats['requests_count'], 1),
            'last_request_time': self.stats['last_request_time'],
            'connection_time_ms': self.stats['connection_time']
        }
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à l'exchange
        
        Returns:
            True si OK, False sinon
        """
        try:
            self._ensure_connected()
            
            # Tester avec une requête simple
            self.exchange.fetch_ticker(list(self.exchange.markets.keys())[0])
            
            self.logger.info(f"Test de connexion à {self.exchange_name} réussi")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Test de connexion à {self.exchange_name} échoué",
                exc_info=True
            )
            return False
    
    def __repr__(self):
        """Représentation textuelle"""
        status = "connected" if self.is_connected() else "disconnected"
        return f"<{self.__class__.__name__}({self.exchange_name}, {status})>"
    
    def __enter__(self):
        """Support du context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support du context manager"""
        self.disconnect()
