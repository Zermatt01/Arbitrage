"""
Migration - Table trades
=========================

Crée la table pour stocker l'historique des trades (réels et dry-run).
"""

import psycopg2
from src.database.db_connection import get_db_connection


def create_trades_table():
    """Crée la table trades"""
    print("=" * 60)
    print("  CRÉATION TABLE TRADES")
    print("=" * 60)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Supprimer l'ancienne table si elle existe
        print("\n🗑️  Suppression de l'ancienne table (si existe)...")
        cursor.execute("DROP TABLE IF EXISTS trades CASCADE")
        print("✅ Ancienne table supprimée")
        
        # Créer la table
        print("\n📝 Création de la nouvelle table...")
        
        create_table_query = """
        CREATE TABLE trades (
            id SERIAL PRIMARY KEY,
            
            -- Informations du trade
            symbol VARCHAR(20) NOT NULL,
            exchange_buy VARCHAR(50) NOT NULL,
            exchange_sell VARCHAR(50) NOT NULL,
            
            -- Prix
            buy_price NUMERIC(20, 8) NOT NULL,
            sell_price NUMERIC(20, 8) NOT NULL,
            quantity NUMERIC(20, 8) NOT NULL,
            
            -- Profit/Perte
            gross_profit_usd NUMERIC(12, 2),
            net_profit_usd NUMERIC(12, 2),
            total_fees_usd NUMERIC(12, 2),
            
            -- Performance
            execution_time_seconds NUMERIC(10, 3),
            
            -- Mode
            dry_run BOOLEAN DEFAULT FALSE,
            
            -- Métadonnées JSON
            metadata JSONB,
            
            -- Timestamps
            executed_at TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW()
        )
        """
        
        cursor.execute(create_table_query)
        print("✅ Table créée")
        
        # Créer les index
        print("\n📝 Création des index...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trades_executed_at ON trades(executed_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_trades_dry_run ON trades(dry_run)",
            "CREATE INDEX IF NOT EXISTS idx_trades_exchanges ON trades(exchange_buy, exchange_sell)",
        ]
        
        for idx_query in indexes:
            cursor.execute(idx_query)
        
        print("✅ Index créés")
        
        # Commit
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ Table trades créée avec succès !")
        print("=" * 60)
        
        # Vérifier
        print("\n📊 Vérification de la structure:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'trades'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        print(f"\n{'Colonne':<30} {'Type':<20}")
        print("-" * 55)
        for col_name, col_type in columns:
            print(f"{col_name:<30} {col_type:<20}")
        
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
    success = create_trades_table()
    
    if success:
        print("\n🎉 Migration réussie !")
        print("💡 Vous pouvez maintenant lancer: python test_etape_5.1.py")
    else:
        print("\n❌ Migration échouée")
