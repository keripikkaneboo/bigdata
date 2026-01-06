  Studi Kasus E-Commerce Brazil dan Data Inflasi

Proyek ini membangun pipeline Big Data untuk mengintegrasikan data transaksi e-commerce Brazil dengan data inflasi sebagai indikator ekonomi makro. Data e-commerce memiliki volume besar dan struktur kompleks, sedangkan data inflasi berasal dari institusi eksternal dalam bentuk data deret waktu. Perbedaan karakteristik dan kualitas data tersebut menuntut adanya proses pengolahan data yang terstruktur dan terotomatisasi agar dapat menghasilkan informasi yang siap dianalisis.

Arsitektur sistem terdiri dari beberapa lapisan utama, yaitu sumber data, pipeline pengolahan data, data warehouse, dan lapisan visualisasi. Data transaksi e-commerce dan data inflasi diekstraksi dari sumber masing-masing, kemudian diproses melalui pipeline ETL dan ELT. Hasil akhir kedua pipeline disimpan dalam data warehouse dengan skema star yang terdiri dari tabel fakta dan tabel dimensi. Data warehouse ini selanjutnya digunakan sebagai sumber data untuk dashboard analitik.

Pendekatan ETL (Extract, Transform, Load) digunakan untuk membersihkan, memvalidasi, dan mentransformasi data sebelum dimuat ke dalam data warehouse sehingga kualitas dan konsistensi data dapat terjaga sejak awal. Pendekatan ELT (Extract, Load, Transform) memuat data mentah terlebih dahulu ke dalam data warehouse, kemudian proses transformasi dilakukan langsung di dalam basis data menggunakan query SQL. ETL memberikan kontrol kualitas data yang lebih ketat, sedangkan ELT menawarkan fleksibilitas dan skalabilitas yang lebih tinggi.


Cara Menjalankan Pipeline

!sebelum menjalankan pipeline, masuk ke dalam direktori pipeline tersebut disimpan .../elt_pipeline atau .../etl_pipeline!

!sebelum menjalankan dashboard, masuk ke dalam direktori dashboart tersebut .../dashboard!

1. pip install -r requirements.txt
2. untuk menjalankan pipeline etl, masuk ke direktori etl_pipeline dan jalankan command berikut di terminal
   python main.py > ../logs/etl_pipeline.log
3. untuk menjalankan pipeline etl, masuk ke direktori elt_pipeline dan jalankan command berikut di terminal
   python main.py > ../logs/elt_pipeline.log
4. untuk menjalankan dashboard, pastikan dalam folder dashboard terdapat file Dashboard_ETL.pbix lalu jalankan command berikut streamlit run Dashboard.py
