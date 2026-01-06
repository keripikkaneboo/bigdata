import subprocess

scripts = [
    "1_extract_load.py",
    "2_indexing.py",
    "3_transform_core.py",
    "4_transform_inflation.py",
    "5_outlier_flag.py",
    "6_validation.py",
    "7_elt_analytic_queries.py"
]

print("🚀 MEMULAI ELT PIPELINE LENGKAP...\n")

for script in scripts:
    print(f"running {script}...")
    result = subprocess.run(["python", script])
    if result.returncode != 0:
        print(f"🛑 STOP: {script} gagal dijalankan.")
        break

print("\n🏁 PIPELINE SELESAI.")