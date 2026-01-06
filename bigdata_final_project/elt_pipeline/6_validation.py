from sqlalchemy import text
from db_utils import get_engine

def run_data_quality_checks():
    engine = get_engine()
    print("\n=== MULAI ELT DATA QUALITY ASSURANCE ===\n")
    
    validations = [
        {
            "rule": "1. Duplicate Row Check",
            "desc": "Cek duplikasi data baris yang sama persis",
            "sql": "SELECT COUNT(*) - COUNT(DISTINCT order_id, product_id, seller_id, order_status) FROM fact_sales;",
            "threshold": 0 
        },
        {
            "rule": "2. Null Check",
            "desc": "Cek Revenue/Price NULL",
            "sql": "SELECT COUNT(*) FROM fact_sales WHERE price IS NULL OR freight_value IS NULL;",
            "threshold": 0
        },
        {
            "rule": "3. Range Check",
            "desc": "Cek nilai negatif",
            "sql": "SELECT COUNT(*) FROM fact_sales WHERE price < 0 OR freight_value < 0;",
            "threshold": 0
        },
        {
            "rule": "4. Datatype Consistency",
            "desc": "Cek konversi tanggal",
            "sql": "SELECT COUNT(*) FROM fact_sales WHERE purchase_date IS NULL;",
            "threshold": 0 
        },
        {
            "rule": "5. Referential Integrity",
            "desc": "Cek Orphan records",
            "sql": "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_products p ON f.product_id = p.product_id WHERE p.product_id IS NULL;",
            "threshold": 0
        }
    ]
    
    all_passed = True
    with engine.connect() as conn:
        for v in validations:
            print(f"🔎 Checking: {v['rule']}")
            try:
                result = conn.execute(text(v['sql'])).fetchone()[0]
                if result <= v['threshold']:
                    print(f"   ✅ PASS (Result: {result})")
                else:
                    print(f"   ❌ FAIL (Result: {result})")
                    all_passed = False
            except Exception as e:
                print(f"   ⚠️ ERROR: {e}")
                all_passed = False
            print("-" * 50)

    if all_passed:
        print("\nVALIDASI BERHASIL!")
    else:
        print("\nADA VALIDASI GAGAL.")

if __name__ == "__main__":
    run_data_quality_checks()