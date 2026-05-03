import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
import os

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
)

# ─── Load & Prepare Data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    df_day = pd.read_csv(os.path.join(script_dir, "main_data.csv"), parse_dates=["dteday"])
    df_hour = pd.read_csv(os.path.join(script_dir, "main_data_hour.csv"), parse_dates=["dteday"])

    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_map = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
    weekday_map = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}

    for df in [df_day, df_hour]:
        df["season_label"] = df["season"].map(season_map)
        df["weather_label"] = df["weathersit"].map(weather_map)
    df_day["weekday_label"] = df_day["weekday"].map(weekday_map)
    df_day["year_label"] = df_day["yr"].map({0: "2011", 1: "2012"})
    df_hour["is_weekend"] = df_hour["weekday"].isin([0, 6])

    # Clustering
    bins = [0, 2000, 4000, 6000, 10000]
    cluster_labels = ["Low (0–2k)", "Medium (2k–4k)", "High (4k–6k)", "Peak (6k+)"]
    df_day["usage_cluster"] = pd.cut(df_day["cnt"], bins=bins, labels=cluster_labels)

    return df_day, df_hour

df_day, df_hour = load_data()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/bike.png", width=80)
st.sidebar.title("🚲 Bike Sharing")
st.sidebar.markdown("**Capital Bikeshare — Washington D.C.**")
st.sidebar.markdown("Data periode: **2011–2012**")
st.sidebar.markdown("---")

year_options = ["All", "2011", "2012"]
selected_year = st.sidebar.selectbox("Pilih Tahun", year_options)

season_options = ["All"] + list(df_day["season_label"].unique())
selected_season = st.sidebar.selectbox("Pilih Musim", season_options)

st.sidebar.markdown("---")
st.sidebar.caption("📊 Proyek Analisis Data — Dicoding")

# ─── Filter Data ─────────────────────────────────────────────────────────────
df_filtered = df_day.copy()
if selected_year != "All":
    df_filtered = df_filtered[df_filtered["year_label"] == selected_year]
if selected_season != "All":
    df_filtered = df_filtered[df_filtered["season_label"] == selected_season]

df_hour_filtered = df_hour.copy()
if selected_year != "All":
    yr_val = 0 if selected_year == "2011" else 1
    df_hour_filtered = df_hour_filtered[df_hour_filtered["yr"] == yr_val]

# ─── Header ──────────────────────────────────────────────────────────────────
st.title("🚲 Bike Sharing Analytics Dashboard")
st.markdown("Analisis pola peminjaman sepeda berdasarkan musim, jam, dan kondisi cuaca.")
st.markdown("---")

# ─── KPI Metrics ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Peminjaman", f"{df_filtered['cnt'].sum():,.0f}")
col2.metric("Rata-rata Harian", f"{df_filtered['cnt'].mean():,.0f}")
col3.metric("Hari Tertinggi", f"{df_filtered['cnt'].max():,.0f}")
col4.metric("Hari Terendah", f"{df_filtered['cnt'].min():,.0f}")

st.markdown("---")

# ─── Tab Layout ──────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🍂 Analisis Musiman", "🕐 Pola Per Jam", "📊 Clustering & Tren"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Analisis Musiman
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Pertanyaan 1: Bagaimana Pola Peminjaman Antar Musim?")
    st.markdown(
        "Rata-rata dan distribusi peminjaman harian per musim, "
        "mengungkap musim mana yang paling produktif untuk layanan bike-sharing."
    )

    season_colors = {"Spring": "#4CAF50", "Summer": "#FF9800", "Fall": "#D32F2F", "Winter": "#1565C0"}
    season_order = ["Spring", "Summer", "Fall", "Winter"]

    col_a, col_b = st.columns(2)

    with col_a:
        fig, ax = plt.subplots(figsize=(6, 4))
        season_avg = df_filtered.groupby("season_label", observed=True)["cnt"].mean().reindex(season_order).dropna()
        bars = ax.bar(season_avg.index, season_avg.values,
                      color=[season_colors.get(s, "#999") for s in season_avg.index],
                      edgecolor="white", linewidth=1.2)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                    f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_title("Rata-rata Peminjaman Harian per Musim", fontsize=11, fontweight="bold")
        ax.set_xlabel("Musim")
        ax.set_ylabel("Rata-rata Peminjaman")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_ylim(0, season_avg.max() * 1.2 if len(season_avg) > 0 else 8000)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        fig, ax = plt.subplots(figsize=(6, 4))
        data_per_season = [df_filtered[df_filtered["season_label"] == s]["cnt"].values for s in season_order
                           if len(df_filtered[df_filtered["season_label"] == s]) > 0]
        valid_seasons = [s for s in season_order if len(df_filtered[df_filtered["season_label"] == s]) > 0]
        if data_per_season:
            bp = ax.boxplot(data_per_season, labels=valid_seasons, patch_artist=True, notch=False)
            for patch, season in zip(bp["boxes"], valid_seasons):
                patch.set_facecolor(season_colors.get(season, "#999"))
                patch.set_alpha(0.7)
        ax.set_title("Distribusi Peminjaman Harian per Musim", fontsize=11, fontweight="bold")
        ax.set_xlabel("Musim")
        ax.set_ylabel("Jumlah Peminjaman")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.info(
        "💡 **Insight**: Fall (Gugur) secara konsisten menghasilkan rata-rata peminjaman tertinggi, "
        "diikuti Summer, Winter, dan Spring. Perbedaan antar musim mencapai >2x lipat antara Fall dan Spring."
    )

    # Tabel ringkasan
    st.markdown("#### Ringkasan Statistik per Musim")
    season_summary = df_filtered.groupby("season_label", observed=True)["cnt"].agg(
        Jumlah_Hari="count", Rata_rata="mean", Total="sum", Std_Dev="std"
    ).round(0).reindex(season_order).dropna()
    st.dataframe(season_summary.style.format("{:,.0f}").background_gradient(cmap="YlOrRd"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Pola Per Jam
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Pertanyaan 2: Pola Peminjaman Per Jam — Weekday vs. Weekend")
    st.markdown(
        "Analisis pola hourly mengungkap perbedaan fundamental antara perilaku "
        "commuter (weekday) dan pengguna rekreasional (weekend)."
    )

    fig, ax = plt.subplots(figsize=(12, 4.5))

    for is_wknd, label, color, ls in [(False, "Weekday", "#1565C0", "-"), (True, "Weekend", "#D32F2F", "--")]:
        sub = df_hour_filtered[df_hour_filtered["is_weekend"] == is_wknd].groupby("hr")["cnt"].mean()
        ax.plot(sub.index, sub.values, label=label, color=color, linewidth=2.5,
                linestyle=ls, marker="o", markersize=4)

    # Shading jam sibuk
    ax.axvspan(7, 9, alpha=0.07, color="blue")
    ax.axvspan(16, 19, alpha=0.07, color="blue")

    # Anotasi puncak
    wkday_hr = df_hour_filtered[df_hour_filtered["is_weekend"] == False].groupby("hr")["cnt"].mean()
    wkend_hr = df_hour_filtered[df_hour_filtered["is_weekend"] == True].groupby("hr")["cnt"].mean()

    if len(wkday_hr) > 0:
        pk = wkday_hr.idxmax()
        ax.annotate(f"Weekday Peak\nJam {pk}:00 ({wkday_hr[pk]:.0f})",
                    xy=(pk, wkday_hr[pk]), xytext=(pk - 4, wkday_hr[pk] + 40),
                    arrowprops=dict(arrowstyle="->", color="#1565C0"), fontsize=9, color="#1565C0")
    if len(wkend_hr) > 0:
        pk2 = wkend_hr.idxmax()
        ax.annotate(f"Weekend Peak\nJam {pk2}:00 ({wkend_hr[pk2]:.0f})",
                    xy=(pk2, wkend_hr[pk2]), xytext=(pk2 + 1.5, wkend_hr[pk2] - 60),
                    arrowprops=dict(arrowstyle="->", color="#D32F2F"), fontsize=9, color="#D32F2F")

    ax.set_title("Rata-rata Peminjaman Sepeda per Jam\nWeekday vs. Weekend", fontsize=12, fontweight="bold")
    ax.set_xlabel("Jam dalam Sehari (0–23)")
    ax.set_ylabel("Rata-rata Peminjaman")
    ax.set_xticks(range(0, 24))
    ax.legend(fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info(
        "💡 **Insight**: Weekday menunjukkan pola **bimodal** (puncak pagi & sore = commuting), "
        "sedangkan Weekend menunjukkan pola **unimodal** (puncak siang = rekreasi). "
        "Titik terendah kedua tipe hari ada di dini hari (03:00–04:00)."
    )

    # Tabel puncak per jam
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**Top 5 Jam Tertinggi — Weekday**")
        if len(wkday_hr) > 0:
            st.dataframe(
                wkday_hr.sort_values(ascending=False).head(5).reset_index()
                .rename(columns={"hr": "Jam", "cnt": "Avg Peminjaman"})
                .style.format({"Avg Peminjaman": "{:.1f}"}),
                use_container_width=True
            )
    with col_d:
        st.markdown("**Top 5 Jam Tertinggi — Weekend**")
        if len(wkend_hr) > 0:
            st.dataframe(
                wkend_hr.sort_values(ascending=False).head(5).reset_index()
                .rename(columns={"hr": "Jam", "cnt": "Avg Peminjaman"})
                .style.format({"Avg Peminjaman": "{:.1f}"}),
                use_container_width=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Clustering & Tren
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Analisis Lanjutan: Clustering & Tren Bulanan")

    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown("#### Distribusi Cluster Penggunaan")
        cluster_count = df_filtered["usage_cluster"].value_counts().sort_index()
        cluster_colors_list = ["#42A5F5", "#66BB6A", "#FFA726", "#EF5350"]
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(cluster_count.values, labels=cluster_count.index,
               autopct="%1.1f%%", colors=cluster_colors_list, startangle=90,
               wedgeprops={"edgecolor": "white", "linewidth": 1.5})
        ax.set_title("Segmentasi Hari Berdasarkan Volume", fontsize=11, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_f:
        st.markdown("#### Cluster vs. Musim (Heatmap)")
        if len(df_filtered) > 0:
            cross = pd.crosstab(df_filtered["usage_cluster"], df_filtered["season_label"])
            for col in ["Spring", "Summer", "Fall", "Winter"]:
                if col not in cross.columns:
                    cross[col] = 0
            cross = cross[["Spring", "Summer", "Fall", "Winter"]]
            fig, ax = plt.subplots(figsize=(5, 4))
            sns.heatmap(cross, annot=True, fmt="d", cmap="YlOrRd", ax=ax,
                        linewidths=0.5, cbar_kws={"label": "Jumlah Hari"})
            ax.set_title("Distribusi Cluster per Musim", fontsize=11, fontweight="bold")
            ax.set_xlabel("Musim")
            ax.set_ylabel("Cluster")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    st.markdown("#### Tren Peminjaman Bulanan (2011 vs 2012)")
    monthly = df_day.groupby(["yr", "mnth"], observed=True)["cnt"].mean().reset_index()
    monthly["year_label"] = monthly["yr"].map({0: "2011", 1: "2012"})
    month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                   7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    monthly["month_name"] = monthly["mnth"].map(month_names)

    fig, ax = plt.subplots(figsize=(11, 4))
    colors_yr = {"2011": "#42A5F5", "2012": "#EF5350"}
    for yr, grp in monthly.groupby("year_label"):
        ax.plot(grp["mnth"], grp["cnt"], label=yr, color=colors_yr[yr],
                linewidth=2.5, marker="o", markersize=5)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([month_names[i] for i in range(1, 13)])
    ax.set_title("Rata-rata Peminjaman Harian per Bulan — 2011 vs. 2012", fontsize=12, fontweight="bold")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Rata-rata Peminjaman")
    ax.legend(title="Tahun", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info(
        "💡 **Insight**: Terjadi pertumbuhan YoY yang konsisten di 2012 vs. 2011 di hampir semua bulan. "
        "Pola musiman berulang: naik dari bulan 4–9 (musim hangat) dan turun di akhir/awal tahun."
    )

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📌 Dashboard ini dibuat sebagai bagian dari Proyek Analisis Data — Dicoding | Data: Capital Bikeshare, Washington D.C.")
