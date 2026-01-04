import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from config import RAW_DIR, FILE_ECOMMERCE_CLEAN

sns.set_theme(style="whitegrid")

class OlistTransformer:
    def __init__(self, raw_path):
        self.raw_path = raw_path
        self.df = None
        self.df_raw = None
        self.quality_report = {}

    def load_and_merge_internal(self):
        print("Source 1: Memuat dataset...")
        try:
            orders = pd.read_csv(os.path.join(self.raw_path, 'olist_orders_dataset.csv'))
            items = pd.read_csv(os.path.join(self.raw_path, 'olist_order_items_dataset.csv'))
            cust = pd.read_csv(os.path.join(self.raw_path, 'olist_customers_dataset.csv'))
            prod = pd.read_csv(os.path.join(self.raw_path, 'olist_products_dataset.csv'))
        except FileNotFoundError as e:
            print(f"Error: {e}. Pastikan script Extract sudah dijalankan.")
            exit()

        df = items.merge(orders, on='order_id', how='left')
        df = df.merge(cust, on='customer_id', how='left')
        self.df_raw = df.merge(prod, on='product_id', how='left')
        self.df = self.df_raw.copy()
        return self.df

    def _generate_detailed_report(self, df, title, color):
        print("\n" + "="*60)
        print(f"{title}")
        print("="*60)
        print(f"Total Baris: {df.shape[0]}")
        print(f"Total Kolom: {df.shape[1]}")
     
        print("\n[1] Missing Values per Kolom:")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("Tidak ada missing value.")
   
        print("\n[2] Cek Duplikasi:")
        print(f"Baris duplikat penuh: {df.duplicated().sum()}")
        pk_cols = ['order_id', 'order_item_id']
        if all(col in df.columns for col in pk_cols):
             print(f"Duplikat Primary Key (order_id, order_item_id): {df.duplicated(subset=pk_cols).sum()}")
        
        # Note: Visualisasi akan mem-block eksekusi script sampai window ditutup
        num_cols = ['price', 'freight_value']
        print("\n[3] Menampilkan Visualisasi Boxplot... (Close window to continue)")
        plt.figure(figsize=(12, 4))
        for i, col in enumerate(num_cols):
            if col in df.columns:
                plt.subplot(1, 2, i+1)
                sns.boxplot(data=df, x=col, color=color)
                plt.title(f"Outlier: {col}")
        plt.tight_layout()
        plt.show()
       
        print("\n[4] Statistik Deskriptif Outlier (IQR):")
        for col in num_cols:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                print(f"- Kolom '{col}': Terdeteksi {len(outliers)} outliers ({round(len(outliers)/len(df)*100, 2)}%)")

    def pre_transformation_report(self):
        self._generate_detailed_report(self.df_raw, "SOURCE 1: LAPORAN SEBELUM TRANSFORMASI", "salmon")

    def transform_pipeline(self):
            print("\n" + "="*60)
            print("MEMULAI PROSES TRANSFORMASI (CLEANING & ENGINEERING)")
            print("="*60)
      
            self.df.drop_duplicates(subset=['order_id', 'order_item_id'], inplace=True)
            date_cols = ['order_purchase_timestamp', 'order_delivered_customer_date',
                        'order_estimated_delivery_date', 'order_approved_at']
            for col in date_cols:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
            self.df['order_delivered_customer_date'] = self.df['order_delivered_customer_date'].fillna(self.df['order_estimated_delivery_date'])
          
            num_cols_list = self.df.select_dtypes(include=[np.number]).columns
            self.df[num_cols_list] = self.df[num_cols_list].fillna(self.df[num_cols_list].median())
            obj_cols_list = self.df.select_dtypes(include=['object']).columns
            self.df[obj_cols_list] = self.df[obj_cols_list].fillna("Unknown")
        
            for col in ['price', 'freight_value']:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                self.df[col] = np.clip(self.df[col], Q1 - 1.5*IQR, Q3 + 1.5*IQR)
         
            self.df.columns = [c.lower().strip().replace(' ', '_') for c in self.df.columns]
            self.df['delivery_days'] = (self.df['order_delivered_customer_date'] - self.df['order_purchase_timestamp']).dt.days.clip(lower=0)
            self.df['total_order_value'] = self.df['price'] + self.df['freight_value']
            self.df['is_late'] = (self.df['order_delivered_customer_date'] > self.df['order_estimated_delivery_date']).astype(int)
            self.df['purchase_hour'] = self.df['order_purchase_timestamp'].dt.hour
            self.df['freight_ratio'] = self.df['freight_value'] / (self.df['price'] + 0.001)

            scaler = MinMaxScaler()
            self.df[['price_norm', 'freight_norm']] = scaler.fit_transform(self.df[['price', 'freight_value']])

            print("\nTransformasi Selesai.")
            return self.df

    def validate_quality_data(self):
            print("\n" + "="*60)
            print("TAHAP 5: VALIDASI KUALITAS DATA")
            print("="*60)

            unique_check = self.df.duplicated(subset=['order_id', 'order_item_id']).sum() == 0
            null_check = self.df[['order_id', 'price', 'customer_id']].isnull().sum().sum() == 0
            range_check = (self.df['price'] >= 0).all() and (self.df['freight_value'] >= 0).all()
            is_datetime = pd.api.types.is_datetime64_any_dtype(self.df['order_purchase_timestamp'])
            ref_integrity = self.df['customer_id'].notnull().all()
            price_skew = self.df['price'].skew()
          
            self.quality_report = {
                "1. Uniqueness (Order Key)": "PASSED" if unique_check else "FAILED",
                "2. Null Check (Critical Cols)": "PASSED" if null_check else "FAILED",
                "3. Range Check (Price >= 0)": "PASSED" if range_check else "FAILED",
                "4. Datatype (Timestamp)": "PASSED" if is_datetime else "FAILED",
                "5. Referential Integrity": "PASSED" if ref_integrity else "FAILED",
                "6. Distribution (Price Skew)": f"{price_skew:.2f} (Normal Range: -2 to 2)"
            }

            for rule, status in self.quality_report.items():
                print(f"{rule:<30} : {status}")
          
            return self.quality_report

    def post_transformation_report(self):
        self._generate_detailed_report(self.df, "SOURCE 1: LAPORAN SESUDAH TRANSFORMASI", "lightgreen")

if __name__ == "__main__":
    path_s1 = RAW_DIR
    trans1 = OlistTransformer(path_s1)
    trans1.load_and_merge_internal()
    trans1.pre_transformation_report()
    df_s1_final = trans1.transform_pipeline()
    trans1.post_transformation_report()
    trans1.validate_quality_data()
    print(f"\nMenyimpan data transformasi ke: {FILE_ECOMMERCE_CLEAN}")
    df_s1_final.to_csv(FILE_ECOMMERCE_CLEAN, index=False)