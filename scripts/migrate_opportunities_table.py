"""
Script de Migration - Table Opportunities
==========================================

Recrée la table opportunities avec le bon schéma pour l'étape 3.6.
"""

import psycopg2
from src.database.db_connection import get_db_connection


def update_opportunities_table():
    """
    Supprime et recrée la table opportunities avec le nouveau schéma
    """
    print("=" * 60)
    print("  MISE À JOUR TABLE OPPORTUNITIES")
    print("=" * 60)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Supprimer l'ancienne table
        print("\n1️⃣  Suppression de l'ancienne table...")
        cursor.execute("DROP TABLE IF EXISTS opportunities CASCADE")
        print("✅ Ancienne table supprimée")
        
        # 2. Créer la nouvelle table
        print("\n2️⃣  Création de la nouvelle table...")
        
        create_table_query = """
        CREATE TABLE opportunities (
            id SERIAL PRIMARY KEY,
            
            -- Informations de base
            symbol VARCHAR(20) NOT NULL,
            exchange_buy VARCHAR(50) NOT NULL,
            exchange_sell VARCHAR(50) NOT NULL,
            
            -- Prix
            buy_price NUMERIC(20, 8) NOT NULL,
            sell_price NUMERIC(20, 8) NOT NULL,
            
            -- Spreads et profits
            spread_pct NUMERIC(10, 4),
            net_profit_pct NUMERIC(10, 4),
            
            -- Frais et slippage
            total_fees_pct NUMERIC(10, 4),
            total_slippage_pct NUMERIC(10, 4),
            
            -- Liquidité
            liquidity_valid BOOLEAN,
            
            -- Scoring
            total_score NUMERIC(5, 2),
            grade VARCHAR(2),
            
            -- Statut
            status VARCHAR(20) DEFAULT 'detected',
            
            -- Métadonnées JSON
            metadata JSONB,
            
            -- Timestamps
            detected_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """
        
        cursor.execute(create_table_query)
        print("✅ Nouvelle table créée")
        
        # 3. Créer les index
        print("\n3️⃣  Création des index...")
        
        indexes = [
            "CREATE INDEX idx_opportunities_symbol ON opportunities(symbol)",
            "CREATE INDEX idx_opportunities_exchanges ON opportunities(exchange_buy, exchange_sell)",
            "CREATE INDEX idx_opportunities_score ON opportunities(total_score)",
            "CREATE INDEX idx_opportunities_detected_at ON opportunities(detected_at)",
            "CREATE INDEX idx_opportunities_status ON opportunities(status)",
        ]
        
        for idx_query in indexes:
            cursor.execute(idx_query)
        
        print("✅ Index créés")
        
        # 4. Commit
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ Table opportunities mise à jour avec succès !")
        print("=" * 60)
        
        # 5. Vérifier
        print("\n📊 Vérification de la structure:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'opportunities'
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
    success = update_opportunities_table()
    
    if success:
        print("\n🎉 Migration réussie !")
        print("💡 Vous pouvez maintenant lancer: python test_etape_3.6.py")
    else:
        print("\n❌ Migration échouée")
