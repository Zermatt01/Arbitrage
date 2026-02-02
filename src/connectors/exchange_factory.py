"""
Exchange Factory
===============

Factory Pattern pour créer facilement des connecteurs d'exchanges.

Usage:
    from src.connectors.exchange_factory import ExchangeFactory
    
    # Créer un exchange
    binance = ExchangeFactory.create('binance')
    
    # Créer plusieurs exchanges
    exchanges = ExchangeFactory.create_all(['binance', 'kraken'])
    
    # Avec credentials
    binance = ExchangeFactory.create('binance', 
        api_key='key', 
        api_secret='secret'
    )
"""

from typing import Dict, List, Optional, Any, Type
from src.connectors.base_connector import BaseConnector
from src.connectors.binance_connector import BinanceConnector
from src.connectors.kraken_connector import KrakenConnector
from src.utils.logger import get_logger


class ExchangeFactory:
    """
    Factory pour créer des connecteurs d'exchanges
    
    Permet de créer facilement des connecteurs sans avoir à
    importer manuellement chaque classe.
    """
    
    # Registre des connecteurs disponibles
    _registry: Dict[str, Type[BaseConnector]] = {
        'binance': BinanceConnector,
        'kraken': KrakenConnector,
    }
    
    # Configuration par défaut pour chaque exchange
    _default_config: Dict[str, Dict[str, Any]] = {
        'binance': {
            'testnet': False,
            'enable_rate_limit': True,
            'timeout': 30000
        },
        'kraken': {
            'enable_rate_limit': True,
            'timeout': 30000
        }
    }
    
    @classmethod
    def create(
        cls,
        exchange_name: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        **kwargs
    ) -> BaseConnector:
        """
        Crée un connecteur pour un exchange spécifique
        
        Args:
            exchange_name: Nom de l'exchange ('binance', 'kraken', etc.)
            api_key: Clé API (optionnel)
            api_secret: Secret API (optionnel)
            **kwargs: Paramètres supplémentaires spécifiques à l'exchange
        
        Returns:
            Instance du connecteur
        
        Raises:
            ValueError si l'exchange n'est pas supporté
        
        Examples:
            >>> # Mode public
            >>> binance = ExchangeFactory.create('binance')
            
            >>> # Avec credentials
            >>> binance = ExchangeFactory.create('binance',
            ...     api_key='key',
            ...     api_secret='secret',
            ...     testnet=True
            ... )
        """
        logger = get_logger(__name__)
        
        # Normaliser le nom (minuscules)
        exchange_name = exchange_name.lower()
        
        # Vérifier que l'exchange est supporté
        if exchange_name not in cls._registry:
            available = ', '.join(cls._registry.keys())
            raise ValueError(
                f"Exchange '{exchange_name}' non supporté. "
                f"Exchanges disponibles: {available}"
            )
        
        # Récupérer la classe du connecteur
        connector_class = cls._registry[exchange_name]
        
        # Récupérer la config par défaut
        default_config = cls._default_config.get(exchange_name, {})
        
        # Merger la config par défaut avec les kwargs
        config = {**default_config, **kwargs}
        
        # Créer le connecteur
        try:
            connector = connector_class(
                api_key=api_key,
                api_secret=api_secret,
                **config
            )
            
            logger.info(
                f"Connecteur {exchange_name} créé",
                extra={'context': {
                    'exchange': exchange_name,
                    'has_credentials': bool(api_key and api_secret)
                }}
            )
            
            return connector
            
        except Exception as e:
            logger.error(
                f"Erreur lors de la création du connecteur {exchange_name}",
                exc_info=True,
                extra={'context': {'error': str(e)}}
            )
            raise
    
    @classmethod
    def create_all(
        cls,
        exchange_names: List[str],
        credentials: Optional[Dict[str, Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, BaseConnector]:
        """
        Crée plusieurs connecteurs en une seule fois
        
        Args:
            exchange_names: Liste des noms d'exchanges
            credentials: Dict des credentials par exchange
                Format: {'binance': {'api_key': '...', 'api_secret': '...'}}
            **kwargs: Paramètres communs à tous les exchanges
        
        Returns:
            Dictionnaire {exchange_name: connector}
        
        Examples:
            >>> # Sans credentials
            >>> exchanges = ExchangeFactory.create_all(['binance', 'kraken'])
            
            >>> # Avec credentials
            >>> credentials = {
            ...     'binance': {'api_key': 'key1', 'api_secret': 'secret1'},
            ...     'kraken': {'api_key': 'key2', 'api_secret': 'secret2'}
            ... }
            >>> exchanges = ExchangeFactory.create_all(
            ...     ['binance', 'kraken'],
            ...     credentials=credentials
            ... )
        """
        logger = get_logger(__name__)
        
        credentials = credentials or {}
        connectors = {}
        
        for exchange_name in exchange_names:
            try:
                # Récupérer les credentials pour cet exchange
                creds = credentials.get(exchange_name, {})
                api_key = creds.get('api_key')
                api_secret = creds.get('api_secret')
                
                # Créer le connecteur
                connector = cls.create(
                    exchange_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    **kwargs
                )
                
                connectors[exchange_name] = connector
                
            except Exception as e:
                logger.error(
                    f"Échec de création du connecteur {exchange_name}: {e}",
                    extra={'context': {'exchange': exchange_name}}
                )
                # Continuer avec les autres exchanges
        
        logger.info(
            f"{len(connectors)}/{len(exchange_names)} connecteurs créés",
            extra={'context': {
                'requested': exchange_names,
                'created': list(connectors.keys())
            }}
        )
        
        return connectors
    
    @classmethod
    def create_from_config(cls, config: Any = None) -> Dict[str, BaseConnector]:
        """
        Crée des connecteurs depuis la configuration
        
        Args:
            config: Objet de configuration (Config par défaut)
        
        Returns:
            Dictionnaire {exchange_name: connector}
        
        Examples:
            >>> from config.config import Config
            >>> exchanges = ExchangeFactory.create_from_config(Config)
        """
        logger = get_logger(__name__)
        
        # Importer Config si non fourni
        if config is None:
            try:
                from config.config import Config
                config = Config
            except ImportError:
                logger.error("Impossible d'importer Config")
                return {}
        
        connectors = {}
        
        # Binance
        if hasattr(config, 'BINANCE_API_KEY') and config.BINANCE_API_KEY:
            if config.BINANCE_API_KEY != 'your_binance_api_key':
                try:
                    testnet = getattr(config, 'BINANCE_TESTNET', False)
                    connectors['binance'] = cls.create(
                        'binance',
                        api_key=config.BINANCE_API_KEY,
                        api_secret=config.BINANCE_API_SECRET,
                        testnet=testnet
                    )
                    logger.info("Connecteur Binance créé depuis config")
                except Exception as e:
                    logger.error(f"Erreur création Binance: {e}")
        
        # Kraken
        if hasattr(config, 'KRAKEN_API_KEY') and config.KRAKEN_API_KEY:
            if config.KRAKEN_API_KEY != 'your_kraken_api_key':
                try:
                    connectors['kraken'] = cls.create(
                        'kraken',
                        api_key=config.KRAKEN_API_KEY,
                        api_secret=config.KRAKEN_API_SECRET
                    )
                    logger.info("Connecteur Kraken créé depuis config")
                except Exception as e:
                    logger.error(f"Erreur création Kraken: {e}")
        
        # Si aucun credentials configuré, créer en mode public
        if not connectors:
            logger.info("Aucun credentials configuré, mode public")
            connectors = cls.create_all(['binance', 'kraken'])
        
        return connectors
    
    @classmethod
    def register(cls, name: str, connector_class: Type[BaseConnector]):
        """
        Enregistre un nouveau connecteur dans la factory
        
        Permet d'ajouter des connecteurs personnalisés
        
        Args:
            name: Nom de l'exchange
            connector_class: Classe du connecteur
        
        Examples:
            >>> class MyExchangeConnector(BaseConnector):
            ...     pass
            >>> ExchangeFactory.register('myexchange', MyExchangeConnector)
            >>> conn = ExchangeFactory.create('myexchange')
        """
        logger = get_logger(__name__)
        
        name = name.lower()
        cls._registry[name] = connector_class
        
        logger.info(
            f"Connecteur {name} enregistré",
            extra={'context': {'name': name, 'class': connector_class.__name__}}
        )
    
    @classmethod
    def get_available_exchanges(cls) -> List[str]:
        """
        Retourne la liste des exchanges disponibles
        
        Returns:
            Liste des noms d'exchanges
        
        Examples:
            >>> ExchangeFactory.get_available_exchanges()
            ['binance', 'kraken']
        """
        return list(cls._registry.keys())
    
    @classmethod
    def is_supported(cls, exchange_name: str) -> bool:
        """
        Vérifie si un exchange est supporté
        
        Args:
            exchange_name: Nom de l'exchange
        
        Returns:
            True si supporté, False sinon
        
        Examples:
            >>> ExchangeFactory.is_supported('binance')
            True
            >>> ExchangeFactory.is_supported('unknown')
            False
        """
        return exchange_name.lower() in cls._registry
    
    @classmethod
    def connect_all(cls, connectors: Dict[str, BaseConnector]) -> Dict[str, bool]:
        """
        Connecte tous les connecteurs
        
        Args:
            connectors: Dict des connecteurs
        
        Returns:
            Dict {exchange_name: success}
        
        Examples:
            >>> connectors = ExchangeFactory.create_all(['binance', 'kraken'])
            >>> results = ExchangeFactory.connect_all(connectors)
            >>> results
            {'binance': True, 'kraken': True}
        """
        logger = get_logger(__name__)
        results = {}
        
        for name, connector in connectors.items():
            try:
                success = connector.connect()
                results[name] = success
                
                if success:
                    logger.info(f"Connecté à {name}")
                else:
                    logger.warning(f"Échec de connexion à {name}")
                    
            except Exception as e:
                logger.error(f"Erreur lors de la connexion à {name}: {e}")
                results[name] = False
        
        return results
    
    @classmethod
    def disconnect_all(cls, connectors: Dict[str, BaseConnector]):
        """
        Déconnecte tous les connecteurs
        
        Args:
            connectors: Dict des connecteurs
        
        Examples:
            >>> connectors = ExchangeFactory.create_all(['binance', 'kraken'])
            >>> ExchangeFactory.connect_all(connectors)
            >>> # ... utiliser les connecteurs ...
            >>> ExchangeFactory.disconnect_all(connectors)
        """
        logger = get_logger(__name__)
        
        for name, connector in connectors.items():
            try:
                connector.disconnect()
                logger.info(f"Déconnecté de {name}")
            except Exception as e:
                logger.error(f"Erreur lors de la déconnexion de {name}: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    print("Test Exchange Factory")
    print("=" * 50)
    
    # Lister les exchanges disponibles
    available = ExchangeFactory.get_available_exchanges()
    print(f"✅ Exchanges disponibles: {', '.join(available)}")
    
    # Créer un seul exchange
    print("\n1. Créer Binance...")
    binance = ExchangeFactory.create('binance')
    print(f"✅ {binance}")
    
    # Créer plusieurs exchanges
    print("\n2. Créer plusieurs exchanges...")
    exchanges = ExchangeFactory.create_all(['binance', 'kraken'])
    print(f"✅ {len(exchanges)} exchanges créés")
    
    # Connecter tous
    print("\n3. Connexion à tous les exchanges...")
    results = ExchangeFactory.connect_all(exchanges)
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}: {'Connecté' if success else 'Échec'}")
    
    # Récupérer des prix
    print("\n4. Récupérer les prix BTC...")
    for name, connector in exchanges.items():
        if connector.is_connected():
            try:
                symbol = 'BTC/USDT' if name == 'binance' else 'BTC/USD'
                ticker = connector.get_ticker(symbol)
                print(f"✅ {name}: ${ticker['last']:,.2f}")
            except Exception as e:
                print(f"❌ {name}: Erreur - {e}")
    
    # Déconnecter tous
    print("\n5. Déconnexion...")
    ExchangeFactory.disconnect_all(exchanges)
    print("✅ Tous déconnectés")
    
    print("\n🎉 Factory Pattern fonctionnel!")
