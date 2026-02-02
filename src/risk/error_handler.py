"""
Error Handler - Gestionnaire d'Erreurs Global
==============================================

Centralise la gestion de toutes les erreurs avec retry et logging.

Usage:
    from src.risk.error_handler import ErrorHandler, ErrorType
    
    handler = ErrorHandler()
    
    # Gérer une erreur
    action = handler.handle_error(error, ErrorType.NETWORK)
    
    if action == 'retry':
        # Réessayer
        pass
    elif action == 'skip':
        # Passer au suivant
        pass
"""

from typing import Callable, Any, Optional, Dict
from enum import Enum
import time
import traceback
from src.utils.logger import get_logger


class ErrorType(Enum):
    """Types d'erreurs"""
    NETWORK = "network"              # Erreur réseau
    API_RATE_LIMIT = "api_rate_limit"  # Rate limit dépassé
    INSUFFICIENT_FUNDS = "insufficient_funds"  # Fonds insuffisants
    INVALID_ORDER = "invalid_order"  # Ordre invalide
    EXCHANGE_ERROR = "exchange_error"  # Erreur exchange
    DATABASE_ERROR = "database_error"  # Erreur DB
    VALIDATION_ERROR = "validation_error"  # Erreur validation
    TIMEOUT = "timeout"              # Timeout
    CRITICAL = "critical"            # Erreur critique
    UNKNOWN = "unknown"              # Erreur inconnue


class ErrorAction(Enum):
    """Actions possibles"""
    RETRY = "retry"          # Réessayer
    RETRY_WITH_BACKOFF = "retry_with_backoff"  # Réessayer avec délai
    SKIP = "skip"            # Passer
    STOP = "stop"            # Arrêter tout
    ALERT = "alert"          # Alerter


class ErrorHandler:
    """
    Gestionnaire centralisé des erreurs
    
    Fonctionnalités :
    - Classification automatique des erreurs
    - Actions appropriées par type
    - Retry avec backoff exponentiel
    - Logging détaillé
    - Circuit breaker integration
    """
    
    # Configuration des actions par type d'erreur
    ERROR_ACTIONS = {
        ErrorType.NETWORK: ErrorAction.RETRY_WITH_BACKOFF,
        ErrorType.API_RATE_LIMIT: ErrorAction.RETRY_WITH_BACKOFF,
        ErrorType.INSUFFICIENT_FUNDS: ErrorAction.SKIP,
        ErrorType.INVALID_ORDER: ErrorAction.SKIP,
        ErrorType.EXCHANGE_ERROR: ErrorAction.RETRY_WITH_BACKOFF,
        ErrorType.DATABASE_ERROR: ErrorAction.RETRY,
        ErrorType.VALIDATION_ERROR: ErrorAction.SKIP,
        ErrorType.TIMEOUT: ErrorAction.RETRY_WITH_BACKOFF,
        ErrorType.CRITICAL: ErrorAction.STOP,
        ErrorType.UNKNOWN: ErrorAction.RETRY,
    }
    
    # Configuration des retry par type
    RETRY_CONFIG = {
        ErrorType.NETWORK: {'max_retries': 3, 'base_delay': 2.0},
        ErrorType.API_RATE_LIMIT: {'max_retries': 5, 'base_delay': 10.0},
        ErrorType.EXCHANGE_ERROR: {'max_retries': 3, 'base_delay': 2.0},
        ErrorType.DATABASE_ERROR: {'max_retries': 3, 'base_delay': 1.0},
        ErrorType.TIMEOUT: {'max_retries': 2, 'base_delay': 5.0},
        ErrorType.UNKNOWN: {'max_retries': 2, 'base_delay': 1.0},
    }
    
    def __init__(self, circuit_breaker=None):
        """
        Initialise le gestionnaire d'erreurs
        
        Args:
            circuit_breaker: Circuit breaker à notifier (optionnel)
        """
        self.logger = get_logger(__name__)
        self.circuit_breaker = circuit_breaker
        
        # Statistiques
        self.error_counts = {error_type: 0 for error_type in ErrorType}
        self.total_errors = 0
        self.total_retries = 0
        
        self.logger.info("ErrorHandler initialisé")
    
    def classify_error(self, error: Exception) -> ErrorType:
        """
        Classifie une erreur selon son type
        
        Args:
            error: Exception à classifier
        
        Returns:
            Type d'erreur
        """
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        # Network errors
        if any(keyword in error_str or keyword in error_type_name for keyword in 
               ['connection', 'timeout', 'network', 'unreachable', 'refused']):
            return ErrorType.NETWORK
        
        # Rate limit
        if any(keyword in error_str for keyword in 
               ['rate limit', 'too many requests', '429', 'ratelimit']):
            return ErrorType.API_RATE_LIMIT
        
        # Insufficient funds
        if any(keyword in error_str for keyword in 
               ['insufficient', 'not enough', 'balance too low', 'funds']):
            return ErrorType.INSUFFICIENT_FUNDS
        
        # Invalid order
        if any(keyword in error_str for keyword in 
               ['invalid order', 'order not found', 'invalid amount', 'invalid price']):
            return ErrorType.INVALID_ORDER
        
        # Exchange errors
        if any(keyword in error_str for keyword in 
               ['exchange', 'market', 'symbol not found']):
            return ErrorType.EXCHANGE_ERROR
        
        # Database errors
        if any(keyword in error_type_name for keyword in 
               ['database', 'psycopg', 'sql']):
            return ErrorType.DATABASE_ERROR
        
        # Timeout
        if 'timeout' in error_str or 'timeout' in error_type_name:
            return ErrorType.TIMEOUT
        
        # Validation
        if any(keyword in error_str for keyword in 
               ['validation', 'invalid', 'required']):
            return ErrorType.VALIDATION_ERROR
        
        # Critical (à définir selon vos besoins)
        if any(keyword in error_str for keyword in 
               ['critical', 'fatal', 'system']):
            return ErrorType.CRITICAL
        
        return ErrorType.UNKNOWN
    
    def handle_error(
        self,
        error: Exception,
        error_type: ErrorType = None,
        context: Dict[str, Any] = None
    ) -> ErrorAction:
        """
        Gère une erreur et retourne l'action à effectuer
        
        Args:
            error: Exception
            error_type: Type d'erreur (auto-détecté si None)
            context: Contexte additionnel
        
        Returns:
            Action à effectuer
        """
        # Classifier l'erreur si pas fourni
        if error_type is None:
            error_type = self.classify_error(error)
        
        # Incrémenter compteurs
        self.error_counts[error_type] += 1
        self.total_errors += 1
        
        # Logger l'erreur
        self.logger.error(
            f"Erreur {error_type.value}: {str(error)}",
            extra={
                'context': {
                    'error_type': error_type.value,
                    'error_message': str(error),
                    'error_class': type(error).__name__,
                    'traceback': traceback.format_exc(),
                    **(context or {})
                }
            }
        )
        
        # Notifier le circuit breaker si disponible
        if self.circuit_breaker:
            self.circuit_breaker.record_error(
                error_type=error_type.value,
                exchange=context.get('exchange') if context else None
            )
        
        # Déterminer l'action
        action = self.ERROR_ACTIONS.get(error_type, ErrorAction.SKIP)
        
        self.logger.info(
            f"Action pour {error_type.value}: {action.value}",
            extra={'context': {'error_type': error_type.value, 'action': action.value}}
        )
        
        return action
    
    def retry_with_backoff(
        self,
        func: Callable,
        error_type: ErrorType = None,
        max_retries: int = None,
        base_delay: float = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Exécute une fonction avec retry et backoff exponentiel
        
        Args:
            func: Fonction à exécuter
            error_type: Type d'erreur attendu (pour config)
            max_retries: Nombre max de tentatives
            base_delay: Délai de base en secondes
            *args, **kwargs: Arguments de la fonction
        
        Returns:
            Résultat de la fonction
        
        Raises:
            Exception si toutes les tentatives échouent
        """
        # Récupérer la config
        if error_type and error_type in self.RETRY_CONFIG:
            config = self.RETRY_CONFIG[error_type]
            max_retries = max_retries or config['max_retries']
            base_delay = base_delay or config['base_delay']
        else:
            max_retries = max_retries or 3
            base_delay = base_delay or 1.0
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                
                # Succès
                if attempt > 0:
                    self.logger.info(
                        f"Succès après {attempt + 1} tentatives",
                        extra={'context': {'attempts': attempt + 1}}
                    )
                
                return result
                
            except Exception as e:
                last_error = e
                
                # Classifier l'erreur
                detected_type = self.classify_error(e)
                
                # Si dernière tentative, abandonner
                if attempt == max_retries - 1:
                    self.logger.error(
                        f"Échec après {max_retries} tentatives: {str(e)}",
                        extra={'context': {
                            'attempts': max_retries,
                            'error': str(e)
                        }}
                    )
                    raise
                
                # Calculer le délai (backoff exponentiel)
                delay = base_delay * (2 ** attempt)
                
                self.logger.warning(
                    f"Tentative {attempt + 1}/{max_retries} échouée, "
                    f"retry dans {delay:.1f}s: {str(e)}",
                    extra={'context': {
                        'attempt': attempt + 1,
                        'max_retries': max_retries,
                        'delay': delay,
                        'error_type': detected_type.value
                    }}
                )
                
                # Incrémenter compteur
                self.total_retries += 1
                
                # Attendre avant retry
                time.sleep(delay)
        
        # Ne devrait jamais arriver ici
        raise last_error
    
    def execute_with_error_handling(
        self,
        func: Callable,
        context: Dict[str, Any] = None,
        *args,
        **kwargs
    ) -> tuple[bool, Any, Optional[Exception]]:
        """
        Exécute une fonction avec gestion d'erreurs complète
        
        Args:
            func: Fonction à exécuter
            context: Contexte pour logging
            *args, **kwargs: Arguments de la fonction
        
        Returns:
            (success, result, error)
        """
        try:
            result = func(*args, **kwargs)
            return True, result, None
            
        except Exception as e:
            # Gérer l'erreur
            error_type = self.classify_error(e)
            action = self.handle_error(e, error_type, context)
            
            # Appliquer l'action
            if action == ErrorAction.RETRY_WITH_BACKOFF:
                try:
                    result = self.retry_with_backoff(
                        func,
                        error_type=error_type,
                        *args,
                        **kwargs
                    )
                    return True, result, None
                except Exception as retry_error:
                    return False, None, retry_error
            
            elif action == ErrorAction.STOP:
                self.logger.critical(f"Erreur critique, arrêt: {str(e)}")
                raise
            
            else:  # SKIP
                return False, None, e
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques d'erreurs
        
        Returns:
            Dict avec les stats
        """
        stats = {
            'total_errors': self.total_errors,
            'total_retries': self.total_retries,
            'errors_by_type': {
                error_type.value: count
                for error_type, count in self.error_counts.items()
                if count > 0
            }
        }
        
        return stats
    
    def display_stats(self):
        """Affiche les statistiques d'erreurs"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("  STATISTIQUES D'ERREURS")
        print("=" * 60)
        
        print(f"\n📊 GLOBAL:")
        print(f"  Total erreurs:     {stats['total_errors']}")
        print(f"  Total retries:     {stats['total_retries']}")
        
        if stats['errors_by_type']:
            print(f"\n📊 PAR TYPE:")
            for error_type, count in sorted(
                stats['errors_by_type'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"  {error_type:<20} {count}")
        
        print("\n" + "=" * 60)
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        self.error_counts = {error_type: 0 for error_type in ErrorType}
        self.total_errors = 0
        self.total_retries = 0
        
        self.logger.info("Statistiques d'erreurs réinitialisées")


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST ERROR HANDLER")
    print("=" * 60)
    
    # Créer le handler
    handler = ErrorHandler()
    
    # Test 1: Classifier une erreur
    print("\n📊 Test classification:")
    error = ConnectionError("Connection refused")
    error_type = handler.classify_error(error)
    print(f"  Erreur: {error}")
    print(f"  Type: {error_type.value}")
    
    # Test 2: Gérer une erreur
    print("\n📊 Test gestion:")
    action = handler.handle_error(error)
    print(f"  Action: {action.value}")
    
    # Test 3: Retry avec backoff
    print("\n📊 Test retry:")
    
    attempt_count = 0
    
    def failing_func():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("Network error")
        return "Success!"
    
    try:
        result = handler.retry_with_backoff(
            failing_func,
            error_type=ErrorType.NETWORK
        )
        print(f"  Résultat: {result}")
        print(f"  Tentatives: {attempt_count}")
    except Exception as e:
        print(f"  Échec: {e}")
    
    # Stats
    print("\n📊 Statistiques:")
    handler.display_stats()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
