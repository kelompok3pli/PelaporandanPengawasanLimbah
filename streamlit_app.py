import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Inisialisasi file laporan
DATA_PATH = "data/laporan_limbah.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    df_init = pd.DataFrame(columns=["Tanggal", "Jenis Limbah", "Volume (kg)", "Lokasi", "Keterangan"])
    df_init.to_csv(DATA_PATH, index=False)

# Fungsi untuk menyimpan data
def simpan_laporan(data):
    df = pd.read_csv(DATA_PATH)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

# Sidebar
st.sidebar.title("📊 Menu Utama")
menu = st.sidebar.radio("Pilih Halaman:", ["Formulir Pelaporan", "Riwayat Pelaporan", "Grafik Pengawasan"])

# Halaman 1: Formulir Pelaporan
if menu == "Formulir Pelaporan":
    st.title("📝 Formulir Pelaporan Limbah")
    st.markdown(
        """
        Halaman ini digunakan untuk mengisi dan mengirim laporan limbah yang dihasilkan.
        Silakan lengkapi semua kolom yang tersedia dan klik **Kirim Laporan**.
        """
    )
    with st.form("form_limbah"):
        tanggal = st.date_input("Tanggal", value=datetime.today())
        jenis = st.selectbox("Jenis Limbah", ["Organik", "Anorganik", "B3", "Cair", "Padat"])
        volume = st.number_input("Volume (kg)", min_value=0.0, step=0.1)
        lokasi = st.text_input("Lokasi")
        keterangan = st.text_area("Keterangan")

        submitted = st.form_submit_button("Kirim Laporan")

        if submitted:
            data = {
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Jenis Limbah": jenis,
                "Volume (kg)": volume,
                "Lokasi": lokasi,
                "Keterangan": keterangan
            }
            simpan_laporan(data)
            st.success("✅ Laporan berhasil dikirim!")

# Halaman 2: Riwayat Pelaporan
elif menu == "Riwayat Pelaporan":
    st.title("📄 Riwayat Pelaporan")
    st.markdown(
        """
        Halaman ini menampilkan seluruh laporan limbah yang telah dikirim.
        Data ditampilkan dalam bentuk tabel agar dapat ditinjau kembali.
        """
    )
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        st.info("Belum ada laporan.")
    else:
        st.dataframe(df)

# Halaman 3: Grafik Pengawasan
elif menu == "Grafik Pengawasan":
    st.title("📈 Grafik Pengawasan Limbah")
    st.markdown(
        """
        Halaman ini menampilkan visualisasi grafik tren volume limbah berdasarkan jenis dan tanggal.
        Grafik membantu memantau peningkatan atau penurunan limbah dari waktu ke waktu.
        """
    )
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        st.warning("Belum ada data untuk ditampilkan.")
    else:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        limbah_grouped = df.groupby(["Tanggal", "Jenis Limbah"])["Volume (kg)"].sum().unstack().fillna(0)

        st.subheader("Tren Volume Limbah per Hari")
        fig, ax = plt.subplots()
        limbah_grouped.plot(ax=ax)
        plt.xlabel("Tanggal")
        plt.ylabel("Volume (kg)")
        plt.xticks(rotation=45)
        st.pyplot(fig)
