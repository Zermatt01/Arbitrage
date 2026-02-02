"""
Dry-Run Executor - Simulation de Trading
=========================================

Simule l'exécution complète des trades sans argent réel.

Usage:
    from src.execution.dry_run_executor import DryRunExecutor
    
    executor = DryRunExecutor(initial_balance=10000.0)
    
    # Exécuter un trade simulé
    result = executor.execute_arbitrage(opportunity)
    
    if result['success']:
        print(f"✅ Profit: ${result['profit_usd']:.2f}")
"""

from typing import Dict, Any, Optional
from datetime import datetime
import random
import time
from src.utils.logger import get_logger
from src.database.db_connection import get_db_connection


class DryRunExecutor:
    """
    Exécute des trades en mode simulation (dry-run)
    
    Fonctionnalités :
    - Simule l'exécution complète
    - Calcule profit/perte théorique
    - Simule slippage et latence
    - Enregistre en DB avec flag dry_run
    - Suit les balances virtuelles
    - Ne place JAMAIS d'ordres réels
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialise le dry-run executor
        
        Args:
            initial_balance: Balance virtuelle initiale
        """
        self.logger = get_logger(__name__)
        
        # Balance virtuelle
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # Statistiques
        self.trades_executed = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        
        # Historique
        self.trade_history = []
        
        self.logger.info(
            "DryRunExecutor initialisé (MODE SIMULATION)",
            extra={'context': {
                'initial_balance': initial_balance,
                'dry_run': True
            }}
        )
    
    def execute_arbitrage(
        self,
        opportunity: Dict[str, Any],
        trade_amount_usd: float = None
    ) -> Dict[str, Any]:
        """
        Exécute un arbitrage en mode simulation
        
        Args:
            opportunity: Opportunité d'arbitrage
            trade_amount_usd: Montant à trader (optionnel)
        
        Returns:
            Dict avec résultats de la simulation
        """
        start_time = time.time()
        
        # Extraire les infos
        symbol = opportunity.get('symbol', 'UNKNOWN')
        exchange_buy = opportunity.get('exchange_buy', 'unknown')
        exchange_sell = opportunity.get('exchange_sell', 'unknown')
        buy_price = opportunity.get('buy_price', 0)
        sell_price = opportunity.get('sell_price', 0)
        
        # Montant par défaut
        if trade_amount_usd is None:
            trade_amount_usd = 100.0
        
        # Vérifier balance suffisante
        if trade_amount_usd > self.current_balance:
            self.logger.warning(
                f"Balance insuffisante: ${trade_amount_usd:.2f} > ${self.current_balance:.2f}",
                extra={'context': {'required': trade_amount_usd, 'available': self.current_balance}}
            )
            return {
                'success': False,
                'error': 'Insufficient balance',
                'balance': self.current_balance
            }
        
        # SIMULATION D'ACHAT
        self.logger.info(
            f"[DRY-RUN] 1/3 - Achat {symbol} sur {exchange_buy}",
            extra={'context': {
                'symbol': symbol,
                'exchange': exchange_buy,
                'price': buy_price,
                'amount_usd': trade_amount_usd
            }}
        )
        
        # Simuler latence d'achat (50-200ms)
        time.sleep(random.uniform(0.05, 0.2))
        
        # Calculer quantité achetée
        buy_quantity = trade_amount_usd / buy_price
        
        # Simuler slippage à l'achat (0-0.2%)
        buy_slippage_pct = random.uniform(0, 0.2)
        actual_buy_price = buy_price * (1 + buy_slippage_pct / 100)
        actual_buy_cost = buy_quantity * actual_buy_price
        
        # SIMULATION DE TRANSFERT (si nécessaire)
        if exchange_buy != exchange_sell:
            self.logger.info(
                f"[DRY-RUN] 2/3 - Transfert vers {exchange_sell}",
                extra={'context': {
                    'from': exchange_buy,
                    'to': exchange_sell,
                    'quantity': buy_quantity
                }}
            )
            
            # Simuler latence de transfert (1-3s)
            time.sleep(random.uniform(0.1, 0.3))
        
        # SIMULATION DE VENTE
        self.logger.info(
            f"[DRY-RUN] 3/3 - Vente {symbol} sur {exchange_sell}",
            extra={'context': {
                'symbol': symbol,
                'exchange': exchange_sell,
                'price': sell_price,
                'quantity': buy_quantity
            }}
        )
        
        # Simuler latence de vente (50-200ms)
        time.sleep(random.uniform(0.05, 0.2))
        
        # Simuler slippage à la vente (0-0.2%)
        sell_slippage_pct = random.uniform(0, 0.2)
        actual_sell_price = sell_price * (1 - sell_slippage_pct / 100)
        actual_sell_revenue = buy_quantity * actual_sell_price
        
        # CALCUL DES FRAIS
        # Frais d'achat (0.1% typique)
        buy_fee_pct = opportunity.get('buy_fee_pct', 0.1)
        buy_fee = actual_buy_cost * (buy_fee_pct / 100)
        
        # Frais de vente (0.1% typique)
        sell_fee_pct = opportunity.get('sell_fee_pct', 0.1)
        sell_fee = actual_sell_revenue * (sell_fee_pct / 100)
        
        total_fees = buy_fee + sell_fee
        
        # CALCUL DU PROFIT/PERTE NET
        gross_profit = actual_sell_revenue - actual_buy_cost
        net_profit = gross_profit - total_fees
        net_profit_pct = (net_profit / actual_buy_cost) * 100
        
        # Temps total d'exécution
        execution_time = time.time() - start_time
        
        # METTRE À JOUR LA BALANCE
        old_balance = self.current_balance
        self.current_balance += net_profit
        
        # Statistiques
        self.trades_executed += 1
        if net_profit > 0:
            self.total_profit += net_profit
        else:
            self.total_loss += abs(net_profit)
        
        # Résultat complet
        result = {
            'success': True,
            'dry_run': True,
            'timestamp': datetime.now().isoformat(),
            
            # Trade info
            'symbol': symbol,
            'exchange_buy': exchange_buy,
            'exchange_sell': exchange_sell,
            
            # Prix
            'expected_buy_price': buy_price,
            'actual_buy_price': actual_buy_price,
            'expected_sell_price': sell_price,
            'actual_sell_price': actual_sell_price,
            
            # Quantités
            'quantity': buy_quantity,
            'trade_amount_usd': trade_amount_usd,
            
            # Slippage
            'buy_slippage_pct': buy_slippage_pct,
            'sell_slippage_pct': sell_slippage_pct,
            'total_slippage_pct': buy_slippage_pct + sell_slippage_pct,
            
            # Frais
            'buy_fee': buy_fee,
            'sell_fee': sell_fee,
            'total_fees': total_fees,
            
            # Profit
            'gross_profit_usd': gross_profit,
            'net_profit_usd': net_profit,
            'net_profit_pct': net_profit_pct,
            
            # Performance
            'execution_time_seconds': execution_time,
            
            # Balance
            'balance_before': old_balance,
            'balance_after': self.current_balance,
        }
        
        # Logger le résultat
        profit_symbol = "+" if net_profit >= 0 else ""
        self.logger.info(
            f"[DRY-RUN] ✅ Trade complété: {profit_symbol}${net_profit:.2f} "
            f"({net_profit_pct:+.2f}%) en {execution_time:.2f}s",
            extra={'context': result}
        )
        
        # Sauvegarder dans l'historique
        self.trade_history.append(result)
        
        # Sauvegarder en DB
        self._save_to_db(result)
        
        return result
    
    def _save_to_db(self, trade_result: Dict[str, Any]) -> bool:
        """
        Sauvegarde le trade simulé en DB
        
        Args:
            trade_result: Résultat du trade
        
        Returns:
            True si succès
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO trades (
                    symbol,
                    exchange_buy,
                    exchange_sell,
                    buy_price,
                    sell_price,
                    quantity,
                    gross_profit_usd,
                    net_profit_usd,
                    total_fees_usd,
                    execution_time_seconds,
                    dry_run,
                    metadata,
                    executed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """
            
            # Métadonnées JSON
            import json
            metadata = {
                'buy_slippage_pct': trade_result['buy_slippage_pct'],
                'sell_slippage_pct': trade_result['sell_slippage_pct'],
                'balance_before': trade_result['balance_before'],
                'balance_after': trade_result['balance_after'],
            }
            
            cursor.execute(query, (
                trade_result['symbol'],
                trade_result['exchange_buy'],
                trade_result['exchange_sell'],
                trade_result['actual_buy_price'],
                trade_result['actual_sell_price'],
                trade_result['quantity'],
                trade_result['gross_profit_usd'],
                trade_result['net_profit_usd'],
                trade_result['total_fees'],
                trade_result['execution_time_seconds'],
                True,  # dry_run
                json.dumps(metadata)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            self.logger.debug("Trade sauvegardé en DB")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde trade: {e}", exc_info=True)
            return False
    
    def get_balance(self) -> float:
        """
        Retourne la balance virtuelle actuelle
        
        Returns:
            Balance en USD
        """
        return self.current_balance
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de simulation
        
        Returns:
            Dict avec les stats
        """
        win_count = sum(1 for t in self.trade_history if t['net_profit_usd'] > 0)
        loss_count = sum(1 for t in self.trade_history if t['net_profit_usd'] <= 0)
        
        net_pnl = self.current_balance - self.initial_balance
        roi_pct = (net_pnl / self.initial_balance) * 100 if self.initial_balance > 0 else 0
        
        stats = {
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'net_pnl': net_pnl,
            'roi_pct': roi_pct,
            
            'trades_executed': self.trades_executed,
            'wins': win_count,
            'losses': loss_count,
            'win_rate_pct': (win_count / self.trades_executed * 100) if self.trades_executed > 0 else 0,
            
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            
            'avg_profit': self.total_profit / win_count if win_count > 0 else 0,
            'avg_loss': self.total_loss / loss_count if loss_count > 0 else 0,
        }
        
        return stats
    
    def display_statistics(self):
        """Affiche les statistiques de façon lisible"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("  STATISTIQUES DRY-RUN")
        print("=" * 60)
        
        print(f"\n💰 BALANCE:")
        print(f"  Initiale:          ${stats['initial_balance']:,.2f}")
        print(f"  Actuelle:          ${stats['current_balance']:,.2f}")
        
        pnl_symbol = "+" if stats['net_pnl'] >= 0 else ""
        print(f"  PnL:               {pnl_symbol}${stats['net_pnl']:,.2f} ({stats['roi_pct']:+.2f}%)")
        
        print(f"\n📊 TRADES:")
        print(f"  Total:             {stats['trades_executed']}")
        print(f"  Gagnants:          {stats['wins']} ({stats['win_rate_pct']:.1f}%)")
        print(f"  Perdants:          {stats['losses']}")
        
        print(f"\n💹 PROFIT/PERTE:")
        print(f"  Total profit:      +${stats['total_profit']:.2f}")
        print(f"  Total perte:       -${stats['total_loss']:.2f}")
        print(f"  Profit moyen:      +${stats['avg_profit']:.2f}")
        print(f"  Perte moyenne:     -${stats['avg_loss']:.2f}")
        
        print("\n" + "=" * 60)
    
    def reset(self):
        """Réinitialise le simulateur"""
        self.current_balance = self.initial_balance
        self.trades_executed = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.trade_history = []
        
        self.logger.info("DryRunExecutor réinitialisé")
    
    def __repr__(self):
        """Représentation textuelle"""
        net_pnl = self.current_balance - self.initial_balance
        return f"<DryRunExecutor(balance=${self.current_balance:.2f}, pnl={net_pnl:+.2f}, trades={self.trades_executed})>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST DRY-RUN EXECUTOR")
    print("=" * 60)
    
    # Créer l'executor
    executor = DryRunExecutor(initial_balance=10000.0)
    
    # Opportunité de test
    opportunity = {
        'symbol': 'BTC/USDT',
        'exchange_buy': 'binance',
        'exchange_sell': 'kraken',
        'buy_price': 50000.0,
        'sell_price': 50500.0,
        'buy_fee_pct': 0.1,
        'sell_fee_pct': 0.1,
    }
    
    # Exécuter quelques trades
    print("\n📊 Exécution de 3 trades:")
    for i in range(3):
        result = executor.execute_arbitrage(opportunity, trade_amount_usd=1000.0)
        if result['success']:
            print(f"\n  Trade {i+1}:")
            print(f"    Profit: ${result['net_profit_usd']:+.2f}")
            print(f"    Balance: ${result['balance_after']:,.2f}")
    
    # Statistiques
    print("\n📊 Statistiques finales:")
    executor.display_statistics()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
