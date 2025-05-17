import streamlit as st
import pandas as pd
from datetime import datetime
import os


# SETUP FILE DAN KONSTANTA
os.makedirs("data", exist_ok=True)
PRODUKSI_FILE = 'data/data_produksi.csv'
PENJUALAN_FILE = 'data/data_penjualan.csv'
KEUANGAN_FILE = 'data/laporan_keuangan.csv'
STOK_FILE = 'data/stok.csv'
PENGISIAN_STOK_FILE = 'data/pengisian_stok.csv'
HARGA_BIBIT = 10000
HARGA_PUPUK = 5000
HARGA_PESTISIDA = 15000
HARGA_KOL = 4000

# FUNGSI BANTUAN
def simpan_data(df, file):
    df.to_csv(file)

def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file, index_col=0)
    return pd.DataFrame()

def load_stok():
    if os.path.exists(STOK_FILE):
        df = pd.read_csv(STOK_FILE)
        if not df.empty and 'Stok' in df.columns:
            value = df.iloc[0]['Stok']
            if pd.notna(value):
                return int(value)
    return 1000

def simpan_stok(stok_baru):
    df = pd.DataFrame([{"Stok": stok_baru}])
    df.to_csv(STOK_FILE, index=False)

# SISTEM LOGIN
ALLOWED_USERS = ["admin1@kolme.com", "admin2@kolme.com", "admin3@kolme.com", "admin4@kolme.com"]
PASSWORD = "kol123"

if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    st.title(":material/person: Login Sistem KOL-ME")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button(":material/login: Login"):
        if username in ALLOWED_USERS and password == PASSWORD:
            st.session_state["login"] = True
            st.session_state["username"] = username
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah.")
else:
    #Navigasi
    st.markdown(f" Login sebagai: `{st.session_state['username']}`")
    with st.sidebar:
        st.image("assets/LOGO_KECIL.png", width=50)
        st.markdown(f":material/person: Login sebagai:\n`{st.session_state['username']}`")
        halaman = st.selectbox("Pilih Halaman", ["Home", "Produksi", "Penjualan", "Isi Stok", "Laporan"])
        st.session_state["halaman"] = halaman
        if st.button(":material/logout: Logout"):
            st.session_state["login"] = False
            st.rerun()


    # HALAMAN HOME
    if halaman == 'Home':
        st.title(":material/home: Home")
        st.image('assets/KOL_ME.jpg', width=250)
        st.markdown("""
        Selamat datang di aplikasi manajemen produksi dan penjualan KOL-ME!

        Aplikasi ini membantu Anda mencatat:
        - Transaksi produksi
        - Transaksi penjualan
        - Laporan keuangan otomatis
        - Penambahan dan pengurangan stok kol
        """)

    # HALAMAN PRODUKSI
    elif halaman == 'Produksi':
        st.title(":material/box_add: Tambah Transaksi Produksi")
        tanggal = st.date_input("Tanggal Produksi", value=datetime.today())
        bibit = st.number_input("Bibit (Kg)", 0)
        pupuk = st.number_input("Pupuk (Kg)", 0)
        pestisida = st.number_input("Pestisida (Liter)", 0)
        total = bibit * HARGA_BIBIT + pupuk * HARGA_PUPUK + pestisida * HARGA_PESTISIDA
        st.info(f"Total Biaya Produksi: Rp {total:,.0f}")

        if st.button(":material/save: Simpan Produksi"):
            df = load_data(PRODUKSI_FILE)
            new = pd.DataFrame([{
                "Tanggal": tanggal,
                "Bibit (Kg)": bibit,
                "Pupuk (Kg)": pupuk,
                "Pestisida (L)": pestisida,
                "Total Biaya": total
            }])
            df = pd.concat([df, new], ignore_index=True)
            simpan_data(df, PRODUKSI_FILE)

            df_keuangan = load_data(KEUANGAN_FILE)
            tanggal_str = tanggal.strftime("%Y-%m-%d")
            transaksi_keuangan = pd.DataFrame([
                {"Tanggal": tanggal_str, "Keterangan": "Beban Produksi", "Debit": total, "Kredit": 0},
                {"Tanggal": tanggal_str, "Keterangan": "     Kas", "Debit": 0, "Kredit": total}
            ])
            df_keuangan = pd.concat([df_keuangan, transaksi_keuangan], ignore_index=True)
            simpan_data(df_keuangan, KEUANGAN_FILE)

            st.success("✅ Data produksi dan laporan keuangan disimpan!")

        st.subheader("Riwayat Transaksi Produksi")
        produksi_df = load_data(PRODUKSI_FILE)
        if not produksi_df.empty:
            produksi_df["Tanggal"] = pd.to_datetime(produksi_df["Tanggal"])
            st.dataframe(produksi_df.sort_values("Tanggal", ascending=False))
        else:
            st.info("Belum ada data produksi.")

    # HALAMAN PENJUALAN
    elif halaman == 'Penjualan':
        st.title(":material/shopping_cart: Tambah Transaksi Penjualan")
        stok_kol = load_stok()
        st.markdown(f" **Stok Kol Saat Ini:** {stok_kol} Kg")

        tanggal_jual = st.date_input("Tanggal Penjualan", value=datetime.today())
        kode = f"J-{tanggal_jual.strftime('%Y%m%d')}"
        st.text_input("Kode Transaksi", value=kode, disabled=True)

        jumlah = st.number_input("Jumlah Kol Terjual (Kg)", 0)
        total = jumlah * HARGA_KOL
        st.info(f"Total Penjualan: Rp {total:,.0f}")

        if st.button(":material/save: Simpan Penjualan"):
            if jumlah > stok_kol:
                st.error(f"❌ Jumlah kol yang dijual melebihi stok! Stok tersedia: {stok_kol} Kg")
            else:
                df = load_data(PENJUALAN_FILE)
                new = pd.DataFrame([{
                    "Tanggal": tanggal_jual,
                    "Kode Transaksi": kode,
                    "Jumlah Kol (Kg)": jumlah,
                    "Total Penjualan": total
                }])
                df = pd.concat([df, new], ignore_index=True)
                simpan_data(df, PENJUALAN_FILE)

                stok_kol -= jumlah
                simpan_stok(stok_kol)

                df_keuangan = load_data(KEUANGAN_FILE)
                tanggal_str = tanggal_jual.strftime("%Y-%m-%d")
                transaksi_keuangan = pd.DataFrame([
                    {"Tanggal": tanggal_str, "Keterangan": "Kas", "Debit": total, "Kredit": 0},
                    {"Tanggal": tanggal_str, "Keterangan": "     Penjualan Kol", "Debit": 0, "Kredit": total}
                ])
                df_keuangan = pd.concat([df_keuangan, transaksi_keuangan], ignore_index=True)
                simpan_data(df_keuangan, KEUANGAN_FILE)

                st.success("✅ Data penjualan dan laporan keuangan disimpan!")

        st.subheader("Riwayat Transaksi Penjualan")
        df_penjualan = load_data(PENJUALAN_FILE)
        if not df_penjualan.empty:
            df_penjualan["Tanggal"] = pd.to_datetime(df_penjualan["Tanggal"])
            st.dataframe(df_penjualan.sort_values("Tanggal", ascending=False))
        else:
            st.info("Belum ada data penjualan.")

    # HALAMAN ISI STOK
    elif halaman == 'Isi Stok':
        st.title(":material/warehouse:  Pengisian/Pengurangan Stok Kol")
        stok_sekarang = load_stok()
        st.markdown(f" **Stok Saat Ini:** {stok_sekarang} Kg")

        tanggal_stok = st.date_input("Tanggal", value=datetime.today())
        mode = st.radio("Pilih Aksi", ["Tambah Stok", "Kurangi Stok"], horizontal=True)
        jumlah = st.number_input("Jumlah (Kg)", 0)
        keterangan = st.text_input("Keterangan (opsional)")

        if st.button(":material/save: Simpan"):
            if jumlah <= 0:
                st.warning("⚠️ Masukkan jumlah yang lebih dari 0.")
            else:
                if mode == "Tambah Stok":
                    stok_baru = stok_sekarang + jumlah
                    aksi = "ditambahkan"
                else:
                    if jumlah > stok_sekarang:
                        st.error("❌ Jumlah pengurangan melebihi stok saat ini!")
                        st.stop()
                    stok_baru = stok_sekarang - jumlah
                    aksi = "dikurangi"

                simpan_stok(stok_baru)

                df_pengisian = load_data(PENGISIAN_STOK_FILE)
                new_entry = pd.DataFrame([{
                    "Tanggal": tanggal_stok,
                    "Aksi": "Tambah" if mode == "Tambah Stok" else "Kurang",
                    "Jumlah (Kg)": jumlah,
                    "Keterangan": keterangan
                }])
                df_pengisian = pd.concat([df_pengisian, new_entry], ignore_index=True)
                simpan_data(df_pengisian, PENGISIAN_STOK_FILE)

                st.success(f"✅ Stok berhasil {aksi} sebanyak {jumlah} Kg. Stok saat ini: {stok_baru} Kg")

        st.subheader(" Riwayat Pengisian/Pengurangan Stok")
        df_pengisian = load_data(PENGISIAN_STOK_FILE)
        if not df_pengisian.empty:
            df_pengisian = df_pengisian.sort_values("Tanggal", ascending=False)
            st.dataframe(df_pengisian)
        else:
            st.info("Belum ada riwayat pengisian atau pengurangan stok.")

    # HALAMAN LAPORAN
    elif halaman == 'Laporan':
        st.title(":material/request_quote: Laporan Keuangan")
        df = load_data(KEUANGAN_FILE)
        if df.empty:
            st.info("Belum ada data keuangan.")
        else:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])
            df = df.sort_values("Tanggal")

            total_debit = df["Debit"].sum()
            total_kredit = df["Kredit"].sum()

            total_row = pd.DataFrame([{
                "Tanggal": "",
                "Keterangan": " Total  ",
                "Debit": total_debit,
                "Kredit": total_kredit
            }])
            df_final = pd.concat([df, total_row], ignore_index=True)

            df_final["Tanggal"] = pd.to_datetime(df_final["Tanggal"], errors='coerce')
            df_final["Tanggal"] = df_final["Tanggal"].apply(lambda x: f"{x.day} {x.strftime('%B')}" if pd.notnull(x) else "")
            df_final["Debit"] = df_final["Debit"].apply(lambda x: f"{x:,.0f}" if x != 0 else "")
            df_final["Kredit"] = df_final["Kredit"].apply(lambda x: f"{x:,.0f}" if x != 0 else "")

            st.dataframe(df_final[["Tanggal", "Keterangan", "Debit", "Kredit"]], use_container_width=True)

            saldo = total_debit - total_kredit
            st.markdown(f"""
            -  **Total Pemasukan (Debit):** Rp {total_debit:,.0f}  
            -  **Total Pengeluaran (Kredit):** Rp {total_kredit:,.0f}  
            -  **Saldo Akhir:** Rp {saldo:,.0f}
            """)

            if st.button("🗑 Hapus Semua Data"):
                pd.DataFrame().to_csv(KEUANGAN_FILE)
                pd.DataFrame().to_csv(PRODUKSI_FILE)
                pd.DataFrame().to_csv(PENJUALAN_FILE)
                pd.DataFrame().to_csv(PENGISIAN_STOK_FILE)
                pd.DataFrame([{"Stok": 1000}]).to_csv(STOK_FILE, index=False)
                st.warning("Semua data dihapus dan stok direset ke 1000 Kg.")
