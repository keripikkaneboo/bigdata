import time
from sqlalchemy import text
from db_utils import get_engine

INFLATION_QUERIES = [
    {
        "name": "1. Cleaning & Unpivot Data Inflasi",
        "sql": """
            CREATE TABLE IF NOT EXISTS dim_brazil_inflation AS
            SELECT * FROM (
                SELECT CAST(year AS UNSIGNED) as year, 1 as month, CAST(january AS DECIMAL(10,2)) as inflation_rate FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 2, CAST(february AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 3, CAST(march AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 4, CAST(april AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 5, CAST(may AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 6, CAST(june AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 7, CAST(july AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 8, CAST(august AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 9, CAST(september AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 10, CAST(october AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 11, CAST(november AS DECIMAL(10,2)) FROM raw_brazil_inflation
                UNION ALL SELECT CAST(year AS UNSIGNED), 12, CAST(december AS DECIMAL(10,2)) FROM raw_brazil_inflation
            ) AS unpivoted_data
            WHERE inflation_rate IS NOT NULL
            ORDER BY year DESC, month DESC;
        """
    },
    {
        "name": "2. Agregasi Penjualan Per Bulan",
        "sql": """
            CREATE TABLE IF NOT EXISTS fact_monthly_purchasing_power AS
            SELECT 
                CAST(YEAR(purchase_date) AS UNSIGNED) as sales_year,
                CAST(MONTH(purchase_date) AS UNSIGNED) as sales_month,
                COUNT(DISTINCT order_id) as total_transactions,
                SUM(price) as total_spending_revenue,
                AVG(price) as avg_spending_per_item
            FROM fact_sales
            WHERE purchase_date IS NOT NULL
            GROUP BY 1, 2;
        """
    },
    {
        "name": "3. Final Table: Korelasi Inflasi vs Daya Beli",
        "sql": """
            CREATE TABLE IF NOT EXISTS mart_inflation_analysis AS
            SELECT 
                s.sales_year, s.sales_month,
                CAST(CONCAT(CAST(s.sales_year AS CHAR), '-', LPAD(CAST(s.sales_month AS CHAR), 2, '0'), '-01') AS DATE) as period_date,
                s.total_transactions, s.total_spending_revenue, s.avg_spending_per_item,
                i.inflation_rate
            FROM fact_monthly_purchasing_power s
            JOIN dim_brazil_inflation i ON s.sales_year = i.year AND s.sales_month = i.month
            ORDER BY s.sales_year DESC, s.sales_month DESC;
        """
    }
]

def run_inflation_analysis():
    engine = get_engine()
    print("\n--- MULAI PROSES ELT: PHASE 3 (INFLATION ANALYSIS) ---")
    with engine.connect() as conn:
        for task in INFLATION_QUERIES:
            print(f"Running: {task['name']}...")
            start_time = time.time()
            try:
                table_name = task['sql'].split("CREATE TABLE IF NOT EXISTS ")[1].split(" ")[0]
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.execute(text(task['sql']))
                print(f"Selesai! ({time.time() - start_time:.2f} detik)")
            except Exception as e:
                print(f"GAGAL: {e}")

if __name__ == "__main__":
    run_inflation_analysis()