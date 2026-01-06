from sqlalchemy import text
from db_utils import get_engine

TRANSFORM_QUERIES = [
    {
        "name": "1. Membuat Dimensi Customers (Cleaned)",
        "sql": """
            CREATE TABLE IF NOT EXISTS dim_customers AS
            SELECT DISTINCT 
                customer_id, customer_unique_id, customer_zip_code_prefix, 
                customer_city, customer_state
            FROM raw_customers
            WHERE customer_id IS NOT NULL;
        """
    },
    {
        "name": "2. Membuat Dimensi Products (Enriched)",
        "sql": """
            CREATE TABLE IF NOT EXISTS dim_products AS
            SELECT DISTINCT 
                p.product_id,
                COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') as category_name,
                p.product_weight_g, p.product_length_cm, p.product_height_cm, p.product_width_cm
            FROM raw_products p
            LEFT JOIN raw_category_translation t ON p.product_category_name = t.product_category_name
            WHERE p.product_id IS NOT NULL;
        """
    },
    {
        "name": "3. Membuat Fact Sales (Cleaned & Integrated)",
        "sql": """
            CREATE TABLE IF NOT EXISTS fact_sales AS
            SELECT DISTINCT 
                o.order_id, o.customer_id, oi.product_id, oi.seller_id, o.order_status,
                CAST(NULLIF(o.order_purchase_timestamp, '') AS DATETIME) as purchase_date,
                CAST(NULLIF(o.order_approved_at, '') AS DATETIME) as approved_date,
                CAST(NULLIF(o.order_delivered_carrier_date, '') AS DATETIME) as carrier_date,
                CAST(NULLIF(o.order_delivered_customer_date, '') AS DATETIME) as delivered_date,
                CAST(NULLIF(o.order_estimated_delivery_date, '') AS DATETIME) as estimated_date,
                CAST(oi.price AS DECIMAL(10,2)) as price,
                CAST(oi.freight_value AS DECIMAL(10,2)) as freight_value
            FROM raw_orders o
            JOIN raw_order_items oi ON o.order_id = oi.order_id
            INNER JOIN dim_products p ON oi.product_id = p.product_id 
            WHERE NULLIF(o.order_purchase_timestamp, '') IS NOT NULL 
                AND CAST(oi.price AS DECIMAL(10,2)) >= 0 
                AND CAST(oi.freight_value AS DECIMAL(10,2)) >= 0;
        """
    }
]

def run_transformations():
    engine = get_engine()
    print("\n--- MULAI PROSES ELT: PHASE 2 (TRANSFORM WAREHOUSE) ---")
    with engine.connect() as conn:
        for task in TRANSFORM_QUERIES:
            print(f"Running: {task['name']}...")
            try:
                table_name = task['sql'].split("CREATE TABLE IF NOT EXISTS ")[1].split(" ")[0]
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.execute(text(task['sql']))
                print("Selesai!")
            except Exception as e:
                print(f"GAGAL: {e}")

if __name__ == "__main__":
    run_transformations()