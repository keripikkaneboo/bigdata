import subprocess
import sys
import time
import os

def run_script(script_name):
    if not os.path.exists(script_name):
        print(f"[ERROR] File {script_name} tidak ditemukan.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f">> MENJALANKAN: {script_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        subprocess.run([sys.executable, script_name], check=True)
        duration = time.time() - start_time
        print(f"\n[SUKSES] {script_name} selesai dalam {duration:.2f} detik.")
    except subprocess.CalledProcessError:
        print(f"\n[GAGAL] Terjadi error saat menjalankan {script_name}.")
        sys.exit(1) 

def main():
    total_start = time.time()
    print("STARTING ETL PIPELINE...\n")

    steps = [
    "1_extract.py",
    "2_transform_ecommerce.py",
    "3_transform_inflation.py",
    "4_load.py",
    "5_validate_sql_queries.py"  
    ]

    for step in steps:
        run_script(step)

    total_duration = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"PIPELINE SELESAI. Total Waktu: {total_duration:.2f} detik.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()