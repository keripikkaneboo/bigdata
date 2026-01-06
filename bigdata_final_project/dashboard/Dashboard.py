import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard ETL & Analytics",
    page_icon="🇧🇷",
    layout="wide"
)

# --- 2. FUNGSI KONEKSI DATABASE (DINAMIS) ---
@st.cache_data
def load_data_from_dw(table_name):
    # Nama file database SQLite (Pastikan file ini ada di GitHub)
    DB_FILE = 'olist_dw.db'
    
    try:
        # Membuat koneksi ke SQLite
        conn = sqlite3.connect(DB_FILE)
        
        # Query mengambil SEMUA data
        query = f"SELECT * FROM {table_name}"
        
        # Membaca SQL
        df = pd.read_sql(query, conn)
        conn.close()
        
        return df
        
    except Exception as e:
        return f"Terjadi kesalahan: {e}. Pastikan file '{DB_FILE}' sudah di-upload ke GitHub."

# --- 3. INISIALISASI STATE ---
if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = 'Home'

def pindah_halaman(nama_halaman):
    st.session_state.halaman_aktif = nama_halaman

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.title("Navigasi")
    
    if st.button("🏠 Home", use_container_width=True):
        pindah_halaman("Home")
        
    if st.button("📊 Dashboard", use_container_width=True):
        pindah_halaman("Dashboard")
        
    if st.button("ℹ️ Info", use_container_width=True):
        pindah_halaman("Info")
        
    if st.button("🔗 Link", use_container_width=True):
        pindah_halaman("Link")
    
    st.write("---")
    st.caption("**Tubes Big Data**")
    st.caption("Enrico Chandra Nugroho (1103220234)")
    st.caption("Kevin Justivio Rachman Ali (1103223068)")

# --- 5. LOGIKA KONTEN UTAMA ---
menu = st.session_state.halaman_aktif

if menu == "Home":
    # === HALAMAN HOME ===
    st.title("🏠 Selamat Datang")
    
    st.write("""
        ### Aplikasi Pelaporan Tugas Besar Big Data
        
        Aplikasi ini dirancang untuk memonitor kinerja **E-Commerce Olist** dan pengaruh indikator ekonomi makro (**Inflasi Brazil**).
        
        Silakan pilih menu di sebelah kiri untuk menavigasi aplikasi:
        * **Dashboard**: Visualisasi ETL interaktif.
        * **Info**: Penjelasan latar belakang, dataset, dan arsitektur sistem (ETL vs ELT).
        * **Link**: Tautan ke sumber data dan referensi.
        """)

elif menu == "Dashboard":
    # === HALAMAN DASHBOARD ===
    st.title("📊 Dashboard ETL (Power BI Embedded)")
    
    # 1. TAMPILAN POWER BI
    power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiNmExYmQyNDktYjhkNi00ZWI2LTkyOWUtZGM5ZTdmNzVmNjlkIiwidCI6IjkwYWZmZTBmLWMyYTMtNDEwOC1iYjk4LTZjZWI0ZTk0ZWYxNSIsImMiOjEwfQ%3D%3D"
    try:
        components.iframe(power_bi_url, width=None, height=800)
    except Exception as e:
        st.error(f"Gagal memuat dashboard: {e}")
        
    st.divider()
    
    # 2. TAMPILAN DATA WAREHOUSE (TABLE EXPLORER)
    st.subheader("Data Warehouse (Live)")
    st.write("Silakan pilih tabel di bawah ini untuk melihat seluruh data langsung dari database MySQL.")
    
    # Pilihan Tabel (Dropdown)
    pilihan_tabel = st.selectbox(
        "Pilih Tabel Database:",
        ("fact_sales", "dim_customer", "dim_product", "dim_inflation")
    )
    
    # Memuat data berdasarkan pilihan
    data_dw = load_data_from_dw(pilihan_tabel)
    
    if isinstance(data_dw, pd.DataFrame):
        # Menampilkan Metrik Informasi Data
        m1, m2 = st.columns(2)
        m1.metric(f"Total Baris ({pilihan_tabel})", f"{len(data_dw):,} Rows")
        m2.metric("Total Kolom", f"{len(data_dw.columns)} Columns")
        
        # Menampilkan Tabel Full
        with st.expander(f"Klik untuk melihat detail data: {pilihan_tabel}", expanded=True):
            st.dataframe(data_dw, use_container_width=True)
            
            # Tombol download
            csv = data_dw.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Download {pilihan_tabel}.csv",
                data=csv,
                file_name=f'{pilihan_tabel}.csv',
                mime='text/csv',
            )
    else:
        st.error("Gagal terhubung ke Database MySQL!")
        st.warning(f"Error: {data_dw}")

elif menu == "Info":
    # === HALAMAN INFO ===
    st.title("ℹ️ Informasi Proyek")
    
    tab1, tab2, tab3 = st.tabs(["Latar Belakang", "Data & Studi Kasus", "Arsitektur Sistem"])
    
    with tab1:
        st.header("Latar Belakang & Tujuan")
        st.markdown("""
        **Latar Belakang**
        Perkembangan industri e-commerce di Brazil menghasilkan volume data transaksi yang besar dan kompleks. 
        Olist, sebagai platform terbesar, memiliki data yang terpecah dalam berbagai tabel relasional. 
        Analisis performa penjualan tidak dapat berdiri sendiri tanpa memperhitungkan faktor eksternal seperti **Inflasi Mata Uang** yang mempengaruhi daya beli.
        """)

    with tab2:
        st.header("Deskripsi Data")
        st.write("Proyek ini menggunakan dua sumber data utama untuk memungkinkan analisis korelasi.")
        
        col_data1, col_data2 = st.columns(2)
        
        with col_data1:
            st.subheader("1. Dataset Utama (Olist)")
            st.write("**Sumber:** Kaggle (2016-2018)")
            st.write("**Total:** ±100.000 Baris Data")
            with st.expander("Rincian 8 Tabel Relasional"):
                st.markdown("""
                1. **Orders**: Tabel fakta status pesanan.
                2. **Order Items**: Detail barang per pesanan.
                3. **Payments**: Metode pembayaran.
                4. **Reviews**: Ulasan pelanggan.
                5. **Sellers**: Identitas penjual.
                6. **Customers**: Lokasi pelanggan.
                7. **Products**: Kategori & dimensi produk.
                8. **Geolocation**: Data kode pos.
                """)

        with col_data2:
            st.subheader("2. Dataset Pendukung")
            st.write("**Sumber:** StatBureau / Kaggle")
            st.write("**Jenis:** Time-Series (Indeks Harga Konsumen)")
            st.markdown("""
            Data ini mencerminkan fluktuasi nilai mata uang Brazil (BRL) yang digunakan untuk melihat kondisi ekonomi makro selama periode transaksi.
            """)
            
    with tab3:
        st.header("Arsitektur Sistem")
        st.write("Perbandingan dua metode pipeline Big Data yang diterapkan:")
        
        col_etl, col_elt = st.columns(2)
        
        with col_etl:
            st.markdown("### 1. Pipeline ETL")
            st.caption("Beban Komputasi: Lokal (Client Side)")
            st.markdown("""
            * **Extract:** Load CSV ke Data Lake lokal.
            * **Transform (Pandas):** * Imputasi nilai kosong.
                * Penanganan Outlier Inflasi (Metode IQR).
                * Unpivot data inflasi (`melt`).
            * **Load:** Simpan ke MySQL sebagai data bersih.
            """)
            
        with col_elt:
            st.markdown("### 2. Pipeline ELT")
            st.caption("Beban Komputasi: Server (MySQL Engine)")
            st.markdown("""
            * **Extract & Load:** Muat data mentah (Raw) langsung ke MySQL.
            * **Transform (SQL Query):** * Menggunakan `CREATE TABLE AS SELECT`.
                * Optimasi dengan **Indexing** pada tabel staging.
                * Feature engineering via Query.
            """)
        
        st.markdown("---")
        st.subheader("Feature Engineering")
        st.markdown("""
        * **Delivery_days**: Selisih hari (Sampai - Beli).
        * **Is_late**: Flag (0/1) jika terlambat dari estimasi.
        * **Freight_ratio**: Rasio ongkos kirim terhadap total belanja.
        * **Volatility_metrics**: Standar deviasi inflasi untuk melihat kestabilan ekonomi.
        """)

elif menu == "Link":
    # === HALAMAN LINK ===
    st.title("🔗 Tautan")
    
    st.markdown("""
    Berikut adalah link untuk proyek ini:
    
    * [📂 Dataset Sumber Olist (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
    * [📂 Dataset Sumber Brazil Inflation Data (Kaggle)](https://www.kaggle.com/datasets/lucashmateo/brazil-inflation-data)
    * [💻 Github Project](https://github.com/keripikkaneboo/bigdata/tree/main/bigdata_final_project)
    * [📈 Dashboard Full Screen](https://app.powerbi.com/view?r=eyJrIjoiNmExYmQyNDktYjhkNi00ZWI2LTkyOWUtZGM5ZTdmNzVmNjlkIiwidCI6IjkwYWZmZTBmLWMyYTMtNDEwOC1iYjk4LTZjZWI0ZTk0ZWYxNSIsImMiOjEwfQ%3D%3D)

    """)


