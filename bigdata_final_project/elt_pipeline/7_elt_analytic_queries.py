from sqlalchemy import text
from db_utils import get_engine

def print_table(headers, rows):
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header = "|" + "|".join(f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers))) + "|"

    print(line)
    print(header)
    print(line)

    for row in rows:
        print("|" + "|".join(f" {str(row[i]).ljust(col_widths[i])} " for i in range(len(row))) + "|")

    print(line)


ANALYTIC_QUERIES = [
    {
        "name": "1. Tren Jumlah Transaksi Bulanan",
        "sql": """
        SELECT
            sales_year,
            sales_month,
            total_transactions
        FROM fact_monthly_purchasing_power
        ORDER BY sales_year, sales_month;
        """
    },
    {
        "name": "2. Tren Total Pengeluaran Bulanan",
        "sql": """
        SELECT
            sales_year,
            sales_month,
            total_spending_revenue
        FROM fact_monthly_purchasing_power
        ORDER BY sales_year, sales_month;
        """
    },
    {
        "name": "3. Inflasi vs Jumlah Transaksi",
        "sql": """
        SELECT
            inflation_rate,
            total_transactions
        FROM mart_inflation_analysis
        ORDER BY inflation_rate;
        """
    },
    {
        "name": "4. Inflasi vs Total Pengeluaran",
        "sql": """
        SELECT
            inflation_rate,
            total_spending_revenue
        FROM mart_inflation_analysis
        ORDER BY inflation_rate;
        """
    },
    {
        "name": "5. Inflasi vs Rata-rata Pengeluaran per Item",
        "sql": """
        SELECT
            inflation_rate,
            avg_spending_per_item
        FROM mart_inflation_analysis
        ORDER BY inflation_rate;
        """
    },
    {
        "name": "6. Distribusi Transaksi per Kategori Produk",
        "sql": """
        SELECT
            p.category_name,
            COUNT(f.order_id) AS total_orders
        FROM fact_sales f
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY p.category_name
        ORDER BY total_orders DESC;
        """
    },
    {
        "name": "7. Rata-rata Ongkos Kirim per Wilayah",
        "sql": """
        SELECT
            c.customer_state,
            AVG(f.freight_value) AS avg_freight_cost
        FROM fact_sales f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        GROUP BY c.customer_state
        ORDER BY avg_freight_cost DESC;
        """
    },
    {
        "name": "8. Total Pengeluaran Tanpa Outlier Harga",
        "sql": """
        SELECT
            SUM(price) AS revenue_without_price_outlier
        FROM fact_sales_outlier_flag
        WHERE is_price_outlier = 0;
        """
    }
]


def run_analytic_queries():
    engine = get_engine()
    print("\n" + "=" * 90)
    print("VALIDASI & ANALISIS QUERY ELT")
    print("=" * 90)

    with engine.connect() as conn:
        for q in ANALYTIC_QUERIES:
            print(f"\n{q['name']}")
            try:
                result = conn.execute(text(q["sql"]))
                rows = result.fetchall()
                headers = list(result.keys())

                if not rows:
                    print("Query berhasil dijalankan, tetapi tidak menghasilkan data.")
                    continue

                print_table(headers, rows)

            except Exception as e:
                print("Gagal menjalankan query")
                print("Error:", e)

    print("\nSeluruh query analitik ELT selesai dijalankan.\n")


if __name__ == "__main__":
    run_analytic_queries()
