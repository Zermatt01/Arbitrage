"""
Fee Calculator - Calculateur de Frais
======================================

Calcule tous les frais de trading pour l'arbitrage crypto.

Usage:
    from src.utils.fee_calculator import FeeCalculator
    
    calculator = FeeCalculator()
    fees = calculator.calculate_trade_fees('binance', 1000, 'maker')
    print(f"Frais: ${fees:.2f}")
"""

from typing import Dict, Literal, Optional
from src.utils.logger import get_logger


class FeeCalculator:
    """
    Calculateur de frais pour l'arbitrage
    
    Gère les frais de trading (maker/taker) pour chaque exchange.
    """
    
    # Configuration des frais par exchange (en %)
    # Source : Sites officiels des exchanges (Janvier 2026)
    TRADING_FEES = {
        'binance': {
            'maker': 0.10,   # 0.10%
            'taker': 0.10,   # 0.10%
            'notes': 'Avec BNB: 0.075%, VIP 0: 0.10%'
        },
        'kraken': {
            'maker': 0.16,   # 0.16%
            'taker': 0.26,   # 0.26%
            'notes': 'Tier 1 (0-$50k volume/mois)'
        },
        'coinbase': {
            'maker': 0.40,   # 0.40%
            'taker': 0.60,   # 0.60%
            'notes': 'Tier 1 (0-$10k volume)'
        },
        'bitfinex': {
            'maker': 0.10,   # 0.10%
            'taker': 0.20,   # 0.20%
            'notes': 'Tier 1'
        },
        'bitstamp': {
            'maker': 0.30,   # 0.30%
            'taker': 0.40,   # 0.40%
            'notes': 'Volume < $20k'
        },
        'okx': {
            'maker': 0.08,   # 0.08%
            'taker': 0.10,   # 0.10%
            'notes': 'Regular user'
        },
        'bybit': {
            'maker': 0.10,   # 0.10%
            'taker': 0.10,   # 0.10%
            'notes': 'VIP 0'
        },
        'huobi': {
            'maker': 0.20,   # 0.20%
            'taker': 0.20,   # 0.20%
            'notes': 'VIP 0'
        },
        'kucoin': {
            'maker': 0.10,   # 0.10%
            'taker': 0.10,   # 0.10%
            'notes': 'Level 0'
        },
        'gate': {
            'maker': 0.15,   # 0.15%
            'taker': 0.15,   # 0.15%
            'notes': 'VIP 0'
        }
    }
    
    # Frais de retrait typiques (en montant fixe USD)
    # NOTE: Ces frais ne sont utilisés que pour le rééquilibrage (optionnel pour v1)
    WITHDRAWAL_FEES = {
        'binance': {
            'BTC': 0.0005,   # ~$40 @ $80k
            'ETH': 0.005,    # ~$15 @ $3k
            'USDT': 1.0      # $1 (réseau TRC20)
        },
        'kraken': {
            'BTC': 0.00015,  # ~$12 @ $80k
            'ETH': 0.0025,   # ~$8 @ $3k
            'USDT': 10.0     # $10 (réseau ERC20)
        }
    }
    
    def __init__(self):
        """Initialise le calculateur"""
        self.logger = get_logger(__name__)
        
        self.logger.debug(
            f"FeeCalculator initialisé avec {len(self.TRADING_FEES)} exchanges",
            extra={'context': {'exchanges': list(self.TRADING_FEES.keys())}}
        )
    
    def get_trading_fee(
        self,
        exchange: str,
        fee_type: Literal['maker', 'taker'] = 'taker'
    ) -> float:
        """
        Récupère le frais de trading pour un exchange
        
        Args:
            exchange: Nom de l'exchange (ex: 'binance')
            fee_type: Type de frais ('maker' ou 'taker')
        
        Returns:
            Frais en % (ex: 0.10 pour 0.10%)
        
        Raises:
            ValueError si exchange inconnu
        """
        exchange = exchange.lower()
        
        if exchange not in self.TRADING_FEES:
            available = ', '.join(self.TRADING_FEES.keys())
            raise ValueError(
                f"Exchange '{exchange}' inconnu. "
                f"Exchanges disponibles: {available}"
            )
        
        fee = self.TRADING_FEES[exchange][fee_type]
        
        self.logger.debug(
            f"Frais {exchange} ({fee_type}): {fee}%",
            extra={'context': {
                'exchange': exchange,
                'fee_type': fee_type,
                'fee_pct': fee
            }}
        )
        
        return fee
    
    def calculate_trade_fees(
        self,
        exchange: str,
        trade_amount_usd: float,
        fee_type: Literal['maker', 'taker'] = 'taker'
    ) -> Dict[str, float]:
        """
        Calcule les frais pour un trade
        
        Args:
            exchange: Nom de l'exchange
            trade_amount_usd: Montant du trade en USD
            fee_type: Type de frais ('maker' ou 'taker')
        
        Returns:
            Dict avec:
                - fee_pct: Frais en %
                - fee_usd: Frais en USD
                - net_amount: Montant après frais
        
        Example:
            >>> calc = FeeCalculator()
            >>> fees = calc.calculate_trade_fees('binance', 1000, 'taker')
            >>> print(fees)
            {'fee_pct': 0.1, 'fee_usd': 1.0, 'net_amount': 999.0}
        """
        fee_pct = self.get_trading_fee(exchange, fee_type)
        fee_usd = (trade_amount_usd * fee_pct) / 100
        net_amount = trade_amount_usd - fee_usd
        
        return {
            'exchange': exchange,
            'fee_type': fee_type,
            'fee_pct': fee_pct,
            'fee_usd': fee_usd,
            'gross_amount': trade_amount_usd,
            'net_amount': net_amount
        }
    
    def calculate_arbitrage_profit(
        self,
        buy_exchange: str,
        sell_exchange: str,
        buy_price: float,
        sell_price: float,
        trade_amount_usd: float,
        buy_fee_type: Literal['maker', 'taker'] = 'taker',
        sell_fee_type: Literal['maker', 'taker'] = 'taker'
    ) -> Dict[str, float]:
        """
        Calcule le profit d'arbitrage NET après tous les frais
        
        Args:
            buy_exchange: Exchange où acheter
            sell_exchange: Exchange où vendre
            buy_price: Prix d'achat
            sell_price: Prix de vente
            trade_amount_usd: Montant à trader
            buy_fee_type: Type de frais à l'achat
            sell_fee_type: Type de frais à la vente
        
        Returns:
            Dict avec tous les détails du calcul
        
        Example:
            >>> calc = FeeCalculator()
            >>> result = calc.calculate_arbitrage_profit(
            ...     'binance', 'kraken',
            ...     83000, 83500,
            ...     1000
            ... )
            >>> print(f"Profit NET: ${result['net_profit_usd']:.2f}")
        """
        # Calcul de base
        crypto_amount = trade_amount_usd / buy_price
        
        # Frais d'achat
        buy_fee_pct = self.get_trading_fee(buy_exchange, buy_fee_type)
        buy_fee_usd = (trade_amount_usd * buy_fee_pct) / 100
        
        # Frais de vente
        sell_amount_usd = crypto_amount * sell_price
        sell_fee_pct = self.get_trading_fee(sell_exchange, sell_fee_type)
        sell_fee_usd = (sell_amount_usd * sell_fee_pct) / 100
        
        # Calcul du profit
        total_fees_usd = buy_fee_usd + sell_fee_usd
        total_fees_pct = (total_fees_usd / trade_amount_usd) * 100
        
        gross_profit_usd = sell_amount_usd - trade_amount_usd
        gross_profit_pct = (gross_profit_usd / trade_amount_usd) * 100
        
        net_profit_usd = gross_profit_usd - total_fees_usd
        net_profit_pct = (net_profit_usd / trade_amount_usd) * 100
        
        # Résultat détaillé
        result = {
            # Exchanges
            'buy_exchange': buy_exchange,
            'sell_exchange': sell_exchange,
            
            # Prix
            'buy_price': buy_price,
            'sell_price': sell_price,
            'crypto_amount': crypto_amount,
            
            # Montants
            'trade_amount_usd': trade_amount_usd,
            'sell_amount_usd': sell_amount_usd,
            
            # Frais d'achat
            'buy_fee_pct': buy_fee_pct,
            'buy_fee_usd': buy_fee_usd,
            
            # Frais de vente
            'sell_fee_pct': sell_fee_pct,
            'sell_fee_usd': sell_fee_usd,
            
            # Frais totaux
            'total_fees_usd': total_fees_usd,
            'total_fees_pct': total_fees_pct,
            
            # Profit brut (avant frais)
            'gross_profit_usd': gross_profit_usd,
            'gross_profit_pct': gross_profit_pct,
            
            # Profit net (après frais)
            'net_profit_usd': net_profit_usd,
            'net_profit_pct': net_profit_pct,
            
            # Rentabilité
            'is_profitable': net_profit_usd > 0,
            'min_spread_needed_pct': total_fees_pct
        }
        
        self.logger.info(
            f"Arbitrage {buy_exchange}→{sell_exchange}: "
            f"Profit NET ${net_profit_usd:.2f} ({net_profit_pct:+.2f}%)",
            extra={'context': result}
        )
        
        return result
    
    def get_all_fees(self) -> Dict[str, Dict[str, float]]:
        """
        Récupère tous les frais configurés
        
        Returns:
            Dict de tous les frais
        """
        return self.TRADING_FEES.copy()
    
    def compare_exchanges_fees(self) -> list:
        """
        Compare les frais entre exchanges
        
        Returns:
            Liste d'exchanges triés par frais croissants
        """
        exchanges = []
        
        for exchange, fees in self.TRADING_FEES.items():
            avg_fee = (fees['maker'] + fees['taker']) / 2
            exchanges.append({
                'exchange': exchange,
                'maker': fees['maker'],
                'taker': fees['taker'],
                'average': avg_fee
            })
        
        # Trier par frais moyens croissants
        exchanges.sort(key=lambda x: x['average'])
        
        return exchanges
    
    def __repr__(self):
        """Représentation textuelle"""
        return f"<FeeCalculator(exchanges={len(self.TRADING_FEES)})>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST FEE CALCULATOR")
    print("=" * 60)
    
    calculator = FeeCalculator()
    
    # Test 1 : Frais simples
    print("\n1. Frais de trading:")
    print("-" * 60)
    fees_binance = calculator.calculate_trade_fees('binance', 1000, 'taker')
    print(f"Binance - Trade de $1,000")
    print(f"  Frais: {fees_binance['fee_pct']}% = ${fees_binance['fee_usd']:.2f}")
    print(f"  Net: ${fees_binance['net_amount']:.2f}")
    
    # Test 2 : Arbitrage complet
    print("\n2. Calcul d'arbitrage complet:")
    print("-" * 60)
    result = calculator.calculate_arbitrage_profit(
        buy_exchange='binance',
        sell_exchange='kraken',
        buy_price=83000,
        sell_price=83500,
        trade_amount_usd=1000
    )
    
    print(f"Acheter sur {result['buy_exchange']} @ ${result['buy_price']:,.2f}")
    print(f"Vendre sur {result['sell_exchange']} @ ${result['sell_price']:,.2f}")
    print(f"Montant: ${result['trade_amount_usd']:,.2f}")
    print(f"\nCrypto acheté: {result['crypto_amount']:.6f}")
    print(f"\nFrais d'achat: ${result['buy_fee_usd']:.2f} ({result['buy_fee_pct']}%)")
    print(f"Frais de vente: ${result['sell_fee_usd']:.2f} ({result['sell_fee_pct']}%)")
    print(f"Frais totaux: ${result['total_fees_usd']:.2f} ({result['total_fees_pct']:.2f}%)")
    print(f"\nProfit BRUT: ${result['gross_profit_usd']:.2f} ({result['gross_profit_pct']:+.2f}%)")
    print(f"Profit NET: ${result['net_profit_usd']:.2f} ({result['net_profit_pct']:+.2f}%)")
    print(f"\n{'✅ RENTABLE' if result['is_profitable'] else '❌ PAS RENTABLE'}")
    print(f"Spread minimum nécessaire: {result['min_spread_needed_pct']:.2f}%")
    
    # Test 3 : Comparaison exchanges
    print("\n3. Comparaison des frais:")
    print("-" * 60)
    comparison = calculator.compare_exchanges_fees()
    print(f"{'Exchange':<15} {'Maker':<10} {'Taker':<10} {'Moyenne':<10}")
    print("-" * 60)
    for exc in comparison[:5]:  # Top 5 moins chers
        print(f"{exc['exchange']:<15} {exc['maker']:<10.2f}% {exc['taker']:<10.2f}% {exc['average']:<10.2f}%")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
