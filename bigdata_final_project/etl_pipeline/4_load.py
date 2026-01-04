import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, FILE_ECOMMERCE_CLEAN, FILE_INFLATION_CLEAN

def log_process(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def main():
    log_process("Memulai Proses ETL Load di Local...")

    try:
        # Mengambil file dari config
        file_ecommerce = FILE_ECOMMERCE_CLEAN
        file_inflation = FILE_INFLATION_CLEAN

        if not os.path.exists(file_ecommerce):
            raise FileNotFoundError(f"File '{file_ecommerce}' tidak ditemukan! Jalankan Transform dahulu.")
        if not os.path.exists(file_inflation):
            raise FileNotFoundError(f"File '{file_inflation}' tidak ditemukan! Jalankan Transform dahulu.")
            
        df_ecommerce = pd.read_csv(file_ecommerce)
        df_inflation_wide = pd.read_csv(file_inflation)
        log_process("Berhasil membaca file CSV.")
    except Exception as e:
        log_process(f"Error Membaca File: {e}")
        return

    try:
        # --- Transformasi Inflasi (Melting) ---
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        cols_to_melt = [c for c in df_inflation_wide.columns if c in month_map.keys()]
        id_vars = ['year']
        if 'yearly_avg' in df_inflation_wide.columns: id_vars.append('yearly_avg')
        if 'is_volatile' in df_inflation_wide.columns: id_vars.append('is_volatile')
        if 'inflation_risk' in df_inflation_wide.columns: id_vars.append('inflation_risk')

        df_inflation_long = df_inflation_wide.melt(
            id_vars=id_vars, 
            value_vars=cols_to_melt, 
            var_name='month_name', 
            value_name='inflation_rate'
        )
        
        df_inflation_long['month_num'] = df_inflation_long['month_name'].map(month_map)
        
        df_inflation_long['year_month'] = pd.to_datetime(
            df_inflation_long['year'].astype(str) + '-' + df_inflation_long['month_num'].astype(str) + '-01'
        ).dt.strftime('%Y-%m')
        final_cols = ['year_month', 'inflation_rate'] + [c for c in id_vars if c != 'year']
        
        dim_inflation = df_inflation_long[final_cols].dropna(subset=['inflation_rate']).drop_duplicates('year_month')
        log_process("Persiapan Dimensi Inflasi (dengan fitur baru) selesai.")
    except Exception as e:
        log_process(f"Error Transformasi Inflasi: {e}")
        return


    try:
        # --- Persiapan Dimensi & Fact Table ---
        dim_customer = df_ecommerce[['customer_id', 'customer_unique_id', 'customer_city', 'customer_state']].drop_duplicates('customer_id')
        
        if 'product_category_name' in df_ecommerce.columns:
            dim_product = df_ecommerce[['product_id', 'product_category_name']].drop_duplicates('product_id')
        else:
            dim_product = df_ecommerce[['product_id']].drop_duplicates()
            dim_product['product_category_name'] = 'Unknown'

        fact_sales = df_ecommerce.copy()
        fact_sales['order_purchase_timestamp'] = pd.to_datetime(fact_sales['order_purchase_timestamp'])
        
        fact_sales['year_month'] = fact_sales['order_purchase_timestamp'].dt.strftime('%Y-%m')
        
        fact_cols = [
            'order_id', 'order_item_id', 'customer_id', 'product_id', 
            'order_purchase_timestamp', 'price', 'freight_value', 
            'order_status', 'year_month', 'delivery_days', 
            'total_order_value', 'is_late', 'purchase_hour', 'freight_ratio'       
        ]

        valid_fact_cols = [c for c in fact_cols if c in fact_sales.columns]
        fact_sales = fact_sales[valid_fact_cols]
        
    except Exception as e:
        log_process(f"Error Persiapan Dataframe: {e}")
        return

    connection_str = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
    
    try:
        engine_root = create_engine(connection_str)
        with engine_root.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            conn.execute(text(f"USE {DB_NAME}"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
            
            # Drop tabel lama
            conn.execute(text("DROP TABLE IF EXISTS Fact_Sales"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Product"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Customer"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Inflation"))

            log_process("Membuat Tabel dengan Schema Baru...")
            
            # 1. Dim Customer
            conn.execute(text("""
                CREATE TABLE Dim_Customer (
                    `customer_id` VARCHAR(50) PRIMARY KEY,
                    `customer_unique_id` VARCHAR(50),
                    `customer_city` VARCHAR(100),
                    `customer_state` VARCHAR(5)
                )
            """))
            
            # 2. Dim Product
            conn.execute(text("""
                CREATE TABLE Dim_Product (
                    `product_id` VARCHAR(50) PRIMARY KEY,
                    `product_category_name` VARCHAR(100)
                )
            """))
            
            # 3. Dim Inflation
            conn.execute(text("""
                CREATE TABLE Dim_Inflation (
                    `year_month` VARCHAR(10) PRIMARY KEY,
                    `inflation_rate` FLOAT,
                    `yearly_avg` FLOAT,
                    `is_volatile` INT
                )
            """))
            
            # 4. Fact Sales
            conn.execute(text("""
                CREATE TABLE Fact_Sales (
                    `order_id` VARCHAR(50),
                    `order_item_id` INT,
                    `customer_id` VARCHAR(50),
                    `product_id` VARCHAR(50),
                    `order_purchase_timestamp` DATETIME,
                    `price` FLOAT,
                    `freight_value` FLOAT,
                    `order_status` VARCHAR(50),
                    `year_month` VARCHAR(10),
                    
                    `delivery_days` INT,
                    `total_order_value` FLOAT,
                    `is_late` INT,
                    `purchase_hour` INT,
                    `freight_ratio` FLOAT,
                    
                    PRIMARY KEY (`order_id`, `order_item_id`),
                    FOREIGN KEY (`customer_id`) REFERENCES Dim_Customer(`customer_id`),
                    FOREIGN KEY (`product_id`) REFERENCES Dim_Product(`product_id`),
                    FOREIGN KEY (`year_month`) REFERENCES Dim_Inflation(`year_month`)
                )
            """))
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
            log_process("Skema Database Berhasil Dibuat.")

        engine_db = create_engine(f"{connection_str}/{DB_NAME}")
        
        log_process("Sedang memuat data ke MySQL...")
        
        # Load Data
        dim_customer.to_sql('Dim_Customer', engine_db, if_exists='append', index=False, chunksize=10000)
        dim_product.to_sql('Dim_Product', engine_db, if_exists='append', index=False, chunksize=10000)
        dim_inflation.to_sql('Dim_Inflation', engine_db, if_exists='append', index=False, chunksize=10000)
        fact_sales.to_sql('Fact_Sales', engine_db, if_exists='append', index=False, chunksize=10000)

        log_process("SUKSES! Semua data beserta fitur baru berhasil dimuat.")
        
    except Exception as e:
        log_process(f"TERJADI ERROR PADA DATABASE: {e}")
        print("\nSaran: Periksa username, password, dan apakah MySQL Server sudah berjalan.")

if __name__ == "__main__":
    main()