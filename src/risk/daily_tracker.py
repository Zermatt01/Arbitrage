"""
Daily Tracker - Suivi de Performance Quotidienne
=================================================

Suit toutes les statistiques quotidiennes en temps réel et les sauvegarde.

Usage:
    from src.risk.daily_tracker import DailyTracker
    
    tracker = DailyTracker()
    tracker.record_trade(profit_usd=24.50, is_win=True)
    stats = tracker.get_stats()
"""

from typing import Dict, Any, Optional
from datetime import datetime, date
import psycopg2
from src.database.db_connection import get_db_connection
from src.utils.logger import get_logger


class DailyTracker:
    """
    Suit les statistiques quotidiennes en temps réel
    
    Métriques suivies :
    - Nombre de trades
    - Profit/perte total
    - Win rate
    - Meilleur trade
    - Pire trade
    - Trades consécutifs gagnants/perdants
    """
    
    def __init__(self):
        """Initialise le tracker"""
        self.logger = get_logger(__name__)
        
        # Date actuelle
        self.today = date.today()
        
        # Compteurs quotidiens
        self.trades_count = 0
        self.wins_count = 0
        self.losses_count = 0
        
        # Profit/perte
        self.total_profit_usd = 0.0
        self.total_loss_usd = 0.0
        
        # Meilleurs/pires trades
        self.best_trade_usd = 0.0
        self.worst_trade_usd = 0.0
        
        # Séries consécutives
        self.current_win_streak = 0
        self.current_loss_streak = 0
        self.max_win_streak = 0
        self.max_loss_streak = 0
        
        # Charger les stats du jour depuis la DB
        self._load_today_stats()
        
        self.logger.info(
            "DailyTracker initialisé",
            extra={'context': {
                'date': str(self.today),
                'trades': self.trades_count,
                'pnl': self.total_profit_usd - self.total_loss_usd
            }}
        )
    
    def _check_new_day(self):
        """Vérifie si on est un nouveau jour et reset si nécessaire"""
        today = date.today()
        
        if today > self.today:
            self.logger.info(
                f"Nouveau jour détecté - Sauvegarde et reset",
                extra={'context': {
                    'old_date': str(self.today),
                    'new_date': str(today),
                    'yesterday_trades': self.trades_count,
                    'yesterday_pnl': self.total_profit_usd - self.total_loss_usd
                }}
            )
            
            # Sauvegarder les stats d'hier
            self._save_to_db()
            
            # Reset pour aujourd'hui
            self.today = today
            self.trades_count = 0
            self.wins_count = 0
            self.losses_count = 0
            self.total_profit_usd = 0.0
            self.total_loss_usd = 0.0
            self.best_trade_usd = 0.0
            self.worst_trade_usd = 0.0
            self.current_win_streak = 0
            self.current_loss_streak = 0
            self.max_win_streak = 0
            self.max_loss_streak = 0
    
    def _load_today_stats(self) -> bool:
        """
        Charge les statistiques du jour depuis la DB
        
        Returns:
            True si stats chargées
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT
                    trades_count,
                    wins_count,
                    losses_count,
                    total_profit_usd,
                    total_loss_usd,
                    best_trade_usd,
                    worst_trade_usd,
                    max_win_streak,
                    max_loss_streak
                FROM daily_performance
                WHERE date = %s
            """
            
            cursor.execute(query, (self.today,))
            result = cursor.fetchone()
            
            if result:
                # Charger les stats existantes
                (self.trades_count, self.wins_count, self.losses_count,
                 self.total_profit_usd, self.total_loss_usd,
                 self.best_trade_usd, self.worst_trade_usd,
                 self.max_win_streak, self.max_loss_streak) = result
                
                self.logger.debug(
                    f"Stats du jour chargées: {self.trades_count} trades",
                    extra={'context': {'date': str(self.today)}}
                )
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Impossible de charger les stats: {e}")
            return False
    
    def record_trade(
        self,
        profit_usd: float,
        is_win: bool,
        symbol: str = None,
        exchange_buy: str = None,
        exchange_sell: str = None
    ):
        """
        Enregistre un trade et met à jour les statistiques
        
        Args:
            profit_usd: Profit/perte en USD (positif = profit, négatif = perte)
            is_win: True si trade gagnant
            symbol: Symbole tradé (optionnel)
            exchange_buy: Exchange d'achat (optionnel)
            exchange_sell: Exchange de vente (optionnel)
        """
        self._check_new_day()
        
        # Incrémenter compteur
        self.trades_count += 1
        
        if is_win:
            self.wins_count += 1
            self.total_profit_usd += profit_usd
            
            # Meilleur trade
            if profit_usd > self.best_trade_usd:
                self.best_trade_usd = profit_usd
            
            # Séries
            self.current_win_streak += 1
            self.current_loss_streak = 0
            
            if self.current_win_streak > self.max_win_streak:
                self.max_win_streak = self.current_win_streak
            
            self.logger.info(
                f"✅ Trade gagnant #{self.trades_count}: +${profit_usd:.2f}",
                extra={'context': {
                    'profit': profit_usd,
                    'symbol': symbol,
                    'win_streak': self.current_win_streak
                }}
            )
        else:
            self.losses_count += 1
            self.total_loss_usd += abs(profit_usd)
            
            # Pire trade
            if profit_usd < self.worst_trade_usd:
                self.worst_trade_usd = profit_usd
            
            # Séries
            self.current_loss_streak += 1
            self.current_win_streak = 0
            
            if self.current_loss_streak > self.max_loss_streak:
                self.max_loss_streak = self.current_loss_streak
            
            self.logger.warning(
                f"❌ Trade perdant #{self.trades_count}: ${profit_usd:.2f}",
                extra={'context': {
                    'loss': profit_usd,
                    'symbol': symbol,
                    'loss_streak': self.current_loss_streak
                }}
            )
        
        # Sauvegarder en DB après chaque trade
        self._save_to_db()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques complètes
        
        Returns:
            Dict avec toutes les stats
        """
        self._check_new_day()
        
        # Calculer le PnL net
        net_pnl = self.total_profit_usd - self.total_loss_usd
        
        # Calculer le win rate
        win_rate = (self.wins_count / self.trades_count * 100) if self.trades_count > 0 else 0.0
        
        # Profit moyen par trade gagnant
        avg_win = (self.total_profit_usd / self.wins_count) if self.wins_count > 0 else 0.0
        
        # Perte moyenne par trade perdant
        avg_loss = (self.total_loss_usd / self.losses_count) if self.losses_count > 0 else 0.0
        
        # Ratio profit/perte
        profit_loss_ratio = (avg_win / avg_loss) if avg_loss > 0 else 0.0
        
        stats = {
            'date': str(self.today),
            'trades_count': self.trades_count,
            'wins_count': self.wins_count,
            'losses_count': self.losses_count,
            'win_rate_pct': win_rate,
            
            'total_profit_usd': self.total_profit_usd,
            'total_loss_usd': self.total_loss_usd,
            'net_pnl_usd': net_pnl,
            
            'best_trade_usd': self.best_trade_usd,
            'worst_trade_usd': self.worst_trade_usd,
            
            'avg_win_usd': avg_win,
            'avg_loss_usd': avg_loss,
            'profit_loss_ratio': profit_loss_ratio,
            
            'current_win_streak': self.current_win_streak,
            'current_loss_streak': self.current_loss_streak,
            'max_win_streak': self.max_win_streak,
            'max_loss_streak': self.max_loss_streak,
        }
        
        return stats
    
    def _save_to_db(self) -> bool:
        """
        Sauvegarde les stats du jour en DB
        
        Returns:
            True si succès
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Calculer le PnL net
            net_pnl = self.total_profit_usd - self.total_loss_usd
            
            # Calculer le win rate
            win_rate = (self.wins_count / self.trades_count * 100) if self.trades_count > 0 else 0.0
            
            # Upsert (insert ou update)
            query = """
                INSERT INTO daily_performance (
                    date,
                    trades_count,
                    wins_count,
                    losses_count,
                    win_rate_pct,
                    total_profit_usd,
                    total_loss_usd,
                    net_pnl_usd,
                    best_trade_usd,
                    worst_trade_usd,
                    max_win_streak,
                    max_loss_streak,
                    updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
                ON CONFLICT (date)
                DO UPDATE SET
                    trades_count = EXCLUDED.trades_count,
                    wins_count = EXCLUDED.wins_count,
                    losses_count = EXCLUDED.losses_count,
                    win_rate_pct = EXCLUDED.win_rate_pct,
                    total_profit_usd = EXCLUDED.total_profit_usd,
                    total_loss_usd = EXCLUDED.total_loss_usd,
                    net_pnl_usd = EXCLUDED.net_pnl_usd,
                    best_trade_usd = EXCLUDED.best_trade_usd,
                    worst_trade_usd = EXCLUDED.worst_trade_usd,
                    max_win_streak = EXCLUDED.max_win_streak,
                    max_loss_streak = EXCLUDED.max_loss_streak,
                    updated_at = NOW()
            """
            
            cursor.execute(query, (
                self.today,
                self.trades_count,
                self.wins_count,
                self.losses_count,
                win_rate,
                self.total_profit_usd,
                self.total_loss_usd,
                net_pnl,
                self.best_trade_usd,
                self.worst_trade_usd,
                self.max_win_streak,
                self.max_loss_streak
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            self.logger.debug(
                f"Stats sauvegardées en DB",
                extra={'context': {'date': str(self.today), 'trades': self.trades_count}}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde stats: {e}", exc_info=True)
            return False
    
    def display_stats(self):
        """Affiche les statistiques de façon lisible"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print(f"  PERFORMANCE DU {stats['date']}")
        print("=" * 60)
        
        print(f"\n📊 TRADES:")
        print(f"  Total:             {stats['trades_count']}")
        print(f"  Gagnants:          {stats['wins_count']} ({stats['win_rate_pct']:.1f}%)")
        print(f"  Perdants:          {stats['losses_count']}")
        
        print(f"\n💰 PROFIT/PERTE:")
        print(f"  Total profit:      +${stats['total_profit_usd']:.2f}")
        print(f"  Total perte:       -${stats['total_loss_usd']:.2f}")
        
        pnl_symbol = "+" if stats['net_pnl_usd'] >= 0 else ""
        print(f"  NET:               {pnl_symbol}${stats['net_pnl_usd']:.2f}")
        
        print(f"\n🏆 MEILLEURS/PIRES:")
        print(f"  Meilleur trade:    +${stats['best_trade_usd']:.2f}")
        print(f"  Pire trade:        ${stats['worst_trade_usd']:.2f}")
        
        print(f"\n📈 MOYENNES:")
        print(f"  Avg profit/trade:  +${stats['avg_win_usd']:.2f}")
        print(f"  Avg perte/trade:   -${stats['avg_loss_usd']:.2f}")
        print(f"  Ratio P/L:         {stats['profit_loss_ratio']:.2f}x")
        
        print(f"\n🔥 SÉRIES:")
        print(f"  Wins actuels:      {stats['current_win_streak']}")
        print(f"  Pertes actuelles:  {stats['current_loss_streak']}")
        print(f"  Max wins:          {stats['max_win_streak']}")
        print(f"  Max pertes:        {stats['max_loss_streak']}")
        
        print("\n" + "=" * 60)
    
    def reset_stats(self):
        """Force le reset des stats (pour tests)"""
        self.trades_count = 0
        self.wins_count = 0
        self.losses_count = 0
        self.total_profit_usd = 0.0
        self.total_loss_usd = 0.0
        self.best_trade_usd = 0.0
        self.worst_trade_usd = 0.0
        self.current_win_streak = 0
        self.current_loss_streak = 0
        self.max_win_streak = 0
        self.max_loss_streak = 0
        
        self.logger.info("Statistiques réinitialisées")
    
    def __repr__(self):
        """Représentation textuelle"""
        net_pnl = self.total_profit_usd - self.total_loss_usd
        return f"<DailyTracker(trades={self.trades_count}, pnl=${net_pnl:.2f})>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST DAILY TRACKER")
    print("=" * 60)
    
    # Créer le tracker
    tracker = DailyTracker()
    
    # Simuler des trades
    print("\n📊 Simulation de trades:")
    tracker.record_trade(24.50, True, 'BTC/USDT')
    tracker.record_trade(-12.00, False, 'ETH/USDT')
    tracker.record_trade(18.75, True, 'BTC/USDT')
    tracker.record_trade(32.00, True, 'SOL/USDT')
    tracker.record_trade(-8.50, False, 'XRP/USDT')
    
    # Afficher stats
    tracker.display_stats()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
