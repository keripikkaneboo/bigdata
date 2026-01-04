import os
import shutil
import time
import glob
import kagglehub
import pandas as pd
from config import RAW_DIR

def extract_from_kaggle(source_name):
    """
    Fungsi untuk download dari Kaggle dan memindahkannya ke folder RAW_DIR (digabung)
    """
    print(f"--- Memulai Ekstraksi: {source_name} ---")
    start_time = time.time()

    try:
        path = kagglehub.dataset_download(source_name)
        print(f"Download selesai di cache: {path}")
    except Exception as e:
        print(f"Gagal download: {e}")
        return

    destination_folder = RAW_DIR 
    
    files = glob.glob(os.path.join(path, "*.*")) 
    for file in files:
        file_name = os.path.basename(file)
        dest_path = os.path.join(destination_folder, file_name)
        
        try:
            if not os.path.exists(dest_path):
                shutil.copy(file, dest_path)
                print(f"Berhasil memindahkan: {file_name}")
            else:
                print(f"File sudah ada: {file_name}")
        except Exception as e:
            print(f"Gagal memindahkan {file_name}: {e}")

    print(f"\nVerifikasi Data di: {destination_folder}")
    

    total_size = 0
    local_files = glob.glob(os.path.join(destination_folder, "*.csv"))
    
    for f in local_files:
        if any(os.path.basename(f) == os.path.basename(src) for src in files):
            size = os.path.getsize(f) / (1024 * 1024) 
            total_size += size
            try:
                df_temp = pd.read_csv(f, nrows=2) 
                print(f"- {os.path.basename(f)}: {df_temp.shape[1]} Kolom, Size: {size:.2f} MB")
            except:
                print(f"- {os.path.basename(f)}: (Gagal baca header), Size: {size:.2f} MB")

    print(f"Waktu Eksekusi: {time.time() - start_time:.2f} detik\n")

if __name__ == "__main__":
    extract_from_kaggle("olistbr/brazilian-ecommerce")
    extract_from_kaggle("lucashmateo/brazil-inflation-data")