"""
Liquidity Validator - Validateur de Liquidité
==============================================

Valide qu'une opportunité est exécutable en analysant la liquidité disponible.

Usage:
    from src.validators.liquidity_validator import LiquidityValidator
    
    validator = LiquidityValidator()
    result = validator.validate_liquidity(orderbook, trade_amount_usd)
"""

from typing import Dict, List, Any, Optional, Tuple
from src.utils.logger import get_logger


class LiquidityValidator:
    """
    Valide la liquidité disponible pour exécuter un trade
    
    Analyse les orderbooks pour :
    - Calculer le prix moyen d'exécution réel
    - Estimer le slippage
    - Vérifier qu'il y a assez de volume
    """
    
    def __init__(self, max_slippage_pct: float = 0.5):
        """
        Initialise le validateur
        
        Args:
            max_slippage_pct: Slippage maximum acceptable (en %)
        """
        self.logger = get_logger(__name__)
        self.max_slippage_pct = max_slippage_pct
        
        self.logger.debug(
            f"LiquidityValidator initialisé",
            extra={'context': {'max_slippage_pct': max_slippage_pct}}
        )
    
    def calculate_execution_price(
        self,
        orderbook_side: List[List[float]],
        crypto_amount: float
    ) -> Dict[str, Any]:
        """
        Calcule le prix moyen d'exécution pour un montant donné
        
        Args:
            orderbook_side: Liste des niveaux de prix [[price, volume], ...]
            crypto_amount: Quantité de crypto à acheter/vendre
        
        Returns:
            Dict avec:
                - avg_price: Prix moyen d'exécution
                - filled_amount: Quantité réellement remplie
                - slippage_pct: Slippage en %
                - levels_used: Nombre de niveaux utilisés
                - can_execute: Peut-on exécuter complètement ?
        
        Example:
            >>> orderbook = [[81235.45, 0.5], [81240.00, 1.2], ...]
            >>> result = validator.calculate_execution_price(orderbook, 1.0)
            >>> print(result['avg_price'])
            81237.73
        """
        if not orderbook_side or crypto_amount <= 0:
            return {
                'avg_price': 0,
                'filled_amount': 0,
                'slippage_pct': 0,
                'levels_used': 0,
                'can_execute': False,
                'total_cost_or_revenue': 0
            }
        
        total_cost_or_revenue = 0
        filled_amount = 0
        levels_used = 0
        best_price = orderbook_side[0][0]
        
        # Parcourir les niveaux du carnet d'ordres
        for level in orderbook_side:
    # CCXT peut retourner [price, volume] ou [price, volume, timestamp]
            price = level[0]
            volume = level[1]
            if filled_amount >= crypto_amount:
                break
            
            levels_used += 1
            remaining = crypto_amount - filled_amount
            
            # Quantité à prendre à ce niveau
            take_amount = min(remaining, volume)
            
            # Coût/revenu à ce niveau
            total_cost_or_revenue += price * take_amount
            filled_amount += take_amount
        
        # Calcul du prix moyen
        if filled_amount > 0:
            avg_price = total_cost_or_revenue / filled_amount
            slippage_pct = ((avg_price - best_price) / best_price) * 100
        else:
            avg_price = 0
            slippage_pct = 0
        
        can_execute = filled_amount >= crypto_amount * 0.95  # Au moins 95%
        
        result = {
            'avg_price': avg_price,
            'filled_amount': filled_amount,
            'slippage_pct': abs(slippage_pct),
            'levels_used': levels_used,
            'can_execute': can_execute,
            'total_cost_or_revenue': total_cost_or_revenue,
            'best_price': best_price
        }
        
        self.logger.debug(
            f"Calcul prix exécution: {filled_amount:.6f} crypto @ {avg_price:.2f} "
            f"(slippage {slippage_pct:+.2f}%)",
            extra={'context': result}
        )
        
        return result
    
    def validate_buy_liquidity(
        self,
        orderbook: Dict[str, Any],
        trade_amount_usd: float
    ) -> Dict[str, Any]:
        """
        Valide la liquidité pour un ACHAT
        
        Args:
            orderbook: Orderbook complet avec 'asks' et métadonnées
            trade_amount_usd: Montant en USD à trader
        
        Returns:
            Dict avec résultat de validation
        """
        asks = orderbook.get('asks', [])
        
        if not asks:
            return {
                'valid': False,
                'reason': 'Pas d\'asks disponibles',
                'avg_price': 0,
                'slippage_pct': 0
            }
        
        # Calculer la quantité de crypto qu'on veut acheter
        best_ask = asks[0][0]
        crypto_amount = trade_amount_usd / best_ask
        
        # Calculer le prix moyen d'exécution
        execution = self.calculate_execution_price(asks, crypto_amount)
        
        # Validation
        if not execution['can_execute']:
            return {
                'valid': False,
                'reason': f"Liquidité insuffisante: seulement {execution['filled_amount']:.6f} disponible",
                'avg_price': execution['avg_price'],
                'slippage_pct': execution['slippage_pct'],
                'filled_pct': (execution['filled_amount'] / crypto_amount) * 100 if crypto_amount > 0 else 0
            }
        
        if execution['slippage_pct'] > self.max_slippage_pct:
            return {
                'valid': False,
                'reason': f"Slippage trop élevé: {execution['slippage_pct']:.2f}% > {self.max_slippage_pct}%",
                'avg_price': execution['avg_price'],
                'slippage_pct': execution['slippage_pct'],
                'filled_pct': 100
            }
        
        # Tout est OK
        return {
            'valid': True,
            'reason': 'Liquidité suffisante',
            'avg_price': execution['avg_price'],
            'best_price': execution['best_price'],
            'slippage_pct': execution['slippage_pct'],
            'filled_pct': 100,
            'crypto_amount': crypto_amount,
            'levels_used': execution['levels_used'],
            'total_cost': execution['total_cost_or_revenue']
        }
    
    def validate_sell_liquidity(
        self,
        orderbook: Dict[str, Any],
        crypto_amount: float
    ) -> Dict[str, Any]:
        """
        Valide la liquidité pour une VENTE
        
        Args:
            orderbook: Orderbook complet avec 'bids' et métadonnées
            crypto_amount: Quantité de crypto à vendre
        
        Returns:
            Dict avec résultat de validation
        """
        bids = orderbook.get('bids', [])
        
        if not bids:
            return {
                'valid': False,
                'reason': 'Pas de bids disponibles',
                'avg_price': 0,
                'slippage_pct': 0
            }
        
        # Calculer le prix moyen d'exécution
        execution = self.calculate_execution_price(bids, crypto_amount)
        
        # Validation
        if not execution['can_execute']:
            return {
                'valid': False,
                'reason': f"Liquidité insuffisante: seulement {execution['filled_amount']:.6f} disponible",
                'avg_price': execution['avg_price'],
                'slippage_pct': execution['slippage_pct'],
                'filled_pct': (execution['filled_amount'] / crypto_amount) * 100 if crypto_amount > 0 else 0
            }
        
        if execution['slippage_pct'] > self.max_slippage_pct:
            return {
                'valid': False,
                'reason': f"Slippage trop élevé: {execution['slippage_pct']:.2f}% > {self.max_slippage_pct}%",
                'avg_price': execution['avg_price'],
                'slippage_pct': execution['slippage_pct'],
                'filled_pct': 100
            }
        
        # Tout est OK
        return {
            'valid': True,
            'reason': 'Liquidité suffisante',
            'avg_price': execution['avg_price'],
            'best_price': execution['best_price'],
            'slippage_pct': execution['slippage_pct'],
            'filled_pct': 100,
            'levels_used': execution['levels_used'],
            'total_revenue': execution['total_cost_or_revenue']
        }
    
    def validate_arbitrage_liquidity(
        self,
        buy_orderbook: Dict[str, Any],
        sell_orderbook: Dict[str, Any],
        trade_amount_usd: float
    ) -> Dict[str, Any]:
        """
        Valide la liquidité pour un arbitrage complet (achat + vente)
        
        Args:
            buy_orderbook: Orderbook de l'exchange d'achat
            sell_orderbook: Orderbook de l'exchange de vente
            trade_amount_usd: Montant à trader
        
        Returns:
            Dict avec résultat complet de validation
        
        Example:
            >>> result = validator.validate_arbitrage_liquidity(
            ...     binance_orderbook, kraken_orderbook, 10000
            ... )
            >>> if result['valid']:
            ...     print(f"Profit NET après slippage: {result['net_profit_pct']:.2f}%")
        """
        # Valider le côté achat
        buy_validation = self.validate_buy_liquidity(buy_orderbook, trade_amount_usd)
        
        if not buy_validation['valid']:
            return {
                'valid': False,
                'reason': f"Achat impossible: {buy_validation['reason']}",
                'buy_validation': buy_validation,
                'sell_validation': None
            }
        
        # Valider le côté vente
        crypto_amount = buy_validation['crypto_amount']
        sell_validation = self.validate_sell_liquidity(sell_orderbook, crypto_amount)
        
        if not sell_validation['valid']:
            return {
                'valid': False,
                'reason': f"Vente impossible: {sell_validation['reason']}",
                'buy_validation': buy_validation,
                'sell_validation': sell_validation
            }
        
        # Calculer le profit NET après slippage
        avg_buy_price = buy_validation['avg_price']
        avg_sell_price = sell_validation['avg_price']
        
        gross_revenue = sell_validation['total_revenue']
        total_cost = buy_validation['total_cost']
        
        gross_profit_usd = gross_revenue - total_cost
        gross_profit_pct = (gross_profit_usd / total_cost) * 100
        
        # Slippage total
        total_slippage_pct = buy_validation['slippage_pct'] + sell_validation['slippage_pct']
        
        result = {
            'valid': True,
            'reason': 'Liquidité suffisante pour arbitrage',
            
            # Détails achat
            'buy_avg_price': avg_buy_price,
            'buy_best_price': buy_validation['best_price'],
            'buy_slippage_pct': buy_validation['slippage_pct'],
            
            # Détails vente
            'sell_avg_price': avg_sell_price,
            'sell_best_price': sell_validation['best_price'],
            'sell_slippage_pct': sell_validation['slippage_pct'],
            
            # Résultat global
            'crypto_amount': crypto_amount,
            'total_slippage_pct': total_slippage_pct,
            'gross_profit_usd': gross_profit_usd,
            'gross_profit_pct': gross_profit_pct,
            
            # Validations détaillées
            'buy_validation': buy_validation,
            'sell_validation': sell_validation
        }
        
        self.logger.info(
            f"Validation arbitrage: "
            f"Achat @ {avg_buy_price:.2f} (slip {buy_validation['slippage_pct']:.2f}%), "
            f"Vente @ {avg_sell_price:.2f} (slip {sell_validation['slippage_pct']:.2f}%), "
            f"Profit brut: {gross_profit_pct:+.2f}%",
            extra={'context': result}
        )
        
        return result
    
    def estimate_max_trade_amount(
        self,
        orderbook_side: List[List[float]],
        max_slippage_pct: float
    ) -> float:
        """
        Estime le montant maximum tradable avec un slippage donné
        
        Args:
            orderbook_side: asks ou bids
            max_slippage_pct: Slippage maximum acceptable
        
        Returns:
            Montant maximum en USD
        """
        if not orderbook_side:
            return 0
        
        best_price = orderbook_side[0][0]
        max_acceptable_price = best_price * (1 + max_slippage_pct / 100)
        
        total_volume = 0
        total_value = 0
        
        for price, volume in orderbook_side:
            if price > max_acceptable_price:
                break
            
            total_volume += volume
            total_value += price * volume
        
        return total_value
    
    def get_liquidity_depth(
        self,
        orderbook: Dict[str, Any],
        depth_levels: int = 10
    ) -> Dict[str, Any]:
        """
        Analyse la profondeur de liquidité
        
        Args:
            orderbook: Orderbook complet
            depth_levels: Nombre de niveaux à analyser
        
        Returns:
            Dict avec statistiques de profondeur
        """
        asks = orderbook.get('asks', [])[:depth_levels]
        bids = orderbook.get('bids', [])[:depth_levels]
        
        # Calcul pour les asks
        ask_volume = sum(vol for _, vol in asks) if asks else 0
        ask_value = sum(price * vol for price, vol in asks) if asks else 0
        
        # Calcul pour les bids
        bid_volume = sum(vol for _, vol in bids) if bids else 0
        bid_value = sum(price * vol for price, vol in bids) if bids else 0
        
        return {
            'ask_volume': ask_volume,
            'ask_value_usd': ask_value,
            'bid_volume': bid_volume,
            'bid_value_usd': bid_value,
            'total_volume': ask_volume + bid_volume,
            'total_value_usd': ask_value + bid_value,
            'depth_levels': depth_levels
        }
    
    def __repr__(self):
        """Représentation textuelle"""
        return f"<LiquidityValidator(max_slippage={self.max_slippage_pct}%)>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST LIQUIDITY VALIDATOR")
    print("=" * 60)
    
    validator = LiquidityValidator(max_slippage_pct=0.5)
    
    # Exemple d'orderbook
    orderbook_buy = {
        'asks': [
            [81235.45, 0.5],
            [81240.00, 1.2],
            [81250.00, 2.0],
            [81300.00, 3.5],
            [81400.00, 5.0]
        ]
    }
    
    orderbook_sell = {
        'bids': [
            [81200.00, 0.8],
            [81195.00, 1.5],
            [81190.00, 2.2],
            [81180.00, 4.0],
            [81150.00, 6.0]
        ]
    }
    
    # Test 1 : Validation achat
    print("\n1. Validation ACHAT de $1,000:")
    print("-" * 60)
    result = validator.validate_buy_liquidity(orderbook_buy, 1000)
    print(f"Valide: {result['valid']}")
    print(f"Prix moyen: ${result.get('avg_price', 0):,.2f}")
    print(f"Slippage: {result.get('slippage_pct', 0):.2f}%")
    print(f"Raison: {result['reason']}")
    
    # Test 2 : Validation vente
    print("\n2. Validation VENTE de 0.0123 BTC:")
    print("-" * 60)
    result = validator.validate_sell_liquidity(orderbook_sell, 0.0123)
    print(f"Valide: {result['valid']}")
    print(f"Prix moyen: ${result.get('avg_price', 0):,.2f}")
    print(f"Slippage: {result.get('slippage_pct', 0):.2f}%")
    print(f"Raison: {result['reason']}")
    
    # Test 3 : Validation arbitrage complet
    print("\n3. Validation ARBITRAGE de $10,000:")
    print("-" * 60)
    result = validator.validate_arbitrage_liquidity(orderbook_buy, orderbook_sell, 10000)
    if result['valid']:
        print(f"✅ Arbitrage VALIDE")
        print(f"Achat @ ${result['buy_avg_price']:,.2f} (slip {result['buy_slippage_pct']:.2f}%)")
        print(f"Vente @ ${result['sell_avg_price']:,.2f} (slip {result['sell_slippage_pct']:.2f}%)")
        print(f"Profit brut: {result['gross_profit_pct']:+.2f}% (${result['gross_profit_usd']:,.2f})")
    else:
        print(f"❌ Arbitrage INVALIDE")
        print(f"Raison: {result['reason']}")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
