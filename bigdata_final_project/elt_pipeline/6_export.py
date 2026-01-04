import pandas as pd
import os
from config import OUTPUT_DIR
from db_utils import get_engine

TABLES_TO_EXPORT = [
    'mart_inflation_analysis', 'fact_sales', 'dim_products', 'dim_customers'
]

def export_tables():
    engine = get_engine()
    print("\n--- MULAI EXPORT TABEL KE CSV ---\n")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Membuat folder: {OUTPUT_DIR}")
    
    for table in TABLES_TO_EXPORT:
        print(f"💾 Exporting: {table}...", end=" ")
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", engine)
            filename = os.path.join(OUTPUT_DIR, f"{table}.csv")
            df.to_csv(filename, index=False)
            print(f"✅ Sukses! ({len(df)} baris)")
        except Exception as e:
            print(f"❌ GAGAL: {e}")

if __name__ == "__main__":
    export_tables()