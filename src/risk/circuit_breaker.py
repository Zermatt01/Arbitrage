"""
Circuit Breaker - Système d'Arrêt d'Urgence
============================================

Arrête automatiquement le trading en cas de problème.

Usage:
    from src.risk.circuit_breaker import CircuitBreaker
    
    cb = CircuitBreaker()
    if cb.is_open():
        print("❌ Trading arrêté")
    else:
        execute_trade()
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger


class CircuitBreaker:
    """
    Système d'arrêt automatique du trading en cas de problème
    
    Conditions de déclenchement :
    - Perte trop importante en peu de temps
    - Trop d'erreurs consécutives
    - Exchange indisponible
    - Balance anormale
    """
    
    # Configuration par défaut
    DEFAULT_CONFIG = {
        # Pertes
        'max_loss_in_minutes': 100.0,      # $100 max en X minutes
        'loss_window_minutes': 15,         # Fenêtre de 15 minutes
        
        # Erreurs
        'max_consecutive_errors': 5,       # 5 erreurs consécutives max
        'max_errors_in_hour': 20,          # 20 erreurs max par heure
        
        # Exchanges
        'max_exchange_downtime_minutes': 5, # 5 min max indisponible
        
        # Balance
        'min_balance_threshold_pct': 50,   # Alerte si < 50% balance initiale
        
        # Auto-reset
        'auto_reset_minutes': 60,          # Reset auto après 60 min
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le circuit breaker
        
        Args:
            config: Configuration personnalisée (optionnel)
        """
        self.logger = get_logger(__name__)
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        
        # État du circuit
        self.is_tripped = False
        self.trip_reason = None
        self.trip_time = None
        
        # Historique des pertes
        self.loss_history = []  # [(timestamp, amount), ...]
        
        # Historique des erreurs
        self.error_history = []  # [(timestamp, error_type), ...]
        self.consecutive_errors = 0
        
        # État des exchanges
        self.exchange_status = {}  # {exchange: (is_up, last_check)}
        
        # Balance initiale
        self.initial_balance = None
        self.current_balance = None
        
        self.logger.info(
            "CircuitBreaker initialisé",
            extra={'context': self.config}
        )
    
    def is_open(self) -> bool:
        """
        Vérifie si le circuit est ouvert (trading arrêté)
        
        Returns:
            True si circuit ouvert (trading arrêté)
        """
        # Vérifier auto-reset
        if self.is_tripped and self._should_auto_reset():
            self._reset("Auto-reset après délai de sécurité")
        
        return self.is_tripped
    
    def check_and_trip(
        self,
        loss_usd: float = None,
        error_occurred: bool = False,
        error_type: str = None,
        exchange_down: str = None,
        current_balance: float = None
    ) -> bool:
        """
        Vérifie les conditions et déclenche si nécessaire
        
        Args:
            loss_usd: Perte enregistrée (optionnel)
            error_occurred: Une erreur s'est produite
            error_type: Type d'erreur (optionnel)
            exchange_down: Exchange indisponible (optionnel)
            current_balance: Balance actuelle (optionnel)
        
        Returns:
            True si circuit déclenché
        """
        # Déjà ouvert
        if self.is_tripped:
            return True
        
        now = datetime.now()
        
        # 1. Vérifier pertes récentes
        if loss_usd and loss_usd > 0:
            self.loss_history.append((now, loss_usd))
            self._cleanup_old_losses()
            
            total_recent_loss = sum(loss for _, loss in self.loss_history)
            
            if total_recent_loss >= self.config['max_loss_in_minutes']:
                self._trip(
                    f"Perte de ${total_recent_loss:.2f} en {self.config['loss_window_minutes']} minutes "
                    f"(max: ${self.config['max_loss_in_minutes']:.2f})"
                )
                return True
        
        # 2. Vérifier erreurs
        if error_occurred:
            self.error_history.append((now, error_type or 'unknown'))
            self.consecutive_errors += 1
            
            # Erreurs consécutives
            if self.consecutive_errors >= self.config['max_consecutive_errors']:
                self._trip(
                    f"{self.consecutive_errors} erreurs consécutives "
                    f"(max: {self.config['max_consecutive_errors']})"
                )
                return True
            
            # Erreurs dans l'heure
            self._cleanup_old_errors()
            errors_in_hour = len(self.error_history)
            
            if errors_in_hour >= self.config['max_errors_in_hour']:
                self._trip(
                    f"{errors_in_hour} erreurs dans la dernière heure "
                    f"(max: {self.config['max_errors_in_hour']})"
                )
                return True
        else:
            # Reset erreurs consécutives si succès
            self.consecutive_errors = 0
        
        # 3. Vérifier exchange down
        if exchange_down:
            self.exchange_status[exchange_down] = (False, now)
            
            # Vérifier durée d'indisponibilité
            first_down_time = self.exchange_status[exchange_down][1]
            downtime_minutes = (now - first_down_time).total_seconds() / 60
            
            if downtime_minutes >= self.config['max_exchange_downtime_minutes']:
                self._trip(
                    f"Exchange {exchange_down} indisponible depuis {downtime_minutes:.1f} minutes "
                    f"(max: {self.config['max_exchange_downtime_minutes']})"
                )
                return True
        
        # 4. Vérifier balance
        if current_balance is not None:
            self.current_balance = current_balance
            
            if self.initial_balance is None:
                self.initial_balance = current_balance
            else:
                balance_pct = (current_balance / self.initial_balance) * 100
                
                if balance_pct < self.config['min_balance_threshold_pct']:
                    self._trip(
                        f"Balance à {balance_pct:.1f}% du capital initial "
                        f"(min: {self.config['min_balance_threshold_pct']}%)"
                    )
                    return True
        
        return False
    
    def _trip(self, reason: str):
        """
        Déclenche le circuit breaker
        
        Args:
            reason: Raison du déclenchement
        """
        self.is_tripped = True
        self.trip_reason = reason
        self.trip_time = datetime.now()
        
        self.logger.error(
            f"🚨 CIRCUIT BREAKER DÉCLENCHÉ: {reason}",
            extra={'context': {
                'reason': reason,
                'time': str(self.trip_time)
            }}
        )
        
        # TODO: Envoyer alerte (email, telegram, etc.)
    
    def _reset(self, reason: str = "Manuel"):
        """
        Reset le circuit breaker
        
        Args:
            reason: Raison du reset
        """
        self.is_tripped = False
        old_reason = self.trip_reason
        self.trip_reason = None
        self.trip_time = None
        
        self.logger.info(
            f"✅ Circuit breaker réinitialisé ({reason})",
            extra={'context': {
                'old_reason': old_reason,
                'reset_reason': reason
            }}
        )
    
    def reset(self):
        """Reset manuel du circuit breaker"""
        if self.is_tripped:
            self._reset("Reset manuel")
        else:
            self.logger.warning("Circuit breaker déjà fermé")
    
    def _should_auto_reset(self) -> bool:
        """
        Vérifie si auto-reset doit se faire
        
        Returns:
            True si auto-reset doit se faire
        """
        if not self.is_tripped or not self.trip_time:
            return False
        
        elapsed = datetime.now() - self.trip_time
        elapsed_minutes = elapsed.total_seconds() / 60
        
        return elapsed_minutes >= self.config['auto_reset_minutes']
    
    def _cleanup_old_losses(self):
        """Nettoie les pertes anciennes (> fenêtre)"""
        cutoff = datetime.now() - timedelta(minutes=self.config['loss_window_minutes'])
        self.loss_history = [(t, loss) for t, loss in self.loss_history if t >= cutoff]
    
    def _cleanup_old_errors(self):
        """Nettoie les erreurs anciennes (> 1 heure)"""
        cutoff = datetime.now() - timedelta(hours=1)
        self.error_history = [(t, err) for t, err in self.error_history if t >= cutoff]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Récupère le statut complet du circuit breaker
        
        Returns:
            Dict avec le statut
        """
        self._cleanup_old_losses()
        self._cleanup_old_errors()
        
        total_recent_loss = sum(loss for _, loss in self.loss_history)
        errors_in_hour = len(self.error_history)
        
        status = {
            'is_open': self.is_tripped,
            'trip_reason': self.trip_reason,
            'trip_time': str(self.trip_time) if self.trip_time else None,
            
            'recent_loss_usd': total_recent_loss,
            'consecutive_errors': self.consecutive_errors,
            'errors_in_hour': errors_in_hour,
            
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'balance_pct': ((self.current_balance / self.initial_balance) * 100) if self.initial_balance else None,
        }
        
        return status
    
    def display_status(self):
        """Affiche le statut de façon lisible"""
        status = self.get_status()
        
        print("\n" + "=" * 60)
        print("  CIRCUIT BREAKER STATUS")
        print("=" * 60)
        
        state = "🚨 OUVERT (TRADING ARRÊTÉ)" if status['is_open'] else "✅ FERMÉ (TRADING ACTIF)"
        print(f"\nÉtat: {state}")
        
        if status['is_open']:
            print(f"\n🚨 RAISON:")
            print(f"  {status['trip_reason']}")
            print(f"  Déclenché à: {status['trip_time']}")
        
        print(f"\n📊 MÉTRIQUES:")
        print(f"  Perte récente ({self.config['loss_window_minutes']}min): ${status['recent_loss_usd']:.2f}")
        print(f"  Erreurs consécutives: {status['consecutive_errors']}")
        print(f"  Erreurs dernière heure: {status['errors_in_hour']}")
        
        if status['balance_pct']:
            print(f"\n💰 BALANCE:")
            print(f"  Initiale: ${status['initial_balance']:.2f}")
            print(f"  Actuelle: ${status['current_balance']:.2f}")
            print(f"  % restant: {status['balance_pct']:.1f}%")
        
        print("\n" + "=" * 60)
    
    def __repr__(self):
        """Représentation textuelle"""
        state = "OPEN" if self.is_tripped else "CLOSED"
        return f"<CircuitBreaker(state={state})>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST CIRCUIT BREAKER")
    print("=" * 60)
    
    # Créer le circuit breaker
    cb = CircuitBreaker()
    cb.initial_balance = 5000.0
    cb.current_balance = 5000.0
    
    print("\n📊 État initial:")
    cb.display_status()
    
    # Simuler des pertes
    print("\n📊 Simulation de pertes:")
    for i in range(3):
        cb.check_and_trip(loss_usd=40.0)
        print(f"  Perte #{i+1}: $40")
        if cb.is_open():
            print("  🚨 CIRCUIT DÉCLENCHÉ!")
            break
    
    # Statut final
    print("\n📊 État final:")
    cb.display_status()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
