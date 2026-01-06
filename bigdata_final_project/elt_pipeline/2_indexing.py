from sqlalchemy import text
from db_utils import get_engine

def add_indexes_to_raw_data():
    engine = get_engine()
    print("\n--- OPTIMASI: MENAMBAHKAN INDEX KE RAW DATA ---")
    indexes = [
        "CREATE INDEX idx_orders_order_id ON raw_orders(order_id(50));",
        "CREATE INDEX idx_items_order_id ON raw_order_items(order_id(50));",
        "CREATE INDEX idx_items_product_id ON raw_order_items(product_id(50));",
        "CREATE INDEX idx_products_product_id ON raw_products(product_id(50));"
    ]
    
    with engine.connect() as conn:
        for sql in indexes:
            try:
                print(f"Executing: {sql.split('ON')[1]}...")
                conn.execute(text(sql))
            except Exception as e:
                print(f"Note: {e}")
        print("Indexing Selesai!")

if __name__ == "__main__":
    add_indexes_to_raw_data()