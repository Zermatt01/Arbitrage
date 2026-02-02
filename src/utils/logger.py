"""
Module Logger - Système de Logging Centralisé
=============================================

Système de logging professionnel pour le bot d'arbitrage.

Features:
- Logs dans fichiers avec rotation automatique
- Logs dans la base de données PostgreSQL
- 5 niveaux: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Format JSON structuré
- Contexte enrichi automatique

Usage:
    from src.utils.logger import get_logger
    
    logger = get_logger(__name__)
    
    logger.info("Message simple")
    logger.error("Erreur détectée", extra={'exchange': 'binance'})
    logger.critical("Problème critique!", exc_info=True)
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import traceback


class JSONFormatter(logging.Formatter):
    """
    Formatter qui convertit les logs en JSON structuré
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatte le log en JSON"""
        
        # Données de base
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Ajouter le contexte supplémentaire s'il existe
        if hasattr(record, 'context') and record.context:
            log_data['context'] = record.context
        
        # Ajouter la stack trace pour les erreurs
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Ajouter des champs custom s'ils existent
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'lineno', 'module', 'msecs', 'message', 
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                          'context']:
                if not key.startswith('_'):
                    log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """
    Formatter coloré pour la console
    """
    
    # Codes couleurs ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    # Emojis pour chaque niveau
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatte le log pour la console avec couleurs"""
        
        # Couleur selon le niveau
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        emoji = self.EMOJIS.get(record.levelname, '')
        
        # Format: [TIME] EMOJI LEVEL - module.function: message
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        formatted = (
            f"{color}[{timestamp}] {emoji} {record.levelname:8}{reset} - "
            f"{record.module}.{record.funcName}: {record.getMessage()}"
        )
        
        # Ajouter le contexte s'il existe
        if hasattr(record, 'context') and record.context:
            formatted += f"\n  Context: {json.dumps(record.context, ensure_ascii=False)}"
        
        # Ajouter la stack trace pour les erreurs
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class DatabaseHandler(logging.Handler):
    """
    Handler qui écrit les logs dans la base de données PostgreSQL
    """
    
    def __init__(self, database_url: str):
        """
        Initialise le handler
        
        Args:
            database_url: URL de connexion PostgreSQL
        """
        super().__init__()
        self.database_url = database_url
        self._engine = None
        self._Session = None
    
    def _get_session(self):
        """Crée ou retourne une session SQLAlchemy"""
        if self._engine is None:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            self._engine = create_engine(
                self.database_url,
                pool_pre_ping=True,  # Vérifier la connexion avant utilisation
                pool_size=5,
                max_overflow=10
            )
            self._Session = sessionmaker(bind=self._engine)
        
        return self._Session()
    
    def emit(self, record: logging.LogRecord):
        """
        Écrit le log dans la base de données
        
        Args:
            record: Log record à écrire
        """
        try:
            from sqlalchemy import text
            
            session = self._get_session()
            
            # Préparer le contexte
            context = {}
            if hasattr(record, 'context') and record.context:
                context = record.context
            
            # Ajouter des infos supplémentaires
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                              'levelname', 'lineno', 'module', 'msecs', 'message', 
                              'pathname', 'process', 'processName', 'relativeCreated',
                              'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                              'context']:
                    if not key.startswith('_'):
                        context[key] = str(value)
            
            # Stack trace si erreur
            stack_trace = None
            if record.exc_info:
                stack_trace = ''.join(traceback.format_exception(*record.exc_info))
            
            # Insérer dans la base de données
            query = text("""
                INSERT INTO system_logs (
                    level, module, function_name, message, 
                    context, stack_trace, environment
                ) VALUES (
                    :level, :module, :function_name, :message,
                    :context, :stack_trace, :environment
                )
            """)
            
            session.execute(query, {
                'level': record.levelname,
                'module': record.module,
                'function_name': record.funcName,
                'message': record.getMessage(),
                'context': json.dumps(context) if context else None,
                'stack_trace': stack_trace,
                'environment': os.getenv('ENVIRONMENT', 'development')
            })
            
            session.commit()
            session.close()
            
        except Exception as e:
            # Ne pas planter si impossible de logger en DB
            # Simplement afficher l'erreur
            print(f"Erreur lors de l'écriture du log en base de données: {e}", file=sys.stderr)
            self.handleError(record)


def setup_logger(
    name: str,
    log_level: str = 'INFO',
    log_to_console: bool = True,
    log_to_file: bool = True,
    log_to_database: bool = True,
    log_dir: Optional[Path] = None,
    database_url: Optional[str] = None
) -> logging.Logger:
    """
    Configure et retourne un logger
    
    Args:
        name: Nom du logger
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Logger dans la console ?
        log_to_file: Logger dans des fichiers ?
        log_to_database: Logger dans PostgreSQL ?
        log_dir: Dossier pour les fichiers de logs
        database_url: URL PostgreSQL
    
    Returns:
        Logger configuré
    """
    
    logger = logging.getLogger(name)
    
    # Éviter de recréer les handlers si le logger existe déjà
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Handler Console
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ConsoleFormatter())
        logger.addHandler(console_handler)
    
    # Handler Fichier
    if log_to_file:
        if log_dir is None:
            log_dir = Path('logs')
        
        log_dir.mkdir(exist_ok=True)
        
        # Fichier pour tous les logs
        all_logs_file = log_dir / 'arbitrage.log'
        file_handler = logging.handlers.RotatingFileHandler(
            all_logs_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
        
        # Fichier séparé pour les erreurs
        error_logs_file = log_dir / 'errors.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_logs_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        logger.addHandler(error_handler)
    
    # Handler Base de Données
    if log_to_database and database_url:
        try:
            db_handler = DatabaseHandler(database_url)
            db_handler.setLevel(logging.INFO)  # Ne logger que INFO et plus en DB
            logger.addHandler(db_handler)
        except Exception as e:
            logger.warning(f"Impossible de configurer le logging en base de données: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger configuré pour le bot d'arbitrage
    
    Usage:
        from src.utils.logger import get_logger
        
        logger = get_logger(__name__)
        logger.info("Message")
    
    Args:
        name: Nom du logger (généralement __name__)
    
    Returns:
        Logger configuré
    """
    
    # Charger la configuration
    try:
        from config.config import Config
        
        return setup_logger(
            name=name,
            log_level=Config.LOG_LEVEL,
            log_to_console=True,
            log_to_file=True,
            log_to_database=not Config.DRY_RUN_MODE,  # Pas de DB en dry-run
            log_dir=Path('logs'),
            database_url=Config.DATABASE_URL if not Config.DRY_RUN_MODE else None
        )
    except ImportError:
        # Fallback si config non disponible
        return setup_logger(
            name=name,
            log_level='INFO',
            log_to_console=True,
            log_to_file=True,
            log_to_database=False
        )


# Logger racine pour le bot
root_logger = get_logger('arbitrage_bot')


def log_function_call(func):
    """
    Décorateur pour logger automatiquement les appels de fonction
    
    Usage:
        @log_function_call
        def ma_fonction(param1, param2):
            return param1 + param2
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        logger.debug(
            f"Appel de {func.__name__}",
            extra={'context': {
                'args': str(args)[:100],
                'kwargs': str(kwargs)[:100]
            }}
        )
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} terminé avec succès")
            return result
        except Exception as e:
            logger.error(
                f"Erreur dans {func.__name__}: {e}",
                exc_info=True,
                extra={'context': {
                    'args': str(args)[:100],
                    'kwargs': str(kwargs)[:100]
                }}
            )
            raise
    
    return wrapper


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer un logger
    logger = get_logger(__name__)
    
    # Tester tous les niveaux
    logger.debug("Message de debug")
    logger.info("Message d'information")
    logger.warning("Message d'avertissement")
    logger.error("Message d'erreur")
    logger.critical("Message critique")
    
    # Avec contexte
    logger.info("Opportunité détectée", extra={
        'context': {
            'symbol': 'BTC/USDT',
            'profit': 0.85,
            'exchange': 'binance'
        }
    })
    
    # Avec exception
    try:
        x = 1 / 0
    except Exception as e:
        logger.error("Division par zéro", exc_info=True)
    
    print("\n✅ Tests de logging terminés")
    print("📁 Vérifiez le dossier 'logs/'")
    print("🗄️  Vérifiez la table 'system_logs' en base de données")
