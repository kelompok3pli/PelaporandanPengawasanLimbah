import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Lokasi file data
DATA_PATH = "data/laporan_limbah.csv"
os.makedirs("data", exist_ok=True)

# Inisialisasi file jika belum ada
if not os.path.exists(DATA_PATH):
    df_init = pd.DataFrame(columns=["Tanggal", "Jenis Limbah", "Volume (kg)", "Lokasi", "Keterangan"])
    df_init.to_csv(DATA_PATH, index=False)

# Fungsi untuk menyimpan data laporan baru
def simpan_laporan(data):
    df = pd.read_csv(DATA_PATH)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

# Sidebar
st.sidebar.title("📊 Menu Utama")
menu = st.sidebar.radio("Pilih Halaman:", ["Formulir Pelaporan", "Riwayat Pelaporan", "Grafik Pengawasan"])

# ===========================
# 1. FORMULIR PELAPORAN
# ===========================
if menu == "Formulir Pelaporan":
    st.title("📝 Formulir Pelaporan Limbah")
    st.markdown(
        """
        Halaman ini digunakan untuk mengisi dan mengirim laporan limbah.
        Silakan lengkapi semua kolom pada formulir berikut ini.

        #### 📌 Petunjuk Pengisian:
        - **Tanggal:** Pilih tanggal pelaporan.
        - **Jenis Limbah:** Pilih kategori jenis limbah yang relevan.
        - **Volume (kg):** Masukkan volume limbah dalam satuan kilogram.
        - **Lokasi:** Masukkan lokasi tempat limbah ditemukan atau dihasilkan.
        - **Keterangan:** Tambahkan catatan penting jika ada.
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

# ===========================
# 2. RIWAYAT PELAPORAN
# ===========================
elif menu == "Riwayat Pelaporan":
    st.title("📄 Riwayat Pelaporan")
    st.markdown(
        """
        Halaman ini menampilkan seluruh laporan limbah yang telah dikirim.

        #### 📌 Petunjuk:
        - Data laporan ditampilkan dalam bentuk tabel.
        - Gunakan scroll atau filter (Ctrl+F) untuk mencari laporan tertentu.
        - Klik tombol hapus jika ingin membersihkan semua data.
        """
    )

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        st.info("Belum ada laporan.")
    else:
        st.dataframe(df)

        # Tombol hapus seluruh data
        with st.expander("⚠️ Hapus Semua Riwayat", expanded=False):
            st.warning("Tindakan ini akan menghapus **semua** data laporan secara permanen.")
            if st.checkbox("Saya yakin ingin menghapus semua data."):
                if st.button("🗑️ Hapus Semua Data"):
                    df = pd.DataFrame(columns=["Tanggal", "Jenis Limbah", "Volume (kg)", "Lokasi", "Keterangan"])
                    df.to_csv(DATA_PATH, index=False)
                    st.success("✅ Semua riwayat berhasil dihapus.")
                    st.experimental_rerun()

# ===========================
# 3. GRAFIK PENGAWASAN
# ===========================
elif menu == "Grafik Pengawasan":
    st.title("📈 Grafik Pengawasan Limbah")
    st.markdown(
        """
        Halaman ini menampilkan grafik tren volume limbah yang telah dilaporkan.

        #### 📌 Petunjuk:
        - Grafik menunjukkan total volume limbah berdasarkan **jenis** dan **tanggal**.
        - Gunakan grafik ini untuk memantau kecenderungan peningkatan atau penurunan limbah.
        """
    )

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        st.warning("Belum ada data untuk ditampilkan.")
    else:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        grouped = df.groupby(["Tanggal", "Jenis Limbah"])["Volume (kg)"].sum().unstack().fillna(0)

        st.subheader("Tren Volume Limbah per Hari")
        fig, ax = plt.subplots(figsize=(10, 5))
        grouped.plot(ax=ax)
        plt.xlabel("Tanggal")
        plt.ylabel("Volume (kg)")
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(fig)
