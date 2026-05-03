# 🚲 Bike Sharing Data Analysis Project

Proyek analisis data menggunakan **Bike Sharing Dataset** dari Capital Bikeshare, Washington D.C. (2011–2012).

## 📁 Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv          # Data harian (day.csv)
│   ├── main_data_hour.csv     # Data per jam (hour.csv)
│   └── dashboard.py           # Streamlit dashboard
├── data/
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb             # Jupyter Notebook analisis lengkap
├── README.md
├── requirements.txt
└── url.txt                    # Link Streamlit Cloud (jika di-deploy)
```

## 📋 Pertanyaan Bisnis

1. Bagaimana perbedaan rata-rata jumlah peminjaman sepeda harian antara empat musim selama 2011–2012?
2. Pada jam berapa rata-rata peminjaman mencapai puncak — weekday vs. weekend?

## 🛠️ Setup & Instalasi

### 1. Clone atau ekstrak folder submission

```bash
cd submission
```

### 2. (Opsional) Buat virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan Streamlit Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada alamat `http://localhost:8501`.

## 📊 Fitur Dashboard

- **Filter** berdasarkan Tahun (2011 / 2012 / All) dan Musim
- **Tab 1** — Analisis musiman: bar chart rata-rata & boxplot distribusi per musim
- **Tab 2** — Pola per jam: line chart weekday vs. weekend dengan anotasi puncak
- **Tab 3** — Clustering manual & tren bulanan 2011 vs. 2012

## 📌 Sumber Data

Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", *Progress in Artificial Intelligence* (2013), Springer Berlin Heidelberg.
