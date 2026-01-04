import os

RAW_DIR = r"C:\\Users\\LENOVO LOQ\\OneDrive - Telkom University\\Documents\\Kuliah\\Tugas dan Materi\\Semester 7\\git\\bigdata\\bigdata_final_project\\raw"
PROCESSED_DIR = r"C:\\Users\\LENOVO LOQ\\OneDrive - Telkom University\\Documents\\Kuliah\\Tugas dan Materi\\Semester 7\\git\\bigdata\\bigdata_final_project\\warehouse\\etl"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

FILE_ECOMMERCE_CLEAN = os.path.join(PROCESSED_DIR, 'transformed_source1_brazilian_ecommerce.csv')
FILE_INFLATION_CLEAN = os.path.join(PROCESSED_DIR, 'transformed_source2_brazil_inflation.csv')

DB_USER = 'root'
DB_PASS = ''
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'olist_dw'