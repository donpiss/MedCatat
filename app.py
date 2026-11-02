from datetime import datetime
import pandas as pd
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Clinic Management System", layout="centered", page_icon="🩺", initial_sidebar_state="auto"
)

# Custom CSS untuk tampilan lebih profesional, minimalis, dan clean
st.markdown(
    """
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            border-radius: 6px;
            font-weight: 500;
        }
        div.stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #eef0f2;
        }
        
        footer {visibility: hidden;}
        
        /* Pengaturan padding khusus layar HP */
        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            /* Membuat tombol di sidebar memenuhi lebar layar HP */
            .stButton>button {
                width: 100%;
            }
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Inisialisasi data pasien dan janji temu di session_state
if "patients" not in st.session_state:
    st.session_state["patients"] = []

if "appointments" not in st.session_state:
    st.session_state["appointments"] = []

if "selected_patient" not in st.session_state:
    st.session_state["selected_patient"] = None

if "menu" not in st.session_state:
    st.session_state["menu"] = "🏠 Dashboard"


# Fungsi untuk navigasi otomatis ke detail pasien
def show_patient_details(patient_name):
    st.session_state["menu"] = "📋 View Patients"
    st.session_state["selected_patient"] = patient_name
    st.rerun()


# Sidebar Navigasi
st.sidebar.title("🩺 MedCatat")
st.sidebar.markdown("---")

menu_options = [
    "🏠 Dashboard",
    "➕ Add Patient",
    "📋 View Patients",
    "📅 Schedule Appointment",
]

# Sinkronisasi menu dengan session_state agar bisa dipindah secara programatik
selected_menu = st.sidebar.radio(
    "Navigasi", menu_options, index=menu_options.index(st.session_state["menu"])
)
st.session_state["menu"] = selected_menu
menu = st.session_state["menu"]

st.sidebar.markdown("---")
st.sidebar.info(
    "Sistem Manajemen Klinik Sederhana\nVersi 1.0 - Clean & Minimalist"
)

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard")
    st.markdown("Ringkasan aktivitas dan jadwal kunjungan klinik hari ini.")
    st.markdown("")

    # Statistik utama (Metrik Cards)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Pasien", value=len(st.session_state["patients"]))
    with col2:
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_count = len(
            [
                appt
                for appt in st.session_state["appointments"]
                if appt["Date"] == today_str
            ]
        )
        st.metric(label="Janji Temu Hari Ini", value=today_count)
    with col3:
        st.metric(
            label="Total Janji Temu",
            value=len(st.session_state["appointments"]),
        )

    st.markdown("---")
    st.subheader("📌 Jadwal Kunjungan Terdekat")

    if st.session_state["appointments"]:
        df_appointments = pd.DataFrame(st.session_state["appointments"])

        # Konversi kolom Date dan Time ke tipe datetime untuk diurutkan
        try:
            df_appointments["Datetime"] = pd.to_datetime(
                df_appointments["Date"] + " " + df_appointments["Time"],
                errors="coerce",
            )
            # Urutkan dari yang paling dekat dengan waktu sekarang
            df_appointments = df_appointments.sort_values(by="Datetime")
        except Exception:
            pass

        if not df_appointments.empty:
            for i, row in df_appointments.iterrows():
                with st.container():
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(
                            f"**{row['Patient']}**<br><span style='color:gray; font-size:14px;'>📅 {row['Date']} | ⏰ {row['Time']} | 📝 {row['Reason']}</span>",
                            unsafe_allow_html=True,
                        )
                    with col_btn:
                        if st.button("Lihat Pasien", key=f"view_dash_{i}"):
                            show_patient_details(row["Patient"])
                    st.divider()
        else:
            st.info("Tidak ada jadwal kunjungan terdekat.")
    else:
        st.info("Belum ada jadwal janji temu yang tercatat.")

# ----------------------------------------------------
# 2. TAMBAH PASIEN
# ----------------------------------------------------
elif menu == "➕ Add Patient":
    st.title("➕ Tambah Pasien Baru")
    st.markdown("Masukkan informasi lengkap pasien pada form di bawah ini.")
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nama Lengkap*")

        # Input Tanggal Lahir (Tanpa input umur manual/otomatis)
        tgl_lahir = st.date_input(
            "Tanggal Lahir",
            value=datetime(1995, 1, 1),
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            key="input_tgl_lahir",
        )

        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        blood_type = st.selectbox(
            "Golongan Darah", ["A", "B", "AB", "O", "Tidak Tahu"])

    with col2:
        contact = st.text_input("Nomor Kontak / WhatsApp")
        allergies = st.text_area(
            "Riwayat Alergi (Obat/Makanan)",
            placeholder="Contoh: Alergi antibiotik penisilin, seafood, atau tulis 'Tidak ada'",
        )
        address = st.text_area("Alamat Lengkap")

    st.markdown("")
    submit = st.button("Simpan Data Pasien", type="primary")

    if submit:
        if name.strip() == "":
            st.error("Nama lengkap wajib diisi!")
        else:
            new_patient = {
                "Name": name,
                "Date of Birth": tgl_lahir.strftime("%Y-%m-%d"),
                "Gender": gender,
                "Blood Type": blood_type,
                "Contact": contact,
                "Allergies": allergies if allergies else "Tidak ada",
                "Address": address,
                "Date Added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state["patients"].append(new_patient)
            st.success(f"Pasien atas nama **{name}** berhasil ditambahkan!")

# ----------------------------------------------------
# 3. LIHAT DAFTAR PASIEN & DETAIL
# ----------------------------------------------------
elif menu == "📋 View Patients":
    st.title("📋 Daftar Pasien")
    st.markdown("Kelola dan lihat informasi detail rekam jejak pasien klinik.")
    st.markdown("")

    if st.session_state["patients"]:
        df = pd.DataFrame(st.session_state["patients"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔍 Detail Profil Pasien")

        patient_names = [p["Name"] for p in st.session_state["patients"]]

        default_index = 0
        if st.session_state["selected_patient"] in patient_names:
            default_index = patient_names.index(
                st.session_state["selected_patient"]
            )

        selected_dropdown = st.selectbox(
            "Pilih Pasien untuk Dilihat Detailnya",
            patient_names,
            index=default_index,
        )

        st.session_state["selected_patient"] = selected_dropdown

        if st.session_state["selected_patient"]:
            patient_data = next(
                (
                    p
                    for p in st.session_state["patients"]
                    if p["Name"] == st.session_state["selected_patient"]
                ),
                None,
            )
            if patient_data:
                st.markdown("")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown(f"**Nama Lengkap:** {patient_data['Name']}")
                    st.markdown(
                        f"**Tanggal Lahir:** {patient_data.get('Date of Birth', '-')}"
                    )
                    st.markdown(f"**Jenis Kelamin:** {patient_data['Gender']}")
                with col_d2:
                    st.markdown(f"**Kontak:** {patient_data['Contact'] or '-'}")
                    st.markdown(f"**Alamat:** {patient_data['Address'] or '-'}")
                    st.markdown(
                        f"**Terdaftar Sejak:** {patient_data['Date Added']}"
                    )
    else:
        st.info(
            "Belum ada data pasien terdaftar. Silakan tambahkan melalui menu 'Add Patient'."
        )

# ----------------------------------------------------
# 4. PENJADWALAN JANJI TEMU
# ----------------------------------------------------
elif menu == "📅 Schedule Appointment":
    st.title("📅 Penjadwalan Janji Temu")
    st.markdown(
        "Atur jadwal kunjungan konsultasi atau tindakan pasien dengan dokter."
    )
    st.markdown("")

    if not st.session_state["patients"]:
        st.warning(
            "Belum ada pasien terdaftar. Harap tambahkan pasien terlebih dahulu."
        )
    else:
        with st.form("schedule_appointment_form", clear_on_submit=True):
            patient_name = st.selectbox(
                "Pilih Pasien", [p["Name"] for p in st.session_state["patients"]]
            )
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                date = st.date_input("Tanggal Kunjungan")
            with col_f2:
                time = st.time_input("Jam Kunjungan")

            reason = st.text_area(
                "Keluhan / Alasan Kunjungan",
                placeholder="Contoh: Konsultasi rutin / sakit gigi",
            )

            st.markdown("")
            submit = st.form_submit_button("Buat Jadwal Temu")

            if submit:
                new_appointment = {
                    "Patient": patient_name,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Time": time.strftime("%H:%M"),
                    "Reason": reason if reason else "-",
                }
                st.session_state["appointments"].append(new_appointment)
                st.success(
                    f"Berhasil menjadwalkan temu untuk **{patient_name}** pada tanggal {date} pukul {time.strftime('%H:%M')}."
                )

        st.markdown("---")
        st.subheader("📋 Riwayat Seluruh Janji Temu")
        if st.session_state["appointments"]:
            df_all_appt = pd.DataFrame(st.session_state["appointments"])
            st.dataframe(df_all_appt, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada riwayat janji temu.")
