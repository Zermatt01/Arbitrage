"""
Opportunity Database Manager - Gestion des Opportunités en DB
==============================================================

Sauvegarde et récupère les opportunités d'arbitrage depuis PostgreSQL.

Usage:
    from src.database.opportunity_db import OpportunityDB
    
    db = OpportunityDB()
    db.save_opportunity(opportunity)
    opportunities = db.get_recent_opportunities(limit=10)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from src.database.db_connection import get_db_connection
from src.utils.logger import get_logger


class OpportunityDB:
    """
    Gère la sauvegarde et récupération des opportunités en base de données
    """
    
    def __init__(self):
        """Initialise le gestionnaire de DB"""
        self.logger = get_logger(__name__)
        self.logger.debug("OpportunityDB initialisé")
    
    def save_opportunity(
        self,
        opportunity: Dict[str, Any],
        status: str = 'detected'
    ) -> Optional[int]:
        """
        Sauvegarde une opportunité en base de données
        
        Args:
            opportunity: Dict avec les données de l'opportunité
            status: Statut (detected, executed, expired, rejected)
        
        Returns:
            ID de l'opportunité créée ou None si erreur
        
        Example:
            >>> db = OpportunityDB()
            >>> opp_id = db.save_opportunity({
            ...     'symbol': 'BTC/USDT',
            ...     'exchange_buy': 'binance',
            ...     'exchange_sell': 'kraken',
            ...     'buy_price': 81235.45,
            ...     'sell_price': 81500.00,
            ...     'spread_pct': 0.33,
            ...     'net_profit_pct': 0.24,
            ...     'total_score': 87.5
            ... })
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Préparer les données
            symbol = opportunity.get('symbol', 'UNKNOWN')
            exchange_buy = opportunity.get('exchange_buy', '')
            exchange_sell = opportunity.get('exchange_sell', '')
            buy_price = float(opportunity.get('buy_price', 0))
            sell_price = float(opportunity.get('sell_price', 0))
            
            # Spreads et profits
            spread_pct = float(opportunity.get('spread_pct', 0))
            net_profit_pct = float(opportunity.get('net_profit_real_pct', 
                                                   opportunity.get('net_profit_pct', 0)))
            
            # Frais et slippage
            total_fees_pct = float(opportunity.get('total_fees_pct', 0))
            total_slippage_pct = float(opportunity.get('total_slippage_pct', 0))
            
            # Liquidité
            liquidity_valid = opportunity.get('liquidity_valid', None)
            
            # Score
            total_score = float(opportunity.get('total_score', 0))
            grade = opportunity.get('grade', '')
            
            # Métadonnées JSON
            metadata = {
                'scores': opportunity.get('scores', {}),
                'buy_slippage_pct': opportunity.get('buy_slippage_pct', 0),
                'sell_slippage_pct': opportunity.get('sell_slippage_pct', 0),
                'liquidity_reason': opportunity.get('liquidity_reason', '')
            }
            
            # Requête SQL
            query = """
                INSERT INTO opportunities (
                    symbol,
                    exchange_buy,
                    exchange_sell,
                    buy_price,
                    sell_price,
                    spread_pct,
                    net_profit_pct,
                    total_fees_pct,
                    total_slippage_pct,
                    liquidity_valid,
                    total_score,
                    grade,
                    status,
                    metadata,
                    detected_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, NOW()
                )
                RETURNING id
            """
            
            cursor.execute(query, (
                symbol,
                exchange_buy,
                exchange_sell,
                buy_price,
                sell_price,
                spread_pct,
                net_profit_pct,
                total_fees_pct,
                total_slippage_pct,
                liquidity_valid,
                total_score,
                grade,
                status,
                psycopg2.extras.Json(metadata)
            ))
            
            opp_id = cursor.fetchone()[0]
            conn.commit()
            
            self.logger.info(
                f"Opportunité sauvegardée: {symbol} {exchange_buy}→{exchange_sell} "
                f"(ID: {opp_id}, Score: {total_score:.1f})",
                extra={'context': {
                    'id': opp_id,
                    'symbol': symbol,
                    'net_profit_pct': net_profit_pct,
                    'total_score': total_score
                }}
            )
            
            cursor.close()
            conn.close()
            
            return opp_id
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde opportunité: {e}", exc_info=True)
            return None
    
    def save_opportunities_batch(
        self,
        opportunities: List[Dict[str, Any]],
        status: str = 'detected'
    ) -> int:
        """
        Sauvegarde plusieurs opportunités en batch
        
        Args:
            opportunities: Liste d'opportunités
            status: Statut commun
        
        Returns:
            Nombre d'opportunités sauvegardées
        """
        count = 0
        
        for opp in opportunities:
            opp_id = self.save_opportunity(opp, status)
            if opp_id:
                count += 1
        
        self.logger.info(
            f"{count}/{len(opportunities)} opportunités sauvegardées",
            extra={'context': {'saved': count, 'total': len(opportunities)}}
        )
        
        return count
    
    def get_recent_opportunities(
        self,
        limit: int = 10,
        min_score: float = 0
    ) -> List[Dict[str, Any]]:
        """
        Récupère les opportunités récentes
        
        Args:
            limit: Nombre maximum d'opportunités
            min_score: Score minimum
        
        Returns:
            Liste d'opportunités
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT *
                FROM opportunities
                WHERE total_score >= %s
                ORDER BY detected_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (min_score, limit))
            opportunities = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convertir en liste de dicts
            result = [dict(opp) for opp in opportunities]
            
            self.logger.debug(
                f"{len(result)} opportunités récupérées (score >= {min_score})",
                extra={'context': {'count': len(result), 'min_score': min_score}}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur récupération opportunités: {e}", exc_info=True)
            return []
    
    def get_opportunities_by_symbol(
        self,
        symbol: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Récupère les opportunités pour un symbole donné
        
        Args:
            symbol: Paire de trading (ex: BTC/USDT)
            hours: Nombre d'heures dans le passé
        
        Returns:
            Liste d'opportunités
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT *
                FROM opportunities
                WHERE symbol = %s
                  AND detected_at >= NOW() - INTERVAL '%s hours'
                ORDER BY detected_at DESC
            """
            
            cursor.execute(query, (symbol, hours))
            opportunities = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            result = [dict(opp) for opp in opportunities]
            
            self.logger.debug(
                f"{len(result)} opportunités pour {symbol} (dernières {hours}h)",
                extra={'context': {'symbol': symbol, 'count': len(result)}}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur récupération par symbole: {e}", exc_info=True)
            return []
    
    def get_opportunities_by_route(
        self,
        exchange_buy: str,
        exchange_sell: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Récupère les opportunités pour une route donnée
        
        Args:
            exchange_buy: Exchange d'achat
            exchange_sell: Exchange de vente
            hours: Nombre d'heures dans le passé
        
        Returns:
            Liste d'opportunités
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT *
                FROM opportunities
                WHERE exchange_buy = %s
                  AND exchange_sell = %s
                  AND detected_at >= NOW() - INTERVAL '%s hours'
                ORDER BY detected_at DESC
            """
            
            cursor.execute(query, (exchange_buy, exchange_sell, hours))
            opportunities = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            result = [dict(opp) for opp in opportunities]
            
            self.logger.debug(
                f"{len(result)} opportunités {exchange_buy}→{exchange_sell} (dernières {hours}h)",
                extra={'context': {
                    'route': f"{exchange_buy}→{exchange_sell}",
                    'count': len(result)
                }}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur récupération par route: {e}", exc_info=True)
            return []
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calcule des statistiques sur les opportunités
        
        Args:
            hours: Période en heures
        
        Returns:
            Dict avec statistiques
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT
                    COUNT(*) as total_opportunities,
                    COUNT(CASE WHEN total_score >= 80 THEN 1 END) as grade_a_or_better,
                    COUNT(CASE WHEN total_score >= 70 THEN 1 END) as grade_b_or_better,
                    COUNT(CASE WHEN liquidity_valid = true THEN 1 END) as with_liquidity,
                    AVG(net_profit_pct) as avg_profit_pct,
                    MAX(net_profit_pct) as max_profit_pct,
                    AVG(total_score) as avg_score,
                    MAX(total_score) as max_score
                FROM opportunities
                WHERE detected_at >= NOW() - INTERVAL '%s hours'
            """
            
            cursor.execute(query, (hours,))
            stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            result = dict(stats) if stats else {}
            
            self.logger.info(
                f"Statistiques calculées pour les dernières {hours}h",
                extra={'context': result}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur calcul statistiques: {e}", exc_info=True)
            return {}
    
    def get_top_routes(self, limit: int = 5, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Récupère les meilleures routes (exchange pairs)
        
        Args:
            limit: Nombre de routes à retourner
            hours: Période en heures
        
        Returns:
            Liste des meilleures routes
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT
                    exchange_buy,
                    exchange_sell,
                    COUNT(*) as opportunity_count,
                    AVG(net_profit_pct) as avg_profit_pct,
                    AVG(total_score) as avg_score
                FROM opportunities
                WHERE detected_at >= NOW() - INTERVAL '%s hours'
                GROUP BY exchange_buy, exchange_sell
                ORDER BY avg_score DESC
                LIMIT %s
            """
            
            cursor.execute(query, (hours, limit))
            routes = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            result = [dict(route) for route in routes]
            
            self.logger.debug(
                f"Top {len(result)} routes récupérées",
                extra={'context': {'count': len(result)}}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur récupération top routes: {e}", exc_info=True)
            return []
    
    def update_opportunity_status(
        self,
        opp_id: int,
        status: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Met à jour le statut d'une opportunité
        
        Args:
            opp_id: ID de l'opportunité
            status: Nouveau statut (executed, expired, rejected)
            metadata: Métadonnées additionnelles
        
        Returns:
            True si succès
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if metadata:
                query = """
                    UPDATE opportunities
                    SET status = %s,
                        metadata = metadata || %s
                    WHERE id = %s
                """
                cursor.execute(query, (status, psycopg2.extras.Json(metadata), opp_id))
            else:
                query = """
                    UPDATE opportunities
                    SET status = %s
                    WHERE id = %s
                """
                cursor.execute(query, (status, opp_id))
            
            conn.commit()
            
            self.logger.info(
                f"Opportunité {opp_id} mise à jour: {status}",
                extra={'context': {'id': opp_id, 'status': status}}
            )
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour opportunité: {e}", exc_info=True)
            return False
    
    def delete_old_opportunities(self, days: int = 30) -> int:
        """
        Supprime les opportunités anciennes
        
        Args:
            days: Nombre de jours à garder
        
        Returns:
            Nombre d'opportunités supprimées
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                DELETE FROM opportunities
                WHERE detected_at < NOW() - INTERVAL '%s days'
            """
            
            cursor.execute(query, (days,))
            deleted_count = cursor.rowcount
            conn.commit()
            
            self.logger.info(
                f"{deleted_count} opportunités anciennes supprimées (> {days} jours)",
                extra={'context': {'deleted': deleted_count, 'days': days}}
            )
            
            cursor.close()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Erreur suppression opportunités: {e}", exc_info=True)
            return 0
    
    def __repr__(self):
        """Représentation textuelle"""
        return "<OpportunityDB()>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST OPPORTUNITY DATABASE")
    print("=" * 60)
    
    db = OpportunityDB()
    
    # Exemple d'opportunité
    opportunity = {
        'symbol': 'BTC/USDT',
        'exchange_buy': 'binance',
        'exchange_sell': 'kraken',
        'buy_price': 81235.45,
        'sell_price': 81500.00,
        'spread_pct': 0.33,
        'net_profit_pct': 0.24,
        'total_fees_pct': 0.36,
        'total_slippage_pct': 0.10,
        'liquidity_valid': True,
        'total_score': 87.5,
        'grade': 'A',
        'scores': {
            'profit': 30.0,
            'liquidity': 28.5,
            'reliability': 18.5,
            'speed': 10.5
        }
    }
    
    # Sauvegarder
    print("\n📝 Sauvegarde opportunité...")
    opp_id = db.save_opportunity(opportunity)
    print(f"✅ Opportunité sauvegardée (ID: {opp_id})")
    
    # Récupérer récentes
    print("\n📊 Récupération opportunités récentes...")
    recent = db.get_recent_opportunities(limit=5)
    print(f"✅ {len(recent)} opportunités récupérées")
    
    # Statistiques
    print("\n📈 Statistiques...")
    stats = db.get_statistics(hours=24)
    print(f"✅ Total opportunités (24h): {stats.get('total_opportunities', 0)}")
    print(f"✅ Score moyen: {stats.get('avg_score', 0):.1f}/100")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
