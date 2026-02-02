#!/usr/bin/env python3
"""
Script de test du schéma de base de données - Étape 1.5
=======================================================

Vérifie que toutes les tables sont créées et fonctionnelles.

Usage:
    python test_schema.py
"""

import sys
from datetime import datetime
from decimal import Decimal


def print_header(text):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Affiche un message de succès"""
    print(f"✅ {text}")


def print_error(text):
    """Affiche un message d'erreur"""
    print(f"❌ {text}")


def print_info(text):
    """Affiche une information"""
    print(f"ℹ️  {text}")


def test_tables_exist():
    """Vérifie que toutes les tables existent"""
    print_header("Test Existence des Tables")
    
    try:
        from sqlalchemy import create_engine, inspect, text
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'opportunities',
            'trades',
            'price_history',
            'exchange_status',
            'system_logs'
        ]
        
        all_exist = True
        for table in required_tables:
            if table in tables:
                print_success(f"Table '{table}' existe")
            else:
                print_error(f"Table '{table}' manquante")
                all_exist = False
        
        if all_exist:
            print_success(f"✨ Toutes les tables ({len(required_tables)}) existent")
        
        return all_exist
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_table_structure():
    """Vérifie la structure des tables"""
    print_header("Test Structure des Tables")
    
    try:
        from sqlalchemy import create_engine, inspect
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        inspector = inspect(engine)
        
        # Tester la structure de opportunities
        columns = [col['name'] for col in inspector.get_columns('opportunities')]
        required_columns = ['id', 'symbol', 'buy_exchange', 'sell_exchange', 'net_profit_percent', 'status']
        
        all_present = all(col in columns for col in required_columns)
        
        if all_present:
            print_success(f"Table 'opportunities': {len(columns)} colonnes")
            print_info(f"  Colonnes clés présentes: {', '.join(required_columns)}")
        else:
            print_error("Certaines colonnes manquent dans 'opportunities'")
        
        # Tester les index
        indexes = inspector.get_indexes('opportunities')
        print_info(f"  Index créés: {len(indexes)}")
        
        return all_present
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_insert_opportunity():
    """Teste l'insertion d'une opportunité"""
    print_header("Test Insertion Opportunité")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Insérer une opportunité de test
        insert_query = text("""
            INSERT INTO opportunities (
                symbol, buy_exchange, sell_exchange, 
                buy_price, sell_price, 
                spread_percent, gross_profit_percent, net_profit_percent,
                estimated_profit_usd, score, status
            ) VALUES (
                :symbol, :buy_exchange, :sell_exchange,
                :buy_price, :sell_price,
                :spread_percent, :gross_profit_percent, :net_profit_percent,
                :estimated_profit_usd, :score, :status
            )
            RETURNING id
        """)
        
        result = session.execute(insert_query, {
            'symbol': 'BTC/USDT',
            'buy_exchange': 'binance',
            'sell_exchange': 'kraken',
            'buy_price': Decimal('45000.00'),
            'sell_price': Decimal('45500.00'),
            'spread_percent': Decimal('1.11'),
            'gross_profit_percent': Decimal('1.11'),
            'net_profit_percent': Decimal('0.91'),
            'estimated_profit_usd': Decimal('45.50'),
            'score': 75,
            'status': 'DETECTED'
        })
        
        opportunity_id = result.scalar()
        session.commit()
        
        print_success(f"Opportunité insérée avec ID: {opportunity_id}")
        
        # Lire l'opportunité
        select_query = text("SELECT * FROM opportunities WHERE id = :id")
        result = session.execute(select_query, {'id': opportunity_id})
        row = result.fetchone()
        
        if row:
            print_success(f"Opportunité lue: {row.symbol} ({row.buy_exchange} → {row.sell_exchange})")
            print_info(f"  Profit net: {row.net_profit_percent}%")
        
        # Nettoyer
        delete_query = text("DELETE FROM opportunities WHERE id = :id")
        session.execute(delete_query, {'id': opportunity_id})
        session.commit()
        print_success("Opportunité de test supprimée")
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_insert_trade():
    """Teste l'insertion d'un trade"""
    print_header("Test Insertion Trade")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Insérer un trade de test
        insert_query = text("""
            INSERT INTO trades (
                symbol, trade_type, buy_exchange, sell_exchange,
                buy_price, buy_amount, buy_total_usd,
                sell_price, sell_amount, sell_total_usd,
                net_profit_usd, status, dry_run
            ) VALUES (
                :symbol, :trade_type, :buy_exchange, :sell_exchange,
                :buy_price, :buy_amount, :buy_total_usd,
                :sell_price, :sell_amount, :sell_total_usd,
                :net_profit_usd, :status, :dry_run
            )
            RETURNING id
        """)
        
        result = session.execute(insert_query, {
            'symbol': 'ETH/USDT',
            'trade_type': 'ARBITRAGE_SPATIAL',
            'buy_exchange': 'binance',
            'sell_exchange': 'kraken',
            'buy_price': Decimal('3000.00'),
            'buy_amount': Decimal('0.1'),
            'buy_total_usd': Decimal('300.00'),
            'sell_price': Decimal('3020.00'),
            'sell_amount': Decimal('0.1'),
            'sell_total_usd': Decimal('302.00'),
            'net_profit_usd': Decimal('1.50'),
            'status': 'COMPLETED',
            'dry_run': True
        })
        
        trade_id = result.scalar()
        session.commit()
        
        print_success(f"Trade inséré avec ID: {trade_id}")
        
        # Lire le trade
        select_query = text("SELECT * FROM trades WHERE id = :id")
        result = session.execute(select_query, {'id': trade_id})
        row = result.fetchone()
        
        if row:
            print_success(f"Trade lu: {row.symbol} (profit: ${row.net_profit_usd})")
            print_info(f"  Mode: {'DRY-RUN' if row.dry_run else 'RÉEL'}")
        
        # Nettoyer
        delete_query = text("DELETE FROM trades WHERE id = :id")
        session.execute(delete_query, {'id': trade_id})
        session.commit()
        print_success("Trade de test supprimé")
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_insert_price():
    """Teste l'insertion d'un prix"""
    print_header("Test Insertion Prix")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Insérer un prix de test
        insert_query = text("""
            INSERT INTO price_history (
                exchange, symbol, bid, ask, last, volume_24h
            ) VALUES (
                :exchange, :symbol, :bid, :ask, :last, :volume_24h
            )
            RETURNING id
        """)
        
        result = session.execute(insert_query, {
            'exchange': 'binance',
            'symbol': 'BTC/USDT',
            'bid': Decimal('45000.00'),
            'ask': Decimal('45001.00'),
            'last': Decimal('45000.50'),
            'volume_24h': Decimal('1234.5678')
        })
        
        price_id = result.scalar()
        session.commit()
        
        print_success(f"Prix inséré avec ID: {price_id}")
        
        # Nettoyer
        delete_query = text("DELETE FROM price_history WHERE id = :id")
        session.execute(delete_query, {'id': price_id})
        session.commit()
        print_success("Prix de test supprimé")
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_exchange_status():
    """Teste la table exchange_status"""
    print_header("Test Exchange Status")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Lire les exchanges initiaux
        select_query = text("SELECT * FROM exchange_status ORDER BY priority DESC")
        result = session.execute(select_query)
        rows = result.fetchall()
        
        print_success(f"{len(rows)} exchange(s) configuré(s)")
        
        for row in rows:
            status = "🟢" if row.is_online else "🔴"
            print_info(f"  {status} {row.exchange_name} (priorité: {row.priority})")
        
        session.close()
        return len(rows) > 0
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_views():
    """Teste les vues créées"""
    print_header("Test Vues")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Tester active_exchanges
        query = text("SELECT * FROM active_exchanges")
        result = session.execute(query)
        rows = result.fetchall()
        
        print_success(f"Vue 'active_exchanges': {len(rows)} exchange(s) actif(s)")
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_sqlalchemy_models():
    """Teste les modèles SQLAlchemy"""
    print_header("Test Modèles SQLAlchemy")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        # Importer les modèles (ils doivent être dans src/models/)
        # Pour l'instant on skip ce test car le fichier n'est pas encore dans le projet
        print_info("Les modèles SQLAlchemy seront testés une fois intégrés au projet")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_database_stats():
    """Affiche des statistiques sur la base de données"""
    print_header("Statistiques Base de Données")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from config.config import Config
        
        engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Nombre de tables
        query = text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        result = session.execute(query)
        table_count = result.scalar()
        print_info(f"Nombre de tables: {table_count}")
        
        # Taille de la base de données
        query = text("SELECT pg_size_pretty(pg_database_size(:dbname))")
        result = session.execute(query, {'dbname': 'arbitrage_db'})
        db_size = result.scalar()
        print_info(f"Taille de la base: {db_size}")
        
        # Nombre de vues
        query = text("""
            SELECT COUNT(*) 
            FROM information_schema.views 
            WHERE table_schema = 'public'
        """)
        result = session.execute(query)
        view_count = result.scalar()
        print_info(f"Nombre de vues: {view_count}")
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def print_summary(results):
    """Affiche le résumé des tests"""
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n✅ Tests réussis: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 Schéma de base de données complètement fonctionnel!")
        print("\n📋 Prochaines étapes:")
        print("  1. L'Étape 1.5 est COMPLÈTE ✅")
        print("  2. Vous pouvez passer à l'Étape 1.6")
        print("  3. Dites 'Étape 1.6' pour configurer le logging")
        
        print("\n📊 Tables créées:")
        print("  - opportunities (opportunités d'arbitrage)")
        print("  - trades (historique des trades)")
        print("  - price_history (historique des prix)")
        print("  - exchange_status (statut des exchanges)")
        print("  - system_logs (logs système)")
        
        print("\n🔍 Vues disponibles:")
        print("  - recent_profitable_opportunities")
        print("  - daily_trade_stats")
        print("  - active_exchanges")
        
        return True
    else:
        print_error("❌ Certains tests ont échoué")
        print("\n🔧 Actions requises:")
        
        for test_name, result in results.items():
            if not result:
                print(f"  - Corriger: {test_name}")
        
        return False


def main():
    """Fonction principale"""
    print("\n" + "🗄️  TEST SCHÉMA BASE DE DONNÉES - ÉTAPE 1.5".center(60))
    
    results = {
        "Tables existent": test_tables_exist(),
        "Structure des tables": test_table_structure(),
        "Insertion opportunité": test_insert_opportunity(),
        "Insertion trade": test_insert_trade(),
        "Insertion prix": test_insert_price(),
        "Exchange status": test_exchange_status(),
        "Vues SQL": test_views(),
        "Statistiques": test_database_stats()
    }
    
    success = print_summary(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
