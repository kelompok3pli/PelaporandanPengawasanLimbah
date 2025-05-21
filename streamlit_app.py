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

# Sidebar Menu
st.sidebar.title("📊 Menu Utama")
menu = st.sidebar.radio("Pilih Halaman:", [
    "Formulir Pelaporan",
    "Riwayat Pelaporan",
    "Grafik Pengawasan",
    "K3 dari Limbah"
])

# ===========================
# 1. FORMULIR PELAPORAN
# ===========================
if menu == "Formulir Pelaporan":
    st.title("📝 Formulir Pelaporan Limbah")
    st.markdown(
        """
        Halaman ini digunakan untuk mengisi dan mengirim laporan limbah.

        #### 📌 Petunjuk Pengisian:
        - **Tanggal:** Pilih tanggal pelaporan.
        - **Jenis Limbah:** Pilih kategori jenis limbah.
        - **Volume (kg):** Masukkan volume dalam kilogram.
        - **Lokasi:** Tulis lokasi ditemukannya limbah.
        - **Keterangan:** Tambahkan catatan penting jika diperlukan.
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
        - Data ditampilkan dalam bentuk tabel.
        - Gunakan pencarian (Ctrl+F) untuk menemukan laporan.
        - Anda bisa menghapus semua riwayat jika diperlukan.
        """
    )

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        st.info("Belum ada laporan.")
    else:
        st.dataframe(df)

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
        Halaman ini menampilkan tren volume limbah berdasarkan tanggal dan jenis.

        #### 📌 Petunjuk:
        - Grafik menunjukkan volume limbah per hari.
        - Gunakan grafik untuk memantau tren penurunan atau kenaikan.
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

# ===========================
# 4. K3 DARI LIMBAH
# ===========================
elif menu == "K3 dari Limbah":
    st.title("🦺 K3 dari Limbah")
    st.markdown(
        """
        Halaman ini memberikan informasi K3 (Keselamatan dan Kesehatan Kerja)
        berdasarkan jenis limbah yang dilaporkan.

        #### 📌 Petunjuk:
        - Pilih jenis limbah untuk melihat potensi bahaya dan penanganan.
        - Gunakan informasi ini untuk menyusun SOP K3 internal.
        """
    )

    info_k3 = {
        "Organik": {
            "Bahaya": "Bau, gas metana, pembusukan, mikroorganisme.",
            "APD": "Sarung tangan, masker, pelindung mata.",
            "Penanganan": "Pisahkan dari limbah lain, komposkan jika memungkinkan."
        },
        "Anorganik": {
            "Bahaya": "Benda tajam, tidak terurai, bahan berbahaya.",
            "APD": "Sarung tangan tahan sobek, alas kaki tertutup.",
            "Penanganan": "Kumpulkan untuk daur ulang, hindari pembakaran."
        },
        "B3": {
            "Bahaya": "Racun, korosif, mudah terbakar, reaktif.",
            "APD": "Sarung tangan kimia, pelindung wajah, sepatu safety.",
            "Penanganan": "Ikuti SOP B3, simpan terpisah dan berlabel jelas."
        },
        "Cair": {
            "Bahaya": "Tumpahan, licin, kontaminasi air.",
            "APD": "Sarung tangan tahan air, pelindung kaki.",
            "Penanganan": "Simpan dalam wadah tertutup, jangan dicampur dengan limbah lain."
        },
        "Padat": {
            "Bahaya": "Debu, serpihan, tersandung.",
            "APD": "Masker, sarung tangan.",
            "Penanganan": "Bungkus rapi, pisahkan dari limbah basah."
        }
    }

    jenis_pilihan = st.selectbox("Pilih Jenis Limbah:", list(info_k3.keys()))
    st.subheader(f"🔍 Informasi K3 untuk Limbah: {jenis_pilihan}")
    st.write(f"**Potensi Bahaya:** {info_k3[jenis_pilihan]['Bahaya']}")
    st.write(f"**APD yang Disarankan:** {info_k3[jenis_pilihan]['APD']}")
    st.write(f"**Tindakan Penanganan:** {info_k3[jenis_pilihan]['Penanganan']}")
