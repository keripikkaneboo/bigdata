import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from config import RAW_DIR, FILE_INFLATION_CLEAN

sns.set_theme(style="whitegrid")

class InflationTransformer:
    def __init__(self, raw_path):
        self.raw_path = raw_path
        self.df = None
        self.df_raw = None
        self.months = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        self.quality_report = {}

    def load_data(self):
        print("[INFO] Source 2: Memuat dataset inflasi...")
        file_path = os.path.join(self.raw_path, 'brazil.inflation.monthly (statbureau.org).csv')

        try:
            self.df_raw = pd.read_csv(file_path)
        except FileNotFoundError:
             print(f"Error: File {file_path} tidak ditemukan.")
             exit()

        self.df_raw.columns = self.df_raw.columns.str.strip()

        if 'Total' in self.df_raw.columns:
            self.df_raw = self.df_raw.drop(columns=['Total'])

        self.df = self.df_raw.copy()
        return self.df

    def _generate_detailed_report(self, df, title, color):
        print("\n" + "="*60)
        print(f"{title}")
        print("="*60)
        print(f"Total Baris: {df.shape[0]} | Total Kolom: {df.shape[1]}")

        print("\n[1] Missing Values per Kolom:")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("Tidak ada missing value.")

        print("\n[2] Cek Duplikasi:")
        print(f"Baris duplikat penuh: {df.duplicated().sum()}")
        year_pk_col = 'Year' if 'Year' in df.columns else 'year'
        if year_pk_col in df.columns:
            print(f"Duplikat Primary Key ({year_pk_col}): {df.duplicated(subset=[year_pk_col]).sum()}")

        print("\n[3] Menampilkan Visualisasi Boxplot (Seluruh Bulan)...")
        plt.figure(figsize=(12, 4))
        current_month_cols = [m for m in self.months if m in df.columns]
        if not current_month_cols:
            current_month_cols = [m.lower() for m in self.months if m.lower() in df.columns]
        
        if year_pk_col in df.columns and current_month_cols:
            df_plot = df.melt(id_vars=[year_pk_col], value_vars=current_month_cols)
            sns.boxplot(data=df_plot, x='variable', y='value', color=color)
            plt.title(f"Sebaran Data Inflasi per Bulan")
            plt.xticks(rotation=45)
            plt.show()

        print("\n[4] Statistik Deskriptif Outlier (IQR) - Sampel Januari & Juli:")
        sample_cols = ['January', 'July'] if 'January' in df.columns else ['january', 'july']
        for col in sample_cols:
            if col in df.columns:
                Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                print(f"- Kolom '{col}': Terdeteksi {len(outliers)} outliers ({round(len(outliers)/len(df)*100, 2)}%)")

    def pre_transformation_report(self):
        self._generate_detailed_report(self.df_raw, "SOURCE 2: LAPORAN SEBELUM TRANSFORMASI", "salmon")

    def transform_pipeline(self):
        print("\n" + "="*60)
        print("MEMULAI PROSES TRANSFORMASI (CLEANING & ENGINEERING)")
        print("="*60)

        self.df.drop_duplicates(subset=['Year'] if 'Year' in self.df.columns else ['year'], inplace=True)
        for month in self.months:
            if month in self.df.columns:
                self.df[month] = self.df[month].fillna(self.df[month].median())
                Q1, Q3 = self.df[month].quantile(0.25), self.df[month].quantile(0.75)
                IQR = Q3 - Q1
                self.df[month] = np.clip(self.df[month], Q1 - 1.5*IQR, Q3 + 1.5*IQR)
        self.df.columns = [c.lower().strip() for c in self.df.columns]
        scaler = MinMaxScaler()
        self.df[['january_norm', 'december_norm']] = scaler.fit_transform(self.df[['january', 'december']])

        month_cols = [m.lower() for m in self.months]
        self.df['yearly_avg'] = self.df[month_cols].mean(axis=1)
        self.df['yearly_max'] = self.df[month_cols].max(axis=1)
        self.df['yearly_std'] = self.df[month_cols].std(axis=1)
        self.df['is_volatile'] = (self.df['yearly_std'] > 0.5).astype(int)
        self.df['year_trend_diff'] = self.df['december'] - self.df['january']

        print("\nTransformasi Selesai.")
        return self.df

    def validate_quality_data(self):
        print("\n" + "="*60)
        print("TAHAP 5: VALIDASI KUALITAS DATA SOURCE 2")
        print("="*60)

        unique_check = self.df['year'].is_unique
        null_check = self.df.isnull().sum().sum() == 0
        range_check = (self.df['year'] >= 1980).all()
        dtype_check = pd.api.types.is_numeric_dtype(self.df['january'])
        ref_integrity = self.df['year'].notnull().all()
        skew_val = self.df['yearly_avg'].skew()

        self.quality_report = {
            "1. Uniqueness (Year)": "PASSED" if unique_check else "FAILED",
            "2. Null Check (Total)": "PASSED" if null_check else "FAILED",
            "3. Range Check (Year >= 1980)": "PASSED" if range_check else "FAILED",
            "4. Datatype (Numeric Rate)": "PASSED" if dtype_check else "FAILED",
            "5. Referential Integrity": "PASSED" if ref_integrity else "FAILED",
            "6. Distribution (Yearly Avg Skew)": f"{skew_val:.2f}"
        }

        for rule, status in self.quality_report.items():
            print(f"{rule:<35} : {status}")

    def post_transformation_report(self):
        original_months = self.months.copy()
        self.months = [m.lower() for m in self.months]
        self._generate_detailed_report(self.df, "SOURCE 2: LAPORAN SESUDAH TRANSFORMASI", "lightgreen")
        self.months = original_months

if __name__ == "__main__":
    path_s2 = RAW_DIR 
    trans2 = InflationTransformer(path_s2)
    trans2.load_data()
    trans2.pre_transformation_report()
    df_s2_final = trans2.transform_pipeline()
    trans2.post_transformation_report()
    trans2.validate_quality_data()
    print(f"\nMenyimpan data inflasi transformasi ke: {FILE_INFLATION_CLEAN}")
    df_s2_final.to_csv(FILE_INFLATION_CLEAN, index=False)