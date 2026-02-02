"""
Slippage Simulator - Calcul Réaliste du Slippage
==================================================

Calcule le slippage réel basé sur l'analyse de l'orderbook.

Usage:
    from src.execution.slippage_simulator import SlippageSimulator
    
    simulator = SlippageSimulator()
    
    # Calculer le slippage pour un achat
    slippage = simulator.calculate_slippage(
        orderbook=orderbook,
        side='buy',
        amount_usd=1000.0
    )
"""

from typing import Dict, Any, List, Tuple
from src.utils.logger import get_logger


class SlippageSimulator:
    """
    Simule le slippage basé sur l'analyse de l'orderbook
    
    Fonctionnalités :
    - Analyse les niveaux de l'orderbook
    - Calcule le prix moyen d'exécution
    - Estime le market impact
    - Retourne slippage précis en %
    """
    
    def __init__(self):
        """Initialise le simulateur"""
        self.logger = get_logger(__name__)
        
        self.logger.debug("SlippageSimulator initialisé")
    
    def calculate_slippage(
        self,
        orderbook: Dict[str, Any],
        side: str,
        amount_usd: float,
        current_price: float = None
    ) -> Dict[str, Any]:
        """
        Calcule le slippage pour un ordre
        
        Args:
            orderbook: Orderbook (format: {'bids': [[price, volume], ...], 'asks': [...]})
            side: 'buy' ou 'sell'
            amount_usd: Montant en USD à trader
            current_price: Prix actuel (optionnel, sinon utilise meilleur bid/ask)
        
        Returns:
            Dict avec:
                - average_price: Prix moyen d'exécution
                - slippage_pct: Slippage en %
                - slippage_usd: Slippage en USD
                - filled_pct: % de l'ordre rempli
                - levels_consumed: Nombre de niveaux consommés
        
        Example:
            >>> orderbook = {
            ...     'bids': [[50000, 1.0], [49990, 2.0]],
            ...     'asks': [[50010, 0.5], [50020, 1.5]]
            ... }
            >>> result = simulator.calculate_slippage(orderbook, 'buy', 1000.0)
            >>> print(f"Slippage: {result['slippage_pct']:.2f}%")
        """
        # Valider les paramètres
        if side not in ['buy', 'sell']:
            raise ValueError(f"side doit être 'buy' ou 'sell', pas '{side}'")
        
        if amount_usd <= 0:
            raise ValueError(f"amount_usd doit être > 0, pas {amount_usd}")
        
        # Sélectionner le bon côté de l'orderbook
        if side == 'buy':
            # Pour acheter, on consomme les asks (vendeurs)
            levels = orderbook.get('asks', [])
            if not levels:
                raise ValueError("Orderbook vide (pas d'asks)")
            best_price = levels[0][0] if levels else 0
        else:
            # Pour vendre, on consomme les bids (acheteurs)
            levels = orderbook.get('bids', [])
            if not levels:
                raise ValueError("Orderbook vide (pas de bids)")
            best_price = levels[0][0] if levels else 0
        
        # Prix de référence
        reference_price = current_price or best_price
        
        # Simuler l'exécution
        result = self._simulate_execution(
            levels=levels,
            amount_usd=amount_usd,
            reference_price=reference_price
        )
        
        # Calculer le slippage
        slippage_pct = ((result['average_price'] - reference_price) / reference_price) * 100
        
        # Pour un achat, slippage positif = prix plus élevé (mauvais)
        # Pour une vente, slippage positif = prix plus bas (mauvais)
        if side == 'sell':
            slippage_pct = -slippage_pct
        
        slippage_usd = (amount_usd * abs(slippage_pct)) / 100
        
        return {
            'average_price': result['average_price'],
            'slippage_pct': slippage_pct,
            'slippage_usd': slippage_usd,
            'filled_pct': result['filled_pct'],
            'levels_consumed': result['levels_consumed'],
            'remaining_usd': result['remaining_usd'],
        }
    
    def _simulate_execution(
        self,
        levels: List[List[float]],
        amount_usd: float,
        reference_price: float
    ) -> Dict[str, Any]:
        """
        Simule l'exécution d'un ordre à travers les niveaux
        
        Args:
            levels: Niveaux de l'orderbook [[price, volume], ...]
            amount_usd: Montant en USD à trader
            reference_price: Prix de référence
        
        Returns:
            Dict avec résultats de simulation
        """
        total_cost = 0.0
        total_quantity = 0.0
        remaining_usd = amount_usd
        levels_consumed = 0
        
        for price, available_volume in levels:
            if remaining_usd <= 0:
                break
            
            # Calculer combien on peut acheter à ce niveau
            max_quantity_at_level = remaining_usd / price
            quantity_to_buy = min(max_quantity_at_level, available_volume)
            
            # Coût de cet achat
            cost = quantity_to_buy * price
            
            # Accumuler
            total_cost += cost
            total_quantity += quantity_to_buy
            remaining_usd -= cost
            levels_consumed += 1
            
            self.logger.debug(
                f"Niveau {levels_consumed}: Prix={price:.2f}, "
                f"Quantité={quantity_to_buy:.6f}, Coût=${cost:.2f}"
            )
        
        # Prix moyen d'exécution
        average_price = total_cost / total_quantity if total_quantity > 0 else reference_price
        
        # % rempli
        filled_usd = amount_usd - remaining_usd
        filled_pct = (filled_usd / amount_usd) * 100
        
        return {
            'average_price': average_price,
            'total_quantity': total_quantity,
            'total_cost': total_cost,
            'filled_pct': filled_pct,
            'remaining_usd': remaining_usd,
            'levels_consumed': levels_consumed,
        }
    
    def estimate_market_impact(
        self,
        orderbook: Dict[str, Any],
        side: str,
        amount_usd: float
    ) -> Dict[str, Any]:
        """
        Estime l'impact sur le marché (slippage + liquidity)
        
        Args:
            orderbook: Orderbook
            side: 'buy' ou 'sell'
            amount_usd: Montant en USD
        
        Returns:
            Dict avec estimation d'impact
        """
        # Calculer le slippage
        slippage = self.calculate_slippage(orderbook, side, amount_usd)
        
        # Analyser la liquidité disponible
        levels = orderbook.get('asks' if side == 'buy' else 'bids', [])
        
        # Volume total disponible dans les 10 premiers niveaux
        total_volume_10_levels = sum(volume for _, volume in levels[:10])
        
        # Volume total disponible
        total_volume_all = sum(volume for _, volume in levels)
        
        # Prix au meilleur niveau
        best_price = levels[0][0] if levels else 0
        
        # Valeur en USD des 10 premiers niveaux
        total_usd_10_levels = sum(price * volume for price, volume in levels[:10])
        
        # Ratio de l'ordre vs liquidité
        liquidity_ratio = amount_usd / total_usd_10_levels if total_usd_10_levels > 0 else float('inf')
        
        # Classification de l'impact
        if slippage['filled_pct'] < 100:
            impact_level = 'CRITICAL'  # Pas assez de liquidité
        elif liquidity_ratio > 0.5:
            impact_level = 'HIGH'  # > 50% de la liquidité
        elif liquidity_ratio > 0.2:
            impact_level = 'MEDIUM'  # 20-50% de la liquidité
        elif liquidity_ratio > 0.1:
            impact_level = 'LOW'  # 10-20% de la liquidité
        else:
            impact_level = 'MINIMAL'  # < 10% de la liquidité
        
        return {
            'slippage_pct': slippage['slippage_pct'],
            'filled_pct': slippage['filled_pct'],
            'levels_consumed': slippage['levels_consumed'],
            'liquidity_ratio': liquidity_ratio,
            'total_volume_10_levels': total_volume_10_levels,
            'total_volume_all': total_volume_all,
            'impact_level': impact_level,
            'is_executable': slippage['filled_pct'] >= 100,
        }
    
    def get_executable_amount(
        self,
        orderbook: Dict[str, Any],
        side: str,
        max_slippage_pct: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calcule le montant maximum exécutable avec slippage limité
        
        Args:
            orderbook: Orderbook
            side: 'buy' ou 'sell'
            max_slippage_pct: Slippage maximum acceptable (%)
        
        Returns:
            Dict avec montant maximum et infos
        """
        levels = orderbook.get('asks' if side == 'buy' else 'bids', [])
        
        if not levels:
            return {
                'max_amount_usd': 0.0,
                'max_quantity': 0.0,
                'slippage_pct': 0.0,
                'levels_available': 0,
            }
        
        best_price = levels[0][0]
        max_price = best_price * (1 + max_slippage_pct / 100)
        
        total_usd = 0.0
        total_quantity = 0.0
        levels_used = 0
        
        for price, volume in levels:
            if price > max_price:
                break
            
            usd_at_level = price * volume
            total_usd += usd_at_level
            total_quantity += volume
            levels_used += 1
        
        # Calculer le slippage effectif
        if total_quantity > 0:
            average_price = total_usd / total_quantity
            actual_slippage_pct = ((average_price - best_price) / best_price) * 100
        else:
            actual_slippage_pct = 0.0
        
        return {
            'max_amount_usd': total_usd,
            'max_quantity': total_quantity,
            'slippage_pct': actual_slippage_pct,
            'levels_available': levels_used,
            'best_price': best_price,
            'worst_price': levels[levels_used - 1][0] if levels_used > 0 else best_price,
        }


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST SLIPPAGE SIMULATOR")
    print("=" * 60)
    
    # Créer le simulateur
    simulator = SlippageSimulator()
    
    # Orderbook de test (BTC/USDT)
    orderbook = {
        'bids': [
            [50000, 1.0],    # 1 BTC @ $50,000
            [49990, 2.0],    # 2 BTC @ $49,990
            [49980, 1.5],    # 1.5 BTC @ $49,980
        ],
        'asks': [
            [50010, 0.5],    # 0.5 BTC @ $50,010
            [50020, 1.0],    # 1 BTC @ $50,020
            [50030, 2.0],    # 2 BTC @ $50,030
        ]
    }
    
    # Test 1: Petit ordre (faible impact)
    print("\n📊 Test 1: Petit ordre ($500)")
    result = simulator.calculate_slippage(orderbook, 'buy', 500.0)
    print(f"   Prix moyen: ${result['average_price']:,.2f}")
    print(f"   Slippage: {result['slippage_pct']:.3f}%")
    print(f"   Rempli: {result['filled_pct']:.1f}%")
    print(f"   Niveaux: {result['levels_consumed']}")
    
    # Test 2: Gros ordre (fort impact)
    print("\n📊 Test 2: Gros ordre ($5,000)")
    result = simulator.calculate_slippage(orderbook, 'buy', 5000.0)
    print(f"   Prix moyen: ${result['average_price']:,.2f}")
    print(f"   Slippage: {result['slippage_pct']:.3f}%")
    print(f"   Rempli: {result['filled_pct']:.1f}%")
    print(f"   Niveaux: {result['levels_consumed']}")
    
    # Test 3: Impact sur le marché
    print("\n📊 Test 3: Estimation d'impact ($2,000)")
    impact = simulator.estimate_market_impact(orderbook, 'buy', 2000.0)
    print(f"   Impact: {impact['impact_level']}")
    print(f"   Ratio liquidité: {impact['liquidity_ratio']:.2%}")
    print(f"   Exécutable: {impact['is_executable']}")
    
    # Test 4: Montant maximum
    print("\n📊 Test 4: Montant max (slippage < 0.5%)")
    max_amt = simulator.get_executable_amount(orderbook, 'buy', max_slippage_pct=0.5)
    print(f"   Max USD: ${max_amt['max_amount_usd']:,.2f}")
    print(f"   Max quantité: {max_amt['max_quantity']:.4f} BTC")
    print(f"   Slippage: {max_amt['slippage_pct']:.3f}%")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
