import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import requests
from streamlit_lottie import st_lottie

# ================== FUNGSI LOTTIE ================== #
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ============ CUSTOM CSS UNTUK BACKGROUND ============ #
st.markdown(
    """
    <style>
        body, .stApp {
            background-color: #e6f9e6; /* Light green */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== INISIALISASI DATA ================== #
DATA_PATH = "data/laporan_limbah.csv"
os.makedirs("data", exist_ok=True)

if not os.path.exists(DATA_PATH):
    df_init = pd.DataFrame(columns=["Tanggal", "Jenis Limbah", "Volume (kg)", "Lokasi", "Keterangan"])
    df_init.to_csv(DATA_PATH, index=False)

ambang_batas_sni = {
    "Organik": 100.0,
    "Anorganik": 50.0,
    "B3": 50.0,
    "Cair": 30.0,
    "Padat": 40.0
}

def simpan_laporan(data):
    df = pd.read_csv(DATA_PATH)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

# ================== SIDEBAR NAVIGASI ================== #
st.sidebar.title("♻️ Navigasi Aplikasi")
menu = st.sidebar.radio("Pilih Halaman:", [
    "Beranda",
    "Formulir Pelaporan",
    "Riwayat Pelaporan",
    "Grafik Pengawasan",
    "K3 dari Limbah"
])

# ================== 0. BERANDA ================== #
if menu == "Beranda":
    st.title("🏠 Beranda Aplikasi Pelaporan Limbah")
    st.markdown(
        """
        ## 👋 Selamat Datang!
        Aplikasi ini dirancang untuk membantu proses **pelaporan, pengawasan, dan manajemen limbah** secara digital dan terstruktur.

        ### 🌟 Tujuan:
        - Menyederhanakan proses pencatatan limbah di lapangan.
        - Menyediakan grafik tren volume limbah untuk pemantauan.
        - Memberikan referensi keselamatan kerja (K3) untuk setiap jenis limbah.
        - **Memantau apakah limbah melebihi nilai ambang batas (NAB) SNI.**

        ### 👤 Pengguna:
        - Petugas kebersihan lingkungan
        - Staf pengelola limbah B3
        - Tim K3 perusahaan/instansi

        ### 🔧 Fitur Utama:
        - ✅ Formulir pelaporan limbah harian
        - 📄 Riwayat laporan yang tersimpan otomatis
        - 📈 Grafik volume limbah per hari & jenis dengan NAB
        - 🩺 Informasi K3 berdasarkan jenis limbah
        - 🗑️ Tombol hapus riwayat pelaporan (opsional)

        ### 📌 Cara Menggunakan:
        1. Masuk ke *Formulir Pelaporan* dan isi data sesuai kondisi di lapangan.
        2. Cek *Riwayat Pelaporan* untuk melihat laporan sebelumnya.
        3. Pantau tren di *Grafik Pengawasan*.
        4. Gunakan halaman *K3 dari Limbah* untuk memastikan penanganan yang aman.
        """
    )

# ================== 1. FORMULIR PELAPORAN ================== #
elif menu == "Formulir Pelaporan":
    st.title("📝 Formulir Pelaporan Limbah")
    st.markdown(
        """
        Halaman ini digunakan untuk mengisi dan mengirim laporan limbah.
        """
    )

    with st.form("form_limbah"):
        tanggal = st.date_input("Tanggal", value=datetime.today())
        jenis = st.selectbox("Jenis Limbah", list(ambang_batas_sni.keys()))
        volume = st.number_input("Volume (kg)", min_value=0.0, step=0.1)
        lokasi = st.text_input("Lokasi")
        keterangan = st.text_area("Keterangan")

        st.info(f"NAB SNI untuk limbah {jenis} adalah {ambang_batas_sni[jenis]} kg.")

        submitted = st.form_submit_button("Kirim Laporan")

        if submitted:
            if volume > ambang_batas_sni[jenis]:
                st.warning(f"⚠️ Volume limbah melebihi NAB SNI ({ambang_batas_sni[jenis]} kg).")
            data = {
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Jenis Limbah": jenis,
                "Volume (kg)": volume,
                "Lokasi": lokasi,
                "Keterangan": keterangan
            }
            simpan_laporan(data)
            st.success("✅ Laporan berhasil dikirim!")

# ================== 2. RIWAYAT PELAPORAN ================== #
elif menu == "Riwayat Pelaporan":
    st.title("📄 Riwayat Pelaporan")
    df = pd.read_csv(DATA_PATH)

    if df.empty:
        st.info("Belum ada laporan.")
    else:
        st.dataframe(df)

        with st.expander("⚠️ Hapus Semua Riwayat", expanded=False):
            st.warning("Tindakan ini akan menghapus **semua** data laporan secara permanen.")
            if st.checkbox("Saya yakin ingin menghapus semua data.") and st.button("🗑️ Hapus Semua Data"):
                df = pd.DataFrame(columns=["Tanggal", "Jenis Limbah", "Volume (kg)", "Lokasi", "Keterangan"])
                df.to_csv(DATA_PATH, index=False)
                st.success("✅ Semua riwayat berhasil dihapus.")
                st.experimental_rerun()

# ================== 3. GRAFIK PENGAWASAN ================== #
elif menu == "Grafik Pengawasan":
    st.title("📈 Grafik Pengawasan Limbah")
    df = pd.read_csv(DATA_PATH)

    if df.empty:
        st.warning("Belum ada data untuk ditampilkan.")
    else:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        grouped = df.groupby(["Tanggal", "Jenis Limbah"])["Volume (kg)"].sum().unstack().fillna(0)

        st.subheader("Tren Volume Limbah per Hari")
        fig, ax = plt.subplots(figsize=(10, 5))
        grouped.plot(ax=ax)

        for jenis, batas in ambang_batas_sni.items():
            if jenis in grouped.columns:
                ax.axhline(y=batas, color='r', linestyle='--', linewidth=1, alpha=0.7)
                ax.text(grouped.index[-1], batas, f"NAB {jenis}: {batas}", color='r', fontsize=8, va='bottom', ha='right')

        plt.xlabel("Tanggal")
        plt.ylabel("Volume (kg)")
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(fig)

# ================== 4. K3 DARI LIMBAH ================== #
elif menu == "K3 dari Limbah":
    st.title("🩺 K3 dari Limbah")

    # Animasi Lottie
    lottie_json = load_lottieurl("https://lottie.host/9d8b6315-5325-4d75-873a-de0de745464f/5kP3gMsiYc.json")
    if lottie_json:
        st_lottie(lottie_json, height=200, key="K3 dari Limbah")

    st.markdown(
        """
        Halaman ini memberikan informasi K3 (Keselamatan dan Kesehatan Kerja) berdasarkan jenis limbah.
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
