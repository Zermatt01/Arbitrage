"""
Modèles SQLAlchemy - Base de Données
====================================

Modèles ORM pour toutes les tables de la base de données.

Usage:
    from src.models.database_models import Opportunity, Trade, PriceHistory
    
    # Créer une opportunité
    opportunity = Opportunity(
        symbol='BTC/USDT',
        buy_exchange='binance',
        sell_exchange='kraken',
        ...
    )
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Opportunity(Base):
    """
    Modèle pour la table opportunities
    Stocke toutes les opportunités d'arbitrage détectées
    """
    __tablename__ = 'opportunities'
    
    # ID
    id = Column(Integer, primary_key=True)
    
    # Informations de la paire
    symbol = Column(String(20), nullable=False, index=True)
    
    # Exchanges
    buy_exchange = Column(String(50), nullable=False)
    sell_exchange = Column(String(50), nullable=False)
    
    # Prix
    buy_price = Column(Numeric(20, 8), nullable=False)
    sell_price = Column(Numeric(20, 8), nullable=False)
    
    # Calculs de profit
    spread_percent = Column(Numeric(10, 4), nullable=False)
    gross_profit_percent = Column(Numeric(10, 4), nullable=False)
    net_profit_percent = Column(Numeric(10, 4), nullable=False)
    estimated_profit_usd = Column(Numeric(15, 2))
    
    # Frais
    buy_fee_percent = Column(Numeric(10, 4))
    sell_fee_percent = Column(Numeric(10, 4))
    total_fees_percent = Column(Numeric(10, 4))
    
    # Liquidité
    available_volume = Column(Numeric(20, 8))
    max_trade_amount = Column(Numeric(15, 2))
    
    # Scoring
    score = Column(Integer, default=0, index=True)
    priority = Column(String(20), default='NORMAL')
    
    # Statut
    status = Column(String(20), default='DETECTED', index=True)
    executed = Column(Boolean, default=False)
    
    # Timestamps
    detected_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime)
    executed_at = Column(DateTime)
    
    # Données brutes
    raw_data = Column(JSON)
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, {self.symbol}, {self.buy_exchange}→{self.sell_exchange}, profit={self.net_profit_percent}%)>"
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'buy_exchange': self.buy_exchange,
            'sell_exchange': self.sell_exchange,
            'buy_price': float(self.buy_price) if self.buy_price else None,
            'sell_price': float(self.sell_price) if self.sell_price else None,
            'spread_percent': float(self.spread_percent) if self.spread_percent else None,
            'net_profit_percent': float(self.net_profit_percent) if self.net_profit_percent else None,
            'estimated_profit_usd': float(self.estimated_profit_usd) if self.estimated_profit_usd else None,
            'score': self.score,
            'status': self.status,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }


class Trade(Base):
    """
    Modèle pour la table trades
    Historique de tous les trades exécutés
    """
    __tablename__ = 'trades'
    
    # ID
    id = Column(Integer, primary_key=True)
    
    # Référence à l'opportunité
    opportunity_id = Column(Integer, ForeignKey('opportunities.id', ondelete='SET NULL'))
    
    # Informations de base
    symbol = Column(String(20), nullable=False, index=True)
    trade_type = Column(String(20), nullable=False)
    
    # Exchanges
    buy_exchange = Column(String(50), nullable=False)
    sell_exchange = Column(String(50), nullable=False)
    
    # Ordre d'achat
    buy_order_id = Column(String(100))
    buy_price = Column(Numeric(20, 8), nullable=False)
    buy_amount = Column(Numeric(20, 8), nullable=False)
    buy_total_usd = Column(Numeric(15, 2), nullable=False)
    buy_fee = Column(Numeric(15, 2), default=0)
    buy_status = Column(String(20), default='PENDING')
    buy_executed_at = Column(DateTime)
    
    # Ordre de vente
    sell_order_id = Column(String(100))
    sell_price = Column(Numeric(20, 8), nullable=False)
    sell_amount = Column(Numeric(20, 8), nullable=False)
    sell_total_usd = Column(Numeric(15, 2), nullable=False)
    sell_fee = Column(Numeric(15, 2), default=0)
    sell_status = Column(String(20), default='PENDING')
    sell_executed_at = Column(DateTime)
    
    # Résultats
    gross_profit_usd = Column(Numeric(15, 2))
    total_fees_usd = Column(Numeric(15, 2), default=0)
    net_profit_usd = Column(Numeric(15, 2))
    profit_percent = Column(Numeric(10, 4))
    
    # Statut
    status = Column(String(20), default='PENDING', index=True)
    
    # Timing
    started_at = Column(DateTime, default=func.now(), index=True)
    completed_at = Column(DateTime)
    execution_time_ms = Column(Integer)
    
    # Mode
    dry_run = Column(Boolean, default=True, index=True)
    notes = Column(Text)
    error_message = Column(Text)
    
    # Données brutes
    raw_buy_order = Column(JSON)
    raw_sell_order = Column(JSON)
    
    def __repr__(self):
        return f"<Trade(id={self.id}, {self.symbol}, profit=${self.net_profit_usd}, status={self.status})>"
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'opportunity_id': self.opportunity_id,
            'symbol': self.symbol,
            'trade_type': self.trade_type,
            'buy_exchange': self.buy_exchange,
            'sell_exchange': self.sell_exchange,
            'buy_price': float(self.buy_price) if self.buy_price else None,
            'sell_price': float(self.sell_price) if self.sell_price else None,
            'net_profit_usd': float(self.net_profit_usd) if self.net_profit_usd else None,
            'status': self.status,
            'dry_run': self.dry_run,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class PriceHistory(Base):
    """
    Modèle pour la table price_history
    Historique des prix collectés
    """
    __tablename__ = 'price_history'
    
    # ID
    id = Column(Integer, primary_key=True)
    
    # Informations
    exchange = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Prix
    bid = Column(Numeric(20, 8), nullable=False)
    ask = Column(Numeric(20, 8), nullable=False)
    last = Column(Numeric(20, 8))
    
    # Spread
    spread = Column(Numeric(20, 8))
    spread_percent = Column(Numeric(10, 4))
    
    # Volume
    volume_24h = Column(Numeric(20, 8))
    quote_volume_24h = Column(Numeric(20, 2))
    
    # Métadonnées
    collected_at = Column(DateTime, default=func.now(), index=True)
    source = Column(String(20), default='API')
    
    # Données brutes
    raw_data = Column(JSON)
    
    def __repr__(self):
        return f"<PriceHistory({self.exchange}, {self.symbol}, bid={self.bid}, ask={self.ask})>"
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'exchange': self.exchange,
            'symbol': self.symbol,
            'bid': float(self.bid) if self.bid else None,
            'ask': float(self.ask) if self.ask else None,
            'last': float(self.last) if self.last else None,
            'spread_percent': float(self.spread_percent) if self.spread_percent else None,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }


class ExchangeStatus(Base):
    """
    Modèle pour la table exchange_status
    Statut et santé de chaque exchange
    """
    __tablename__ = 'exchange_status'
    
    # ID
    id = Column(Integer, primary_key=True)
    
    # Exchange
    exchange_name = Column(String(50), nullable=False, unique=True)
    
    # Statut
    is_online = Column(Boolean, default=True, index=True)
    is_api_working = Column(Boolean, default=True)
    is_websocket_working = Column(Boolean, default=False)
    
    # Performance
    average_latency_ms = Column(Integer)
    last_successful_request_at = Column(DateTime)
    last_failed_request_at = Column(DateTime)
    consecutive_failures = Column(Integer, default=0)
    
    # Rate limiting
    rate_limit_remaining = Column(Integer)
    rate_limit_reset_at = Column(DateTime)
    
    # Métadonnées
    last_checked_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Erreurs
    last_error_message = Column(Text)
    error_count_24h = Column(Integer, default=0)
    
    # Configuration
    is_enabled = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=50)
    notes = Column(Text)
    
    def __repr__(self):
        status = "online" if self.is_online else "offline"
        return f"<ExchangeStatus({self.exchange_name}, {status})>"
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'exchange_name': self.exchange_name,
            'is_online': self.is_online,
            'is_api_working': self.is_api_working,
            'average_latency_ms': self.average_latency_ms,
            'consecutive_failures': self.consecutive_failures,
            'is_enabled': self.is_enabled,
            'last_checked_at': self.last_checked_at.isoformat() if self.last_checked_at else None
        }


class SystemLog(Base):
    """
    Modèle pour la table system_logs
    Logs du système
    """
    __tablename__ = 'system_logs'
    
    # ID
    id = Column(Integer, primary_key=True)
    
    # Niveau
    level = Column(String(20), nullable=False, index=True)
    
    # Source
    module = Column(String(100), index=True)
    function_name = Column(String(100))
    
    # Message
    message = Column(Text, nullable=False)
    
    # Contexte
    context = Column(JSON)
    stack_trace = Column(Text)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), index=True)
    environment = Column(String(20), default='development')
    
    def __repr__(self):
        return f"<SystemLog({self.level}, {self.module}, {self.message[:50]}...)>"
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Helper pour créer toutes les tables
def create_all_tables(engine):
    """
    Crée toutes les tables dans la base de données
    
    Usage:
        from sqlalchemy import create_engine
        from src.models.database_models import create_all_tables
        
        engine = create_engine('postgresql://...')
        create_all_tables(engine)
    """
    Base.metadata.create_all(engine)
    print("✅ Toutes les tables ont été créées")


# Helper pour supprimer toutes les tables
def drop_all_tables(engine):
    """
    Supprime toutes les tables (ATTENTION: perte de données!)
    """
    Base.metadata.drop_all(engine)
    print("⚠️  Toutes les tables ont été supprimées")
# ============================================================
# CONFIGURATION DE LA BASE DE DONNÉES
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    # Importer la configuration
    from config.config import Config
    
    # Créer l'engine
    engine = create_engine(
        f'postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}',
        echo=False,  # Mettre True pour voir les requêtes SQL
        pool_pre_ping=True  # Vérifier la connexion avant utilisation
    )
    
    # Créer la session factory
    Session = sessionmaker(bind=engine)
    
    print("✅ Base de données connectée")
    
except Exception as e:
    print(f"⚠️  Erreur de connexion à la base de données: {e}")
    engine = None
    Session = None