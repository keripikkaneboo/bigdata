import pandas as pd
import os
from sqlalchemy import text
from config import DATASET_DIR
from db_utils import get_engine, DB_NAME

FILES_MAPPING = {
    'olist_customers_dataset.csv': 'raw_customers',
    'olist_geolocation_dataset.csv': 'raw_geolocation',
    'olist_order_items_dataset.csv': 'raw_order_items',
    'olist_order_payments_dataset.csv': 'raw_order_payments',
    'olist_order_reviews_dataset.csv': 'raw_order_reviews',
    'olist_orders_dataset.csv': 'raw_orders',
    'olist_products_dataset.csv': 'raw_products',
    'olist_sellers_dataset.csv': 'raw_sellers',
    'product_category_name_translation.csv': 'raw_category_translation',
    'brazil.inflation.monthly (statbureau.org).csv': 'raw_brazil_inflation'
}

def load_raw_data():
    # Koneksi root untuk create DB
    engine_root = get_engine(with_db=False)
    with engine_root.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    
    # Koneksi ke DB spesifik
    engine = get_engine(with_db=True)
    print("\n--- MULAI PROSES ELT: PHASE 1 (INGEST RAW DATA) ---")

    for csv_file, table_name in FILES_MAPPING.items():
        file_path = os.path.join(DATASET_DIR, csv_file)
        
        if not os.path.exists(file_path):
            print(f"⚠️  SKIP: File {csv_file} tidak ditemukan.")
            continue
            
        print(f"📂 Processing: {csv_file} -> {table_name}")
        
        try:
            df = pd.read_csv(file_path, dtype=str)
            df.columns = [c.strip().lower() for c in df.columns]
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False, chunksize=5000)
            print(f"   ✅ Sukses! ({len(df)} baris)")
            
        except Exception as e:
            print(f"   ❌ GAGAL: {e}")

if __name__ == "__main__":
    load_raw_data()