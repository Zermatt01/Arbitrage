"""
Migration - Table daily_performance
====================================

Crée la table pour stocker les performances quotidiennes.
"""

import psycopg2
from src.database.db_connection import get_db_connection


def create_daily_performance_table():
    """Crée la table daily_performance"""
    print("=" * 60)
    print("  CRÉATION TABLE DAILY_PERFORMANCE")
    print("=" * 60)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Créer la table
        print("\n📝 Création de la table...")
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS daily_performance (
            id SERIAL PRIMARY KEY,
            date DATE UNIQUE NOT NULL,
            
            -- Compteurs
            trades_count INTEGER DEFAULT 0,
            wins_count INTEGER DEFAULT 0,
            losses_count INTEGER DEFAULT 0,
            win_rate_pct NUMERIC(5, 2) DEFAULT 0,
            
            -- Profit/Perte
            total_profit_usd NUMERIC(12, 2) DEFAULT 0,
            total_loss_usd NUMERIC(12, 2) DEFAULT 0,
            net_pnl_usd NUMERIC(12, 2) DEFAULT 0,
            
            -- Meilleurs/Pires
            best_trade_usd NUMERIC(12, 2) DEFAULT 0,
            worst_trade_usd NUMERIC(12, 2) DEFAULT 0,
            
            -- Séries
            max_win_streak INTEGER DEFAULT 0,
            max_loss_streak INTEGER DEFAULT 0,
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """
        
        cursor.execute(create_table_query)
        print("✅ Table créée")
        
        # Créer les index
        print("\n📝 Création des index...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_daily_performance_date ON daily_performance(date DESC)",
        ]
        
        for idx_query in indexes:
            cursor.execute(idx_query)
        
        print("✅ Index créés")
        
        # Commit
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ Table daily_performance créée avec succès !")
        print("=" * 60)
        
        # Vérifier
        print("\n📊 Vérification de la structure:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'daily_performance'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        print(f"\n{'Colonne':<25} {'Type':<20}")
        print("-" * 50)
        for col_name, col_type in columns:
            print(f"{col_name:<25} {col_type:<20}")
        
        print(f"\n✅ Total: {len(columns)} colonnes")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_daily_performance_table()
    
    if success:
        print("\n🎉 Migration réussie !")
        print("💡 Vous pouvez maintenant lancer: python test_etape_4.3.py")
    else:
        print("\n❌ Migration échouée")
