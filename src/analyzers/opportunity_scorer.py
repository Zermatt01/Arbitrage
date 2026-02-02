"""
Opportunity Scorer - Système de Scoring des Opportunités
=========================================================

Score et classe les opportunités d'arbitrage selon plusieurs critères.

Usage:
    from src.analyzers.opportunity_scorer import OpportunityScorer
    
    scorer = OpportunityScorer()
    result = scorer.score_opportunity(opportunity)
    print(f"Score: {result['total_score']}/100")
"""

from typing import Dict, List, Any
from src.utils.logger import get_logger


class OpportunityScorer:
    """
    Score les opportunités d'arbitrage selon plusieurs critères
    
    Critères de scoring :
    - Profit NET (40 points max)
    - Liquidité disponible (30 points max)
    - Fiabilité des exchanges (20 points max)
    - Vitesse d'exécution (10 points max)
    
    Score total : 0-100 points
    """
    
    # Fiabilité des exchanges (basée sur uptime, API, sécurité)
    EXCHANGE_RELIABILITY = {
        'binance': 95,    # Très fiable
        'kraken': 90,     # Très fiable
        'coinbase': 85,   # Fiable
        'bitfinex': 80,   # Fiable
        'bitstamp': 80,   # Fiable
        'okx': 85,        # Fiable
        'bybit': 80,      # Fiable
        'huobi': 75,      # Moyennement fiable
        'kucoin': 75,     # Moyennement fiable
        'gate': 70,       # Moyennement fiable
    }
    
    # Vitesse moyenne d'exécution (latence en ms)
    EXCHANGE_SPEED = {
        'binance': 150,   # Très rapide
        'okx': 180,       # Rapide
        'bybit': 200,     # Rapide
        'kraken': 250,    # Moyen
        'coinbase': 300,  # Moyen
        'bitfinex': 350,  # Lent
        'bitstamp': 400,  # Lent
        'huobi': 450,     # Très lent
        'kucoin': 500,    # Très lent
        'gate': 550,      # Très lent
    }
    
    def __init__(self):
        """Initialise le scorer"""
        self.logger = get_logger(__name__)
        self.logger.debug("OpportunityScorer initialisé")
    
    def score_profit(self, net_profit_pct: float) -> float:
        """
        Score le profit NET (0-40 points)
        
        Args:
            net_profit_pct: Profit NET en % (float)
        
        Returns:
            Score sur 40 points
        """
        if net_profit_pct <= 0:
            return 0.0
        
        # Score linéaire jusqu'à 2%
        if net_profit_pct <= 2.0:
            score = (net_profit_pct / 2.0) * 40
        else:
            score = 40.0
        
        return min(score, 40.0)
    
    def score_liquidity(
        self,
        filled_pct: float = 100.0,
        slippage_pct: float = 0.0,
        volume_ratio: float = 1.0
    ) -> float:
        """
        Score la liquidité (0-30 points)
        
        Args:
            filled_pct: % du montant qui peut être rempli
            slippage_pct: Slippage total en %
            volume_ratio: Ratio volume disponible / volume souhaité
        
        Returns:
            Score sur 30 points
        """
        # Remplissage (15 points)
        fill_score = (filled_pct / 100.0) * 15.0
        
        # Slippage (10 points)
        if slippage_pct <= 0.5:
            slippage_score = 10.0 * (1.0 - slippage_pct / 0.5)
        else:
            slippage_score = 0.0
        
        # Volume (5 points)
        if volume_ratio >= 10.0:
            volume_score = 5.0
        elif volume_ratio >= 1.0:
            volume_score = 5.0 * (volume_ratio - 1.0) / 9.0
        else:
            volume_score = 0.0
        
        total = fill_score + slippage_score + volume_score
        return min(total, 30.0)
    
    def score_reliability(
        self,
        exchange_buy: str,
        exchange_sell: str
    ) -> float:
        """
        Score la fiabilité des exchanges (0-20 points)
        
        Args:
            exchange_buy: Exchange d'achat
            exchange_sell: Exchange de vente
        
        Returns:
            Score sur 20 points
        """
        buy_reliability = self.EXCHANGE_RELIABILITY.get(exchange_buy.lower(), 50)
        sell_reliability = self.EXCHANGE_RELIABILITY.get(exchange_sell.lower(), 50)
        
        avg_reliability = (buy_reliability + sell_reliability) / 2.0
        score = (avg_reliability / 100.0) * 20.0
        
        return score
    
    def score_speed(
        self,
        exchange_buy: str,
        exchange_sell: str
    ) -> float:
        """
        Score la vitesse d'exécution (0-10 points)
        
        Args:
            exchange_buy: Exchange d'achat
            exchange_sell: Exchange de vente
        
        Returns:
            Score sur 10 points
        """
        buy_speed = self.EXCHANGE_SPEED.get(exchange_buy.lower(), 500)
        sell_speed = self.EXCHANGE_SPEED.get(exchange_sell.lower(), 500)
        
        avg_latency = (buy_speed + sell_speed) / 2.0
        
        # Convertir latence en score (inverse)
        if avg_latency <= 200:
            score = 10.0
        elif avg_latency <= 500:
            score = 10.0 - ((avg_latency - 200.0) / 300.0) * 5.0
        elif avg_latency <= 1000:
            score = 5.0 - ((avg_latency - 500.0) / 500.0) * 5.0
        else:
            score = 0.0
        
        return max(score, 0.0)
    
    def score_opportunity(
        self,
        opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score une opportunité complète
        
        Args:
            opportunity: Opportunité à scorer
        
        Returns:
            Dict avec scores détaillés et score total
        """
        # Extraire les données
        net_profit_pct = opportunity.get('net_profit_real_pct', 
                                        opportunity.get('net_profit_pct', 0.0))
        
        exchange_buy = opportunity.get('exchange_buy', '')
        exchange_sell = opportunity.get('exchange_sell', '')
        
        # Liquidité
        filled_pct = opportunity.get('filled_pct', 100.0)
        slippage_pct = opportunity.get('total_slippage_pct', 0.0)
        
        # Estimer le volume ratio si disponible
        volume_ratio = 1.0
        if 'liquidity_valid' in opportunity:
            volume_ratio = 5.0 if opportunity['liquidity_valid'] else 0.5
        
        # Calculer chaque score
        profit_score = self.score_profit(net_profit_pct)
        liquidity_score = self.score_liquidity(filled_pct, slippage_pct, volume_ratio)
        reliability_score = self.score_reliability(exchange_buy, exchange_sell)
        speed_score = self.score_speed(exchange_buy, exchange_sell)
        
        # Score total
        total_score = profit_score + liquidity_score + reliability_score + speed_score
        
        # Créer le résultat
        result = {
            'total_score': round(total_score, 2),
            'grade': self._get_grade(total_score),
            
            # Scores détaillés
            'profit_score': round(profit_score, 2),
            'liquidity_score': round(liquidity_score, 2),
            'reliability_score': round(reliability_score, 2),
            'speed_score': round(speed_score, 2),
            
            # Métadonnées
            'net_profit_pct': net_profit_pct,
            'exchange_buy': exchange_buy,
            'exchange_sell': exchange_sell,
            'slippage_pct': slippage_pct,
        }
        
        self.logger.debug(
            f"Opportunité scorée: {exchange_buy}→{exchange_sell} "
            f"Score {total_score:.1f}/100 ({result['grade']})",
            extra={'context': result}
        )
        
        # Fusionner avec l'opportunité originale
        scored_opportunity = {**opportunity, **result}
        
        return scored_opportunity
    
    def _get_grade(self, score: float) -> str:
        """
        Convertit un score en note
        
        Args:
            score: Score 0-100
        
        Returns:
            Note (S, A, B, C, D, F)
        """
        if score >= 90:
            return 'S'   # Excellent
        elif score >= 80:
            return 'A'   # Très bon
        elif score >= 70:
            return 'B'   # Bon
        elif score >= 60:
            return 'C'   # Moyen
        elif score >= 50:
            return 'D'   # Passable
        else:
            return 'F'   # Mauvais
    
    def rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Score et classe plusieurs opportunités
        
        Args:
            opportunities: Liste d'opportunités
        
        Returns:
            Liste triée par score décroissant avec scores ajoutés
        """
        scored_opportunities = []
        
        for opp in opportunities:
            scored_opp = self.score_opportunity(opp)
            scored_opportunities.append(scored_opp)
        
        # Trier par score décroissant
        scored_opportunities.sort(key=lambda x: x['total_score'], reverse=True)
        
        self.logger.info(
            f"{len(opportunities)} opportunités classées",
            extra={'context': {
                'total': len(opportunities),
                'top_score': scored_opportunities[0]['total_score'] if scored_opportunities else 0,
                'avg_score': sum(o['total_score'] for o in scored_opportunities) / len(scored_opportunities) if scored_opportunities else 0
            }}
        )
        
        return scored_opportunities
    
    def filter_by_score(
        self,
        opportunities: List[Dict[str, Any]],
        min_score: float = 60.0
    ) -> List[Dict[str, Any]]:
        """
        Filtre les opportunités par score minimum
        
        Args:
            opportunities: Liste d'opportunités scorées
            min_score: Score minimum (défaut: 60/100)
        
        Returns:
            Liste filtrée
        """
        filtered = [
            opp for opp in opportunities
            if opp.get('total_score', 0) >= min_score
        ]
        
        self.logger.info(
            f"{len(filtered)}/{len(opportunities)} opportunités >= {min_score} points",
            extra={'context': {
                'total': len(opportunities),
                'filtered': len(filtered),
                'min_score': min_score
            }}
        )
        
        return filtered
    
    def get_top_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Récupère les N meilleures opportunités
        
        Args:
            opportunities: Liste d'opportunités scorées et triées
            top_n: Nombre d'opportunités à retourner
        
        Returns:
            Top N opportunités
        """
        return opportunities[:top_n]
    
    def __repr__(self):
        """Représentation textuelle"""
        return f"<OpportunityScorer(exchanges={len(self.EXCHANGE_RELIABILITY)})>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST OPPORTUNITY SCORER")
    print("=" * 60)
    
    scorer = OpportunityScorer()
    
    # Exemples d'opportunités
    opportunities = [
        {
            'exchange_buy': 'binance',
            'exchange_sell': 'kraken',
            'net_profit_pct': 0.8,
            'total_slippage_pct': 0.1,
            'liquidity_valid': True,
        },
        {
            'exchange_buy': 'kraken',
            'exchange_sell': 'coinbase',
            'net_profit_pct': 1.5,
            'total_slippage_pct': 0.3,
            'liquidity_valid': True,
        },
        {
            'exchange_buy': 'bitstamp',
            'exchange_sell': 'huobi',
            'net_profit_pct': 2.0,
            'total_slippage_pct': 0.8,
            'liquidity_valid': False,
        }
    ]
    
    print("\n📊 Classement des opportunités:")
    print("-" * 60)
    
    ranked = scorer.rank_opportunities(opportunities)
    
    for i, opp in enumerate(ranked, 1):
        print(f"\n#{i} - {opp['exchange_buy']} → {opp['exchange_sell']}")
        print(f"  Score total: {opp['total_score']:.1f}/100 (Grade {opp['grade']})")
        print(f"  - Profit: {opp['profit_score']:.1f}/40")
        print(f"  - Liquidité: {opp['liquidity_score']:.1f}/30")
        print(f"  - Fiabilité: {opp['reliability_score']:.1f}/20")
        print(f"  - Vitesse: {opp['speed_score']:.1f}/10")
        print(f"  Profit NET: {opp['net_profit_pct']:.2f}%")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
