import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import os
import re
import subprocess

st.set_page_config(page_title="Formulir Pendaftaran Peristiwa Kependudukan")

# --- Logo dan Judul ---
col1, col2 = st.columns([1, 6])  # Adjust ratio kalau mau

with col1:
    st.image("logo_kabupaten_malang.png", width=80)  # Sesuaikan path & size

with col2:
    st.title("FORMULIR PENDAFTARAN PERISTIWA KEPENDUDUKAN")

# Mapping nama bulan ke Indonesia
BULAN_ID = {
    "January": "Januari",
    "February": "Februari",
    "March": "Maret",
    "April": "April",
    "May": "Mei",
    "June": "Juni",
    "July": "Juli",
    "August": "Agustus",
    "September": "September",
    "October": "Oktober",
    "November": "November",
    "December": "Desember"
}

# --- Mandatory input ---
def style_if_empty(value):
    return "**WAJIB DIISI!**" if not value else ""

nama = st.text_input("Nama Lengkap", placeholder=style_if_empty(""))
nik = st.text_input("NIK", placeholder=style_if_empty(""))
kk = st.text_input("Nomor Kartu Keluarga", placeholder=style_if_empty(""))
# --- Tanggal Permohonan ---
tanggal_permohonan = st.date_input(
    "Tanggal Permohonan",
    value=datetime.today()
)


jenis_permohonan = st.selectbox(
    "Pilih Jenis Permohonan",
    ["-", "Kartu Keluarga", "KTP-el", "Kartu Identitas Anak", "Perubahan Data"]
)

sub_jenis = None
sub_value = None

if jenis_permohonan == "KTP-el":
    sub_jenis = st.selectbox(
        "Sub Jenis KTP-el",
        ["-", "A. BARU", "B. PINDAH DATANG", "C. HILANG/RUSAK",
         "D. PERPANJANGAN ITAP", "E. PERUBAHAN STATUS KEWARGANEGARAAN",
         "F. LUAR DOMISILI", "G. TRANSMIGRASI"]
    )
    if sub_jenis == "C. HILANG/RUSAK":
        sub_value = st.selectbox("Detail KTP-el:", ["-", "1. HILANG", "2. RUSAK"])

elif jenis_permohonan == "Kartu Keluarga":
    sub_jenis = st.selectbox(
        "Sub Jenis Kartu Keluarga",
        ["-", "A. BARU", "B. PERUBAHAN DATA", "C. HILANG/RUSAK"]
    )
    if sub_jenis == "A. BARU":
        sub_value = st.selectbox("Detail A. BARU:", [
            "-", "1. Membentuk Keluarga Baru", "2. Penggantian Kepala Keluarga",
            "3. Pisah KK", "4. Pindah Datang", "5. WNI dan LN karena Pindah",
            "6. Rentan Adminduk"
        ])
    elif sub_jenis == "B. PERUBAHAN DATA":
        sub_value = st.selectbox("Detail B. PERUBAHAN DATA:", [
            "-", "1. Menumpang Dalam KK", "2. Peristiwa Penting",
            "3. Perubahan Elemen data yang Tercantum dalam KK"
        ])
    elif sub_jenis == "C. HILANG/RUSAK":
        sub_value = st.selectbox("Detail C. HILANG/RUSAK:", ["-", "1. Hilang", "2. Rusak"])

elif jenis_permohonan == "Kartu Identitas Anak":
    sub_jenis = st.selectbox(
        "Sub Jenis KIA",
        ["-", "A. BARU", "B. HILANG/RUSAK", "C. Perpanjangan ITAP", "D. Lainnya"]
    )
    if sub_jenis == "B. HILANG/RUSAK":
        sub_value = st.selectbox("Detail B. HILANG/RUSAK:", ["-", "1. Hilang", "2. Rusak"])

elif jenis_permohonan == "Perubahan Data":
    sub_jenis = st.selectbox(
        "Sub Jenis Perubahan Data",
        ["-", "A. KK", "B. KTP-el", "C. KIA"]
    )


# --- Persyaratan ---
persyaratan_list = [
    "KK Lama / KK Rusak", "Buku nikah / kutipan akta perkawinan", "Kutipan Akta Perceraian", "Surat Keterangan Pindah",
    "Surat Keterangan Pindah Luar Negeri", "KTP-El Lama/Rusak", "Dokumen Perjalanan", "Surat Keterangan Hilang dari Kepolisian",
    "Surat keterangan / bukti perubahan Peristiwa Kependudukan dan Peristiwa Penting", "SPTJM Perkawinan/perceraian belum tercatat",
    "Akta Kematian", "Surat pernyataan penyebab terjadinya hilang atau rusak", "Surat Keterangan Pindah dari Perwakilan RI",
    "Surat pernyataan bersedia menerima sebagai anggota keluarga", "Surat Kuasa Pengasuhan Anak dari Orang Tua/Wali", "Kartu Izin Tinggal Tetap"
]

persyaratan = st.multiselect("Persyaratan yang Dilampirkan (Minimal 1)", persyaratan_list)

# --- Validasi semua wajib ---
error_messages = []

if st.button("Buat & Unduh Surat Pengantar (PDF)"):
    if not nama:
        error_messages.append("❗ Nama wajib diisi")
    if not nik:
        error_messages.append("❗ NIK wajib diisi")
    if not kk:
        error_messages.append("❗ Nomor KK wajib diisi")
    if not tanggal_permohonan:
        error_messages.append("❗ Tanggal Permohonan wajib diisi")
    if jenis_permohonan == "-" or not jenis_permohonan:
        error_messages.append("❗ Jenis Permohonan wajib dipilih")
    if jenis_permohonan == "KTP-el" and (not sub_jenis or sub_jenis == "-"):
        error_messages.append("❗ Sub Jenis KTP-el wajib dipilih")
    if jenis_permohonan == "Kartu Keluarga" and (not sub_jenis or sub_jenis == "-"):
        error_messages.append("❗ Sub Jenis Kartu Keluarga wajib dipilih")
    if sub_jenis and "HILANG/RUSAK" in sub_jenis and (not sub_value or sub_value == "-"):
        error_messages.append("❗ Detail HILANG/RUSAK wajib dipilih")
    if not persyaratan:
        error_messages.append("❗ Persyaratan wajib dipilih minimal 1")

    if error_messages:
        for msg in error_messages:
            st.warning(msg)
    else:
        doc = DocxTemplate("FORM F-1.02.docx")

        bulan_eng = tanggal_permohonan.strftime("%B")
        bulan_id = BULAN_ID.get(bulan_eng, bulan_eng)
        tanggal_permohonan_str = tanggal_permohonan.strftime(f"%d {bulan_id} ")

        # --- Context lengkap: persyaratan + permohonan + sub ---
        context = {
    'nama': nama,
    'nik': nik,
    'kk': kk,
    'jenis_permohonan': jenis_permohonan,
    'sub_jenis': sub_jenis or "",
    'sub_value': sub_value or "",
    'tanggal': tanggal_permohonan_str,

    # Centang Persyaratan
    'P1': "✓" if "KK Lama / KK Rusak" in persyaratan else "",
    'P2': "✓" if "Buku nikah / kutipan akta perkawinan" in persyaratan else "",
    'P3': "✓" if "Kutipan Akta Perceraian" in persyaratan else "",
    'P4': "✓" if "Surat Keterangan Pindah" in persyaratan else "",
    'P5': "✓" if "Surat Keterangan Pindah Luar Negeri" in persyaratan else "",
    'P6': "✓" if "KTP-El Lama/Rusak" in persyaratan else "",
    'P7': "✓" if "Dokumen Perjalanan" in persyaratan else "",
    'P8': "✓" if "Surat Keterangan Hilang dari Kepolisian" in persyaratan else "",
    'P9': "✓" if "Surat keterangan / bukti perubahan Peristiwa Kependudukan dan Peristiwa Penting" in persyaratan else "",
    'P10': "✓" if "SPTJM Perkawinan/perceraian belum tercatat" in persyaratan else "",
    'P11': "✓" if "Akta Kematian" in persyaratan else "",
    'P12': "✓" if "Surat pernyataan penyebab terjadinya hilang atau rusak" in persyaratan else "",
    'P13': "✓" if "Surat Keterangan Pindah dari Perwakilan RI" in persyaratan else "",
    'P14': "✓" if "Surat pernyataan bersedia menerima sebagai anggota keluarga" in persyaratan else "",
    'P15': "✓" if "Surat Kuasa Pengasuhan Anak dari Orang Tua/Wali" in persyaratan else "",
    'P16': "✓" if "Kartu Izin Tinggal Tetap" in persyaratan else "",

    # Centang Jenis Permohonan
    'J1': "✓" if jenis_permohonan == "Kartu Keluarga" else "",
    'J2': "✓" if jenis_permohonan == "KTP-el" else "",
    'J3': "✓" if jenis_permohonan == "Kartu Identitas Anak" else "",
    'J4': "✓" if jenis_permohonan == "Perubahan Data" else "",

    # SUB KTP-el (A-G)
    'J2A': "✓" if jenis_permohonan == "KTP-el" and sub_jenis == "A. BARU" else "",
    'J2B': "✓" if jenis_permohonan == "KTP-el" and sub_jenis == "B. PINDAH DATANG" else "",
    'J2C': "✓" if jenis_permohonan == "KTP-el" and sub_jenis == "C. HILANG/RUSAK" else "",
    'J2D': "✓" if jenis_permohonan == "KTP-el" and sub_jenis == "D. PERPANJANGAN ITAP" else "",
    'J2E': "✓" if jenis_permohonan == "KTP-el" and sub_jenis == "E. PERUBAHAN STATUS KEWARGANEGARAAN" else "",
    'J2F': "✓" if jenis_permohonan == "KTP-el" and sub_jenis == "F. LUAR DOMISILI" else "",
    'J2G': "✓" if jenis_permohonan == "KTP-el" and sub_jenis == "G. TRANSMIGRASI" else "",

    # Detail HILANG/RUSAK KTP-el
    'J2C1': "✓" if jenis_permohonan == "KTP-el" and sub_value and "1. Hilang" in sub_value else "",
    'J2C2': "✓" if jenis_permohonan == "KTP-el" and sub_value and "2. Rusak" in sub_value else "",

    # SUB Kartu Keluarga (A-C)
    'J1A': "✓" if jenis_permohonan == "Kartu Keluarga" and sub_jenis == "A. BARU" else "",
    'J1B': "✓" if jenis_permohonan == "Kartu Keluarga" and sub_jenis == "B. PERUBAHAN DATA" else "",
    'J1C': "✓" if jenis_permohonan == "Kartu Keluarga" and sub_jenis == "C. HILANG/RUSAK" else "",

    # Detail Kartu Keluarga - A. BARU
    'J1A1': "✓" if sub_value == "1. Membentuk Keluarga Baru" else "",
    'J1A2': "✓" if sub_value == "2. Penggantian Kepala Keluarga" else "",
    'J1A3': "✓" if sub_value == "3. Pisah KK" else "",
    'J1A4': "✓" if sub_value == "4. Pindah Datang" else "",
    'J1A5': "✓" if sub_value == "5. WNI dan LN karena Pindah" else "",
    'J1A6': "✓" if sub_value == "6. Rentan Adminduk" else "",

    # Detail Kartu Keluarga - B. PERUBAHAN DATA
    'J1B1': "✓" if sub_value == "1. Menumpang Dalam KK" else "",
    'J1B2': "✓" if sub_value == "2. Peristiwa Penting" else "",
    'J1B3': "✓" if sub_value == "3. Perubahan Elemen data yang Tercantum dalam KK" else "",

    # Detail Kartu Keluarga - C. HILANG/RUSAK
    'J1C1': "✓" if sub_value == "1. Hilang" else "",
    'J1C2': "✓" if sub_value == "2. Rusak" else "",

    # SUB KIA (A-D)
    'J3A': "✓" if jenis_permohonan == "Kartu Identitas Anak" and sub_jenis == "A. BARU" else "",
    'J3B': "✓" if jenis_permohonan == "Kartu Identitas Anak" and sub_jenis == "B. HILANG/RUSAK" else "",
    'J3C': "✓" if jenis_permohonan == "Kartu Identitas Anak" and sub_jenis == "C. Perpanjangan ITAP" else "",
    'J3D': "✓" if jenis_permohonan == "Kartu Identitas Anak" and sub_jenis == "D. Lainnya" else "",

    # Detail HILANG/RUSAK KIA
    'J3B1': "✓" if jenis_permohonan == "Kartu Identitas Anak" and sub_value and "1. Hilang" in sub_value else "",
    'J3B2': "✓" if jenis_permohonan == "Kartu Identitas Anak" and sub_value and "2. Rusak" in sub_value else "",

    # SUB Perubahan Data (A-C)
    'J4A': "✓" if jenis_permohonan == "Perubahan Data" and sub_jenis == "A. KK" else "",
    'J4B': "✓" if jenis_permohonan == "Perubahan Data" and sub_jenis == "B. KTP-el" else "",
    'J4C': "✓" if jenis_permohonan == "Perubahan Data" and sub_jenis == "C. KIA" else "",
}

        doc.render(context)
        nama_sanitized = re.sub(r'\W+', '_', nama)
        output_docx = f"Surat Pengantar F1.02 {nama_sanitized}.docx"

        doc.save(output_docx)

        subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', '.', output_docx])
        output_pdf = output_docx.replace('.docx', '.pdf')

        with open(output_pdf, "rb") as f:
            st.download_button(
                label="📥 Unduh Surat Pengantar (PDF)",
                data=f,
                file_name=output_pdf,
                mime="application/pdf"
            )

        os.remove(output_docx)
