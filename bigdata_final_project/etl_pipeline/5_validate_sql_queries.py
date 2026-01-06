from sqlalchemy import create_engine, text
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

def get_engine():
    conn_str = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conn_str)

VALIDATION_QUERIES = [
    {
        "name": "Top 10 Kategori Pendapatan Tertinggi",
        "sql": """
        SELECT 
            p.product_category_name AS category,
            SUM(f.total_order_value) AS revenue
        FROM Fact_Sales f
        JOIN Dim_Product p ON f.product_id = p.product_id
        GROUP BY p.product_category_name
        ORDER BY revenue DESC
        LIMIT 10;
        """
    },
    {
        "name": "Rata-rata Ongkos Kirim per Negara Bagian",
        "sql": """
        SELECT 
            c.customer_state AS state,
            AVG(f.freight_value) AS avg_freight
        FROM Fact_Sales f
        JOIN Dim_Customer c ON f.customer_id = c.customer_id
        GROUP BY c.customer_state
        ORDER BY avg_freight DESC;
        """
    },
    {
        "name": "Tren Pesanan Bulanan",
        "sql": """
        SELECT 
            `year_month`,
            COUNT(`order_id`) AS total_orders
        FROM Fact_Sales
        GROUP BY `year_month`
        ORDER BY `year_month`;
        """
    },
    {
        "name": "Dampak Inflasi terhadap Volume Pesanan",
        "sql": """
        SELECT 
            i.inflation_rate,
            COUNT(f.order_id) AS total_orders
        FROM Fact_Sales f
        JOIN Dim_Inflation i ON f.year_month = i.year_month
        GROUP BY i.inflation_rate
        ORDER BY i.inflation_rate;
        """
    },
    {
        "name": "Persentase Keterlambatan Pengiriman",
        "sql": """
        SELECT 
            (SUM(is_late) / COUNT(*)) * 100 AS late_percentage
        FROM Fact_Sales;
        """
    },
    {
        "name": "Durasi Pengiriman Rata-rata per Wilayah",
        "sql": """
        SELECT 
            c.customer_state AS state,
            AVG(f.delivery_days) AS avg_delivery_days
        FROM Fact_Sales f
        JOIN Dim_Customer c ON f.customer_id = c.customer_id
        GROUP BY c.customer_state
        ORDER BY avg_delivery_days DESC;
        """
    },
    {
        "name": "Jam Belanja Tersibuk",
        "sql": """
        SELECT 
            purchase_hour,
            COUNT(*) AS total_transactions
        FROM Fact_Sales
        GROUP BY purchase_hour
        ORDER BY total_transactions DESC;
        """
    },
    {
        "name": "Pendapatan: Ekonomi Stabil vs Tidak Stabil",
        "sql": """
        SELECT 
            i.is_volatile,
            SUM(f.total_order_value) AS revenue
        FROM Fact_Sales f
        JOIN Dim_Inflation i ON f.year_month = i.year_month
        GROUP BY i.is_volatile;
        """
    }
]

def print_table(headers, rows):
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    separator = "+".join("-" * (w + 2) for w in col_widths)


    print(separator)
    header_row = "|".join(f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers)))
    print(header_row)
    print(separator)


    for row in rows:
        data_row = "|".join(f" {str(row[i]).ljust(col_widths[i])} " for i in range(len(row)))
        print(data_row)

    print(separator)


def run_sql_validation():
    engine = get_engine()
    print("\n" + "=" * 80)
    print("VALIDASI QUERY SQL ANALITIK (POST-ETL)")
    print("=" * 80)

    with engine.connect() as conn:
        for q in VALIDATION_QUERIES:
            print(f"\n▶ {q['name']}")
            try:
                result = conn.execute(text(q["sql"]))
                rows = result.fetchall()

                if not rows:
                    print("Query berhasil, tetapi tidak menghasilkan data.")
                    continue
                headers = list(result.keys())
                print_table(headers, rows)
            except Exception as e:
                print("Gagal menjalankan query")
                print("Error:", e)

    print("\nVALIDASI QUERY SELESAI.\n")

if __name__ == "__main__":
    run_sql_validation()
