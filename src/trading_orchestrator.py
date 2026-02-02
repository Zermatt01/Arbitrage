"""
Trading Orchestrator - Version Ultra-Compatible
================================================

Version simplifiée qui s'adapte aux fichiers existants.
"""

from typing import Dict, Any, List
import time
from datetime import datetime
from src.utils.logger import get_logger
from src.collectors.price_collector import PriceCollector
from src.risk.risk_manager import RiskManager
from src.risk.circuit_breaker import CircuitBreaker
from src.risk.daily_tracker import DailyTracker
from src.risk.error_handler import ErrorHandler
from src.execution.dry_run_executor import DryRunExecutor


class TradingOrchestrator:
    """Orchestrateur simplifié et ultra-compatible"""
    
    def __init__(
        self,
        dry_run: bool = True,
        initial_balance: float = 10000.0,
        exchange_names: List[str] = None,
        config: Dict[str, Any] = None
    ):
        self.logger = get_logger(__name__)
        self.dry_run = dry_run
        self.config = config or {}
        
        # Exchanges
        if exchange_names is None:
            exchange_names = ['binance', 'kraken']
        self.exchange_names = exchange_names
        
        # État
        self.is_running = False
        self.start_time = None
        self.cycle_count = 0
        
        # Composants
        self.logger.info("Initialisation des composants...")
        
        try:
            self.price_collector = PriceCollector(exchange_names=self.exchange_names)
        except Exception as e:
            self.logger.error(f"Erreur init PriceCollector: {e}")
            raise
        
        try:
            self.risk_manager = RiskManager()
            if hasattr(self.risk_manager, 'update_balance'):
                self.risk_manager.update_balance(initial_balance)
        except Exception as e:
            self.logger.error(f"Erreur init RiskManager: {e}")
            self.risk_manager = None
        
        try:
            self.circuit_breaker = CircuitBreaker()
        except Exception as e:
            self.logger.error(f"Erreur init CircuitBreaker: {e}")
            self.circuit_breaker = None
        
        try:
            self.daily_tracker = DailyTracker()
        except Exception as e:
            self.logger.error(f"Erreur init DailyTracker: {e}")
            self.daily_tracker = None
        
        try:
            self.error_handler = ErrorHandler(circuit_breaker=self.circuit_breaker)
        except Exception as e:
            self.logger.warning(f"Erreur init ErrorHandler: {e}")
            self.error_handler = None
        
        try:
            self.executor = DryRunExecutor(initial_balance=initial_balance)
            self.logger.warning("🎮 MODE DRY-RUN ACTIVÉ - AUCUN TRADE RÉEL")
        except Exception as e:
            self.logger.error(f"Erreur init Executor: {e}")
            raise
        
        # Stats
        self.stats = {
            'opportunities_detected': 0,
            'trades_executed': 0,
            'trades_skipped': 0,
            'errors_count': 0,
        }
        
        self.logger.info(
            "TradingOrchestrator initialisé",
            extra={'context': {'dry_run': dry_run, 'initial_balance': initial_balance}}
        )
    
    def run(
        self,
        duration_seconds: int = None,
        max_cycles: int = None,
        interval_seconds: float = 5.0
    ):
        """Lance le bot"""
        self.is_running = True
        self.start_time = datetime.now()
        
        self.logger.info(
            "🚀 Démarrage du bot",
            extra={'context': {
                'duration': duration_seconds,
                'max_cycles': max_cycles,
                'interval': interval_seconds
            }}
        )
        
        try:
            while self.is_running:
                # Conditions d'arrêt
                if self._should_stop(duration_seconds, max_cycles):
                    break
                
                # Circuit breaker
                if self.circuit_breaker and hasattr(self.circuit_breaker, 'is_open'):
                    if self.circuit_breaker.is_open():
                        reason = getattr(self.circuit_breaker, 'trip_reason', 'Unknown')
                        self.logger.error(f"⚠️ Circuit breaker ouvert: {reason}")
                        break
                
                # Exécuter cycle
                self._run_cycle()
                
                # Attendre
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            self.logger.info("⏸️ Arrêt manuel (Ctrl+C)")
        
        except Exception as e:
            self.logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        
        finally:
            self._shutdown()
    
    def _run_cycle(self):
        """Exécute un cycle"""
        self.cycle_count += 1
        self.logger.debug(f"--- Cycle #{self.cycle_count} ---")
        
        try:
            # 1. Collecter prix ET opportunités (collect_and_analyze fait tout)
            result = self._collect_prices()
            
            # Vérifier si des prix ont été collectés
            if not result.get('prices'):
                self.logger.debug("Aucun prix collecté")
                return
            
            # 2. Les opportunités sont déjà dans result
            opportunities = result.get('opportunities', [])
            self.stats['opportunities_detected'] += len(opportunities)
            
            if not opportunities:
                self.logger.debug("Aucune opportunité")
                return
            
            self.logger.info(f"💡 {len(opportunities)} opportunité(s)")
            
            # 3. Exécuter
            for opp in opportunities:
                self._process_opportunity(opp)
        
        except Exception as e:
            self.stats['errors_count'] += 1
            self.logger.error(f"Erreur cycle: {e}")
    
    def _collect_prices(self) -> Dict[str, Any]:
        """Collecte les prix et analyse les opportunités"""
        try:
            # Utiliser collect_and_analyze() qui fait TOUT d'un coup
            symbols = self.config.get('symbols', ['BTC/USDT'])
            trade_amount = self.config.get('default_trade_amount', 100.0)
            
            # Collecter pour le premier symbole (ou tous si on veut)
            all_opportunities = []
            all_prices = {}
            
            for symbol in symbols:
                result = self.price_collector.collect_and_analyze(
                    symbol=symbol,
                    save_to_db=False,  # Optionnel
                    trade_amount_usd=trade_amount
                )
                
                # Fusionner les opportunités
                all_opportunities.extend(result.get('opportunities', []))
                
                # Garder les prix du premier symbole
                if not all_prices:
                    all_prices = result.get('prices', {})
            
            # Retourner dans le format attendu
            return {
                'prices': all_prices,
                'opportunities': all_opportunities
            }
        
        except Exception as e:
            self.logger.error(f"Erreur collection: {e}")
            return {'prices': {}, 'opportunities': []}
    
    def _process_opportunity(self, opportunity: Dict[str, Any]):
        """Traite une opportunité"""
        symbol = opportunity.get('symbol', 'UNKNOWN')
        profit_pct = opportunity.get('net_profit_pct', 0)
        
        self.logger.info(
            f"📊 {symbol} ({profit_pct:+.2f}%)",
            extra={'context': opportunity}
        )
        
        # Montant
        trade_amount = self.config.get('default_trade_amount', 100.0)
        
        # Validation
        if self.risk_manager and hasattr(self.risk_manager, 'can_trade'):
            can_trade, reason = self.risk_manager.can_trade(opportunity, trade_amount)
            if not can_trade:
                self.logger.warning(f"❌ Refusé: {reason}")
                self.stats['trades_skipped'] += 1
                return
        
        # Exécution
        try:
            result = self.executor.execute_arbitrage(opportunity, trade_amount)
            
            if result.get('success'):
                net_profit = result['net_profit_usd']
                is_win = net_profit > 0
                
                self.logger.info(
                    f"{'✅' if is_win else '❌'} Trade: {net_profit:+.2f} USD",
                    extra={'context': result}
                )
                
                # Trackers
                if self.risk_manager and hasattr(self.risk_manager, 'record_trade_result'):
                    self.risk_manager.record_trade_result(net_profit, is_win)
                
                if self.daily_tracker and hasattr(self.daily_tracker, 'record_trade'):
                    self.daily_tracker.record_trade(
                        profit_usd=net_profit,
                        is_win=is_win,
                        symbol=symbol
                    )
                
                # Balance
                new_balance = self.executor.get_balance()
                if self.risk_manager and hasattr(self.risk_manager, 'update_balance'):
                    self.risk_manager.update_balance(new_balance)
                
                self.stats['trades_executed'] += 1
            
            else:
                self.logger.warning(f"❌ Échoué: {result.get('error')}")
                self.stats['trades_skipped'] += 1
        
        except Exception as e:
            self.logger.error(f"Erreur exécution: {e}")
            self.stats['errors_count'] += 1
    
    def _should_stop(self, duration_seconds, max_cycles) -> bool:
        """Vérifie arrêt"""
        if duration_seconds and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if elapsed >= duration_seconds:
                self.logger.info(f"⏰ Durée max ({duration_seconds}s)")
                return True
        
        if max_cycles and self.cycle_count >= max_cycles:
            self.logger.info(f"🔄 Cycles max ({max_cycles})")
            return True
        
        return False
    
    def _shutdown(self):
        """Arrêt"""
        self.is_running = False
        
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        self.logger.info("=" * 60)
        self.logger.info("  ARRÊT DU BOT")
        self.logger.info("=" * 60)
        
        self.display_statistics()
        
        self.logger.info(f"\n⏱️  Durée: {elapsed:.0f}s ({elapsed/60:.1f} min)")
        self.logger.info(f"🔄 Cycles: {self.cycle_count}")
        self.logger.info("=" * 60)
    
    def stop(self):
        """Arrête le bot"""
        self.logger.info("🛑 Arrêt demandé...")
        self.is_running = False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Récupère stats"""
        stats = {'bot': self.stats}
        
        # Executor
        if hasattr(self.executor, 'get_statistics'):
            stats['executor'] = self.executor.get_statistics()
        else:
            stats['executor'] = {
                'current_balance': getattr(self.executor, 'current_balance', 10000.0),
                'net_pnl': 0.0,
                'roi_pct': 0.0,
                'win_rate_pct': 0.0
            }
        
        # Tracker
        if self.daily_tracker and hasattr(self.daily_tracker, 'get_stats'):
            stats['tracker'] = self.daily_tracker.get_stats()
        else:
            stats['tracker'] = {}
        
        # Risk Manager
        if self.risk_manager and hasattr(self.risk_manager, 'get_daily_stats'):
            stats['risk_manager'] = self.risk_manager.get_daily_stats()
        else:
            stats['risk_manager'] = {}
        
        # Circuit Breaker
        if self.circuit_breaker and hasattr(self.circuit_breaker, 'get_status'):
            cb_status = self.circuit_breaker.get_status()
            # Assurer que is_tripped existe
            if 'is_tripped' not in cb_status:
                cb_status['is_tripped'] = False
            stats['circuit_breaker'] = cb_status
        else:
            stats['circuit_breaker'] = {'is_tripped': False}
        
        # Errors
        if self.error_handler and hasattr(self.error_handler, 'get_stats'):
            stats['errors'] = self.error_handler.get_stats()
        else:
            stats['errors'] = {}
        
        return stats
    
    def display_statistics(self):
        """Affiche stats"""
        try:
            stats = self.get_statistics()
            
            print("\n" + "=" * 60)
            print("  STATISTIQUES DU BOT")
            print("=" * 60)
            
            print("\n📊 OPPORTUNITÉS:")
            print(f"  Détectées:         {stats['bot']['opportunities_detected']}")
            
            print("\n💼 TRADES:")
            print(f"  Exécutés:          {stats['bot']['trades_executed']}")
            print(f"  Ignorés:           {stats['bot']['trades_skipped']}")
            
            print("\n💰 PERFORMANCE:")
            net_pnl = stats['executor'].get('net_pnl', 0.0)
            roi = stats['executor'].get('roi_pct', 0.0)
            print(f"  Balance:           ${stats['executor'].get('current_balance', 0):,.2f}")
            print(f"  PnL:               {net_pnl:+.2f} USD ({roi:+.2f}%)")
            print(f"  Win rate:          {stats['executor'].get('win_rate_pct', 0):.1f}%")
            
            print("\n⚠️  ERREURS:")
            print(f"  Total:             {stats['bot']['errors_count']}")
            
            print("\n🔒 CIRCUIT BREAKER:")
            cb_state = "🚨 OUVERT" if stats['circuit_breaker'].get('is_tripped', False) else "✅ FERMÉ"
            print(f"  État:              {cb_state}")
            
            print("\n" + "=" * 60)
        
        except Exception as e:
            print(f"\n❌ Erreur affichage stats: {e}")
    
    def __repr__(self):
        state = "RUNNING" if self.is_running else "STOPPED"
        mode = "DRY-RUN" if self.dry_run else "REAL"
        return f"<TradingOrchestrator(state={state}, mode={mode}, cycles={self.cycle_count})>"


# Exemple
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST TRADING ORCHESTRATOR")
    print("=" * 60)
    
    orchestrator = TradingOrchestrator(
        dry_run=True,
        initial_balance=10000.0,
        config={
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'default_trade_amount': 100.0,
            'min_opportunity_score': 70
        }
    )
    
    print("\n🚀 Lancement pour 10 secondes...")
    orchestrator.run(
        duration_seconds=10,
        interval_seconds=2
    )
    
    print("\n" + "=" * 60)
    print("✅ Test terminé")
