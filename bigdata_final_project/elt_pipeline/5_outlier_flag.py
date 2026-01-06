from sqlalchemy import text
from db_utils import get_engine

OUTLIER_SQL = """
DROP TABLE IF EXISTS fact_sales_outlier_flag;

CREATE TABLE fact_sales_outlier_flag AS
WITH price_ranked AS (
    SELECT
        price,
        NTILE(4) OVER (ORDER BY price) AS quartile
    FROM fact_sales
),
price_bounds AS (
    SELECT
        MAX(CASE WHEN quartile = 1 THEN price END) AS q1,
        MIN(CASE WHEN quartile = 4 THEN price END) AS q3
    FROM price_ranked
),
freight_ranked AS (
    SELECT
        freight_value,
        NTILE(4) OVER (ORDER BY freight_value) AS quartile
    FROM fact_sales
),
freight_bounds AS (
    SELECT
        MAX(CASE WHEN quartile = 1 THEN freight_value END) AS q1,
        MIN(CASE WHEN quartile = 4 THEN freight_value END) AS q3
    FROM freight_ranked
)
SELECT
    f.*,
    CASE
        WHEN f.price < (pb.q1 - 1.5 * (pb.q3 - pb.q1))
          OR f.price > (pb.q3 + 1.5 * (pb.q3 - pb.q1))
        THEN 1 ELSE 0
    END AS is_price_outlier,
    CASE
        WHEN f.freight_value < (fb.q1 - 1.5 * (fb.q3 - fb.q1))
          OR f.freight_value > (fb.q3 + 1.5 * (fb.q3 - fb.q1))
        THEN 1 ELSE 0
    END AS is_freight_outlier
FROM fact_sales f
CROSS JOIN price_bounds pb
CROSS JOIN freight_bounds fb;
"""

SUMMARY_SQL = """
SELECT
    COUNT(*) AS total_rows,
    SUM(is_price_outlier) AS price_outliers,
    SUM(is_freight_outlier) AS freight_outliers,
    ROUND(SUM(is_price_outlier) / COUNT(*) * 100, 2) AS price_outlier_pct,
    ROUND(SUM(is_freight_outlier) / COUNT(*) * 100, 2) AS freight_outlier_pct
FROM fact_sales_outlier_flag;
"""

def run_outlier_flag():
    engine = get_engine()
    print("\n--- IDENTIFIKASI OUTLIER (ELT - MARIA DB COMPATIBLE) ---")

    with engine.connect() as conn:
        for stmt in OUTLIER_SQL.split(";"):
            if stmt.strip():
                conn.execute(text(stmt))

        print("Tabel fact_sales_outlier_flag berhasil dibuat.")

        result = conn.execute(text(SUMMARY_SQL)).fetchone()

        print("\nRINGKASAN OUTLIER:")
        print("-" * 50)
        print(f"Total Data              : {result.total_rows}")
        print(f"Price Outlier           : {result.price_outliers} "
              f"({result.price_outlier_pct}%)")
        print(f"Freight Value Outlier   : {result.freight_outliers} "
              f"({result.freight_outlier_pct}%)")
        print("-" * 50)

    print("Proses identifikasi outlier selesai.\n")

if __name__ == "__main__":
    run_outlier_flag()
