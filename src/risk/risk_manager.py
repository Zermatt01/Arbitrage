"""
Risk Manager - Validation Pre-Trade
====================================

Valide chaque trade avant exécution en vérifiant toutes les limites.

Usage:
    from src.risk.risk_manager import RiskManager
    
    rm = RiskManager()
    can_trade, reason = rm.can_trade(opportunity)
    if can_trade:
        print("✅ Trade autorisé")
    else:
        print(f"❌ Trade refusé: {reason}")
"""

from typing import Dict, Any, Tuple
from datetime import datetime, date
from src.risk.limits_config import LimitsConfig
from src.utils.logger import get_logger


class RiskManager:
    """
    Gère la validation de tous les trades avant exécution
    
    Vérifie :
    - Montants dans les limites
    - Nombre de trades quotidiens
    - Pertes quotidiennes
    - Balance suffisante
    - Score minimum
    - Profit minimum
    - Slippage maximum
    """
    
    def __init__(self, limits_config: LimitsConfig = None):
        """
        Initialise le Risk Manager
        
        Args:
            limits_config: Configuration des limites (optionnel)
        """
        self.logger = get_logger(__name__)
        self.limits = limits_config or LimitsConfig()
        
        # Compteurs quotidiens (réinitialisés chaque jour)
        self.today = date.today()
        self.daily_trades_count = 0
        self.daily_profit_loss = 0.0
        self.consecutive_losses = 0
        
        # Balances (à mettre à jour régulièrement)
        self.current_balance_usd = 0.0
        
        self.logger.info(
            "RiskManager initialisé",
            extra={'context': {
                'max_trade': self.limits.max_trade_amount,
                'max_daily': self.limits.max_daily_trades
            }}
        )
    
    def _check_new_day(self):
        """Vérifie si on est un nouveau jour et reset les compteurs"""
        today = date.today()
        
        if today > self.today:
            self.logger.info(
                f"Nouveau jour détecté - Reset des compteurs",
                extra={'context': {
                    'old_date': str(self.today),
                    'new_date': str(today),
                    'trades_yesterday': self.daily_trades_count,
                    'pnl_yesterday': self.daily_profit_loss
                }}
            )
            
            self.today = today
            self.daily_trades_count = 0
            self.daily_profit_loss = 0.0
            # Note: consecutive_losses ne se reset pas (volontaire)
    
    def update_balance(self, balance_usd: float):
        """
        Met à jour la balance actuelle
        
        Args:
            balance_usd: Balance en USD
        """
        old_balance = self.current_balance_usd
        self.current_balance_usd = balance_usd
        
        self.logger.debug(
            f"Balance mise à jour: ${balance_usd:.2f}",
            extra={'context': {
                'old_balance': old_balance,
                'new_balance': balance_usd
            }}
        )
    
    def can_trade(
        self,
        opportunity: Dict[str, Any],
        trade_amount_usd: float = None
    ) -> Tuple[bool, str]:
        """
        Vérifie si un trade peut être exécuté
        
        Args:
            opportunity: Opportunité à valider
            trade_amount_usd: Montant du trade (optionnel)
        
        Returns:
            (can_trade, reason) - True si OK, sinon False + raison
        
        Example:
            >>> rm = RiskManager()
            >>> can_trade, reason = rm.can_trade(opportunity, 100.0)
            >>> if can_trade:
            ...     execute_trade()
        """
        self._check_new_day()
        
        # Récupérer le montant
        if trade_amount_usd is None:
            trade_amount_usd = self.limits.max_trade_amount
        
        # 1. Vérifier montant minimum
        if trade_amount_usd < self.limits.min_trade_amount:
            reason = f"Montant trop faible: ${trade_amount_usd:.2f} < ${self.limits.min_trade_amount:.2f}"
            self.logger.warning(reason)
            return False, reason
        
        # 2. Vérifier montant maximum
        if trade_amount_usd > self.limits.max_trade_amount:
            reason = f"Montant trop élevé: ${trade_amount_usd:.2f} > ${self.limits.max_trade_amount:.2f}"
            self.logger.warning(reason)
            return False, reason
        
        # 3. Vérifier nombre de trades quotidiens
        if self.daily_trades_count >= self.limits.max_daily_trades:
            reason = f"Limite quotidienne atteinte: {self.daily_trades_count}/{self.limits.max_daily_trades} trades"
            self.logger.warning(reason)
            return False, reason
        
        # 4. Vérifier pertes quotidiennes
        if self.daily_profit_loss <= -self.limits.max_daily_loss:
            reason = f"Perte quotidienne max atteinte: ${self.daily_profit_loss:.2f}"
            self.logger.warning(reason)
            return False, reason
        
        # 5. Vérifier pertes consécutives
        if self.consecutive_losses >= self.limits.max_consecutive_losses:
            reason = f"Trop de pertes consécutives: {self.consecutive_losses}"
            self.logger.warning(reason)
            return False, reason
        
        # 6. Vérifier balance suffisante
        if self.current_balance_usd > 0:
            if self.current_balance_usd < self.limits.min_balance_usd:
                reason = f"Balance insuffisante: ${self.current_balance_usd:.2f} < ${self.limits.min_balance_usd:.2f}"
                self.logger.warning(reason)
                return False, reason
            
            # Vérifier qu'on ne trade pas tout le capital
            reserved = self.current_balance_usd * (self.limits.reserve_pct / 100.0)
            available = self.current_balance_usd - reserved
            
            if trade_amount_usd > available:
                reason = f"Trade dépasse le capital disponible: ${trade_amount_usd:.2f} > ${available:.2f} (réserve: {self.limits.reserve_pct}%)"
                self.logger.warning(reason)
                return False, reason
        
        # 7. Vérifier profit minimum (si disponible)
        net_profit_pct = opportunity.get('net_profit_pct', 
                                        opportunity.get('net_profit_real_pct', 0))
        
        if net_profit_pct < self.limits.min_profit_pct:
            reason = f"Profit insuffisant: {net_profit_pct:.2f}% < {self.limits.min_profit_pct:.2f}%"
            self.logger.warning(reason)
            return False, reason
        
        # 8. Vérifier score minimum (si disponible)
        total_score = opportunity.get('total_score', 100)
        
        if total_score < self.limits.min_score:
            reason = f"Score trop faible: {total_score:.1f}/100 < {self.limits.min_score:.1f}/100"
            self.logger.warning(reason)
            return False, reason
        
        # 9. Vérifier slippage (si disponible)
        total_slippage = opportunity.get('total_slippage_pct', 0)
        
        if total_slippage > self.limits.max_slippage_pct:
            reason = f"Slippage trop élevé: {total_slippage:.2f}% > {self.limits.max_slippage_pct:.2f}%"
            self.logger.warning(reason)
            return False, reason
        
        # 10. Vérifier liquidité (si disponible)
        liquidity_valid = opportunity.get('liquidity_valid', True)
        
        if not liquidity_valid:
            reason = "Liquidité insuffisante"
            self.logger.warning(reason)
            return False, reason
        
        # ✅ Tous les checks passés
        self.logger.info(
            f"Trade validé: {opportunity.get('symbol', 'UNKNOWN')} "
            f"{opportunity.get('exchange_buy', '')}→{opportunity.get('exchange_sell', '')} "
            f"${trade_amount_usd:.2f}",
            extra={'context': {
                'symbol': opportunity.get('symbol'),
                'amount': trade_amount_usd,
                'profit_pct': net_profit_pct,
                'score': total_score
            }}
        )
        
        return True, "OK"
    
    def record_trade_result(
        self,
        profit_loss_usd: float,
        is_profit: bool
    ):
        """
        Enregistre le résultat d'un trade
        
        Args:
            profit_loss_usd: Profit/perte en USD
            is_profit: True si profit, False si perte
        """
        self._check_new_day()
        
        # Mettre à jour les compteurs
        self.daily_trades_count += 1
        self.daily_profit_loss += profit_loss_usd
        
        if is_profit:
            self.consecutive_losses = 0
            self.logger.info(
                f"✅ Trade profitable: +${profit_loss_usd:.2f}",
                extra={'context': {
                    'profit': profit_loss_usd,
                    'daily_pnl': self.daily_profit_loss,
                    'daily_trades': self.daily_trades_count
                }}
            )
        else:
            self.consecutive_losses += 1
            self.logger.warning(
                f"❌ Trade perdant: -${abs(profit_loss_usd):.2f} "
                f"(consécutives: {self.consecutive_losses})",
                extra={'context': {
                    'loss': profit_loss_usd,
                    'consecutive': self.consecutive_losses,
                    'daily_pnl': self.daily_profit_loss,
                    'daily_trades': self.daily_trades_count
                }}
            )
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques quotidiennes
        
        Returns:
            Dict avec les stats du jour
        """
        self._check_new_day()
        
        # Calculer les limites restantes
        trades_remaining = max(0, self.limits.max_daily_trades - self.daily_trades_count)
        loss_remaining = max(0, self.limits.max_daily_loss + self.daily_profit_loss)
        
        stats = {
            'date': str(self.today),
            'trades_count': self.daily_trades_count,
            'trades_remaining': trades_remaining,
            'profit_loss_usd': self.daily_profit_loss,
            'loss_remaining_usd': loss_remaining,
            'consecutive_losses': self.consecutive_losses,
            'current_balance_usd': self.current_balance_usd,
        }
        
        return stats
    
    def reset_daily_stats(self):
        """Force le reset des statistiques quotidiennes (pour tests)"""
        self.daily_trades_count = 0
        self.daily_profit_loss = 0.0
        self.consecutive_losses = 0
        
        self.logger.info("Statistiques quotidiennes réinitialisées")
    
    def __repr__(self):
        """Représentation textuelle"""
        return (f"<RiskManager(trades={self.daily_trades_count}/{self.limits.max_daily_trades}, "
                f"pnl=${self.daily_profit_loss:.2f})>")


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST RISK MANAGER")
    print("=" * 60)
    
    # Créer le risk manager
    rm = RiskManager()
    rm.update_balance(5000.0)  # $5000 de capital
    
    # Opportunité de test
    opportunity = {
        'symbol': 'BTC/USDT',
        'exchange_buy': 'binance',
        'exchange_sell': 'kraken',
        'net_profit_pct': 0.8,
        'total_score': 87.5,
        'total_slippage_pct': 0.1,
        'liquidity_valid': True
    }
    
    # Test 1: Trade normal
    print("\n📊 Test 1: Trade normal ($100)")
    can_trade, reason = rm.can_trade(opportunity, 100.0)
    print(f"   Résultat: {can_trade}")
    print(f"   Raison: {reason}")
    
    # Test 2: Montant trop élevé
    print("\n📊 Test 2: Montant trop élevé ($500)")
    can_trade, reason = rm.can_trade(opportunity, 500.0)
    print(f"   Résultat: {can_trade}")
    print(f"   Raison: {reason}")
    
    # Test 3: Enregistrer des trades
    print("\n📊 Test 3: Enregistrement de trades")
    rm.record_trade_result(24.50, True)   # Profit
    rm.record_trade_result(-12.00, False) # Perte
    rm.record_trade_result(18.75, True)   # Profit
    
    # Stats
    print("\n📊 Statistiques quotidiennes:")
    stats = rm.get_daily_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
