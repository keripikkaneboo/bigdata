Judul: Analisis Sentimen Data Review Aplikasi Gojek

Tujuan: Proyek ini mengolah data review aplikasi gojek yang diambil dari Kaggle dan digabungkan dengan data hasil scrapping aplikasi Gojek dari Google Playstore, kolom yang diambil yaitu content, score, review created version, app version, dan at. Data diolah dengan melakukan sentiment analisis yang meliputi normalisasi menggunakan nltk dan kamus baku bahasa indonesia, tokenisasi, stopwords, dan stemming. dengan melakukan 3 model, tujuan proyek ini yaitu untuk membangun model yang dapat memprediksi review positif atau negatif dan diharapkan dapat membantu para pengembang untuk menerima dan memfilter masukan dari user aplikasi Gojek dari Google Playstore.

Anggota
1. Kevin Justivio Rachman Ali (1103223068).
2. Enrico Chandra Nugroho (1103220234).

How to run:
NOTE: Old data merupakan dataset lama yang tidak digunakan kembali, Raw data merupakan data mentah.
NOTE: codingan sering dijalankan pada Google Collab, oleh karena itu banyak awal codingan yang diawali dengan "!gdown" yang digunakan untuk mendownload file yang dibutuhkan dari google drive. untuk menjalankan, ganti file pathnya sesuai dengan lokasi data tersebut disimpan (file - file yang dibutuhkan ada pada bagian Dataset).


1. jalankan file .ipynb mulai dari app_scraper, codingan ini untuk mengambil data scrappingnya.

2. lalu jalankan file Processing_and_Cleaning_data_gojek.ipynb, codingan ini untuk melakukan penggabungan data, cleaning data, dll.

3. lalu jalankan reduce.ipynb, codingan ini akan mengurangi jumlah baris data agar proses tidak memakan waktu yang lama dan mengacak urutan datanya (agar isi file gabungan membaur).

4. lalu jalankan labelling.ipynb, codingan ini akan memberikan label pada setiap review yang ada di dalam file.

5. terakhir, jalankan modelling.ipynb, ini akan mengtrain 3 model (CNN, BiLSTM, dan LightBGM).
