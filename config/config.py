"""
Module de Configuration
=======================

Charge et gère toutes les variables d'environnement du projet.

Usage:
    from config.config import Config
    
    # Accéder aux configurations
    api_key = Config.BINANCE_API_KEY
    db_url = Config.DATABASE_URL
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Charger le fichier .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'

# Charger les variables d'environnement
load_dotenv(ENV_FILE)


class Config:
    """
    Classe de configuration centralisant toutes les variables d'environnement
    """
    
    # === MODE D'EXECUTION ===
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DRY_RUN_MODE = os.getenv('DRY_RUN_MODE', 'true').lower() == 'true'
    
    # === BINANCE CONFIGURATION ===
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
    
    # === KRAKEN CONFIGURATION ===
    KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY', '')
    KRAKEN_API_SECRET = os.getenv('KRAKEN_API_SECRET', '')
    
    # === COINBASE PRO CONFIGURATION ===
    COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
    COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
    COINBASE_PASSPHRASE = os.getenv('COINBASE_PASSPHRASE', '')
    
    # === DATABASE CONFIGURATION ===
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'arbitrage_db')
    DB_USER = os.getenv('DB_USER', 'arbitrage_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DATABASE_URL = os.getenv('DATABASE_URL', 
                            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    
    # === REDIS CONFIGURATION ===
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # === TRADING PARAMETERS ===
    MIN_TRADE_AMOUNT = float(os.getenv('MIN_TRADE_AMOUNT', 10))
    MAX_TRADE_AMOUNT = float(os.getenv('MAX_TRADE_AMOUNT', 100))
    MIN_PROFIT_THRESHOLD = float(os.getenv('MIN_PROFIT_THRESHOLD', 0.5))
    MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', 50))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 500))
    
    # === MONITORING & ALERTS ===
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    ALERT_EMAIL = os.getenv('ALERT_EMAIL', '')
    
    # === LOGGING CONFIGURATION ===
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_JSON = os.getenv('LOG_JSON', 'true').lower() == 'true'
    LOG_DIR = Path(os.getenv('LOG_DIR', './logs'))
    
    # === TRADING PAIRS ===
    TRADING_PAIRS = os.getenv('TRADING_PAIRS', 'BTC/USDT,ETH/USDT').split(',')
    
    # === PERFORMANCE SETTINGS ===
    PRICE_COLLECTION_INTERVAL = int(os.getenv('PRICE_COLLECTION_INTERVAL', 5))
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 10))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    # === RISK MANAGEMENT ===
    CIRCUIT_BREAKER_LOSS_THRESHOLD = float(os.getenv('CIRCUIT_BREAKER_LOSS_THRESHOLD', 100))
    CIRCUIT_BREAKER_TIME_WINDOW = int(os.getenv('CIRCUIT_BREAKER_TIME_WINDOW', 30))
    MAX_CONSECUTIVE_ERRORS = int(os.getenv('MAX_CONSECUTIVE_ERRORS', 5))
    
    # === ADVANCED SETTINGS ===
    USE_CACHE = os.getenv('USE_CACHE', 'false').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 5))
    ENABLE_WEB_INTERFACE = os.getenv('ENABLE_WEB_INTERFACE', 'false').lower() == 'true'
    WEB_PORT = int(os.getenv('WEB_PORT', 5000))
    
    @classmethod
    def is_production(cls):
        """Vérifie si on est en mode production"""
        return cls.ENVIRONMENT.lower() == 'production'
    
    @classmethod
    def is_development(cls):
        """Vérifie si on est en mode développement"""
        return cls.ENVIRONMENT.lower() == 'development'
    
    @classmethod
    def is_dry_run(cls):
        """Vérifie si on est en mode dry-run (simulation)"""
        return cls.DRY_RUN_MODE
    
    @classmethod
    def validate_config(cls):
        """
        Valide la configuration et retourne les erreurs potentielles
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Vérifications critiques pour le mode production
        if cls.is_production() and not cls.is_dry_run():
            if not cls.BINANCE_API_KEY:
                errors.append("BINANCE_API_KEY manquante en mode production")
            if not cls.BINANCE_API_SECRET:
                errors.append("BINANCE_API_SECRET manquante en mode production")
        
        # Vérifications des valeurs numériques
        if cls.MIN_TRADE_AMOUNT <= 0:
            errors.append("MIN_TRADE_AMOUNT doit être > 0")
        
        if cls.MAX_TRADE_AMOUNT <= cls.MIN_TRADE_AMOUNT:
            errors.append("MAX_TRADE_AMOUNT doit être > MIN_TRADE_AMOUNT")
        
        if cls.MIN_PROFIT_THRESHOLD < 0:
            errors.append("MIN_PROFIT_THRESHOLD doit être >= 0")
        
        if cls.MAX_DAILY_TRADES <= 0:
            errors.append("MAX_DAILY_TRADES doit être > 0")
        
        # Vérification des paires de trading
        if not cls.TRADING_PAIRS:
            errors.append("Au moins une paire de trading doit être configurée")
        
        return len(errors) == 0, errors
    
    @classmethod
    def display_config(cls):
        """Affiche la configuration actuelle (masque les secrets)"""
        config_display = {
            'Environment': cls.ENVIRONMENT,
            'Dry Run Mode': cls.DRY_RUN_MODE,
            'Binance Testnet': cls.BINANCE_TESTNET,
            'Binance API Key': cls._mask_secret(cls.BINANCE_API_KEY),
            'Kraken API Key': cls._mask_secret(cls.KRAKEN_API_KEY),
            'Database': f"{cls.DB_USER}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}",
            'Min Trade Amount': cls.MIN_TRADE_AMOUNT,
            'Max Trade Amount': cls.MAX_TRADE_AMOUNT,
            'Min Profit Threshold': f"{cls.MIN_PROFIT_THRESHOLD}%",
            'Max Daily Trades': cls.MAX_DAILY_TRADES,
            'Trading Pairs': ', '.join(cls.TRADING_PAIRS),
            'Log Level': cls.LOG_LEVEL,
            'Use Cache': cls.USE_CACHE,
        }
        
        return config_display
    
    @staticmethod
    def _mask_secret(secret):
        """Masque un secret pour l'affichage"""
        if not secret or len(secret) == 0:
            return "Non configuré"
        if len(secret) <= 8:
            return "****"
        return f"{secret[:4]}...{secret[-4:]}"


# Créer une instance globale pour l'import facile
config = Config()


# Validation automatique au chargement
if __name__ != "__main__":
    is_valid, errors = Config.validate_config()
    if not is_valid:
        import warnings
        for error in errors:
            warnings.warn(f"Configuration Warning: {error}")
