import streamlit as st
from buletin_easyocr import BuletinExtractor

if "extractor" not in st.session_state:
    st.session_state.extractor = BuletinExtractor()

# Configurare pagină
st.set_page_config(
    page_title="Generator Acte Notariale",
    page_icon="🏛️",
    layout="wide"
)

# Titlu
st.title("🏛️ Generator Acte Notariale cu AI")
st.markdown("---")

# Butoane radio pentru tipurile de acte
tip_act = st.radio(
    "Selectează tipul actului:",
    ["Declarație acord călătorie minor", "Contract vânzare-cumpărare", "Procura", "Donatie"],
    horizontal=True
)

st.markdown("---")

# Layout cu două coloane
col_left, col_right = st.columns([2, 1])

with col_left:
    # Afișează DOAR Declarație acord călătorie minor completă
    if tip_act == "Declarație acord călătorie minor":
        st.header("🌍 Detalii călătorie minor")

        # MAI PUȚINE COLOANE pentru câmpuri mai late
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            destinatie = st.text_input("Destinația:", value="Italia", help="Apasă Enter pentru a aplica")
        with col2:
            perioada = st.text_input("Perioada:", value="01-15 August 2024", help="Apasă Enter pentru a aplica")
        with col3:
            insotitor = st.text_input("Însoțitor:", value="Elena Popescu", help="Apasă Enter pentru a aplica")
        with col4:
            nume_minor = st.text_input("Nume minor:", value="Maria Popescu", help="Apasă Enter pentru a aplica")
        with col5:
            nume_tata = st.text_input("Nume tată:", value="Ion Popescu", help="Apasă Enter pentru a aplica")

            # === Upload + OCR Buletin Tată ===
            uploaded_tata = st.file_uploader("Încarcă buletin tată (jpg/png)",
                                             type=["jpg", "jpeg", "png"],
                                             key="upload_tata")

            if uploaded_tata and st.button("📄 Adaugă buletin tată"):
                import tempfile

                with st.spinner("Se procesează buletinul tatălui..."):

                    # Salvăm temporar imaginea încărcată
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(uploaded_tata.read())
                        cale_temp = tmp.name

                    # Extragem datele

                    date_tata = st.session_state.extractor.proceseaza_buletin(cale_temp)

                    # Actualizăm numele tatălui dacă găsim nume + prenume
                    if date_tata.get("nume") and date_tata.get("prenume"):
                        nume_tata = f"{date_tata['nume']} {date_tata['prenume']}"
                        st.session_state["nume_tata"] = nume_tata

                    # Stocăm textul complet în textarea
                    st.session_state["date_tata_text"] = "\n".join([
                        f"Nume: {date_tata.get('nume', '')}",
                        f"Prenume: {date_tata.get('prenume', '')}",
                        f"CNP: {date_tata.get('cnp', '')}",
                        f"Data naștere: {date_tata.get('data_nastere', '')}",
                        f"Loc naștere: {date_tata.get('loc_nastere', '')}",
                        f"Domiciliu: {date_tata.get('domiciliu', '')}",
                        f"Serie/Număr: {date_tata.get('serie_numar', '')}",
                        f"Emisă de: {date_tata.get('emisa', '')}",
                        f"La data: {date_tata.get('ladata', '')}",
                    ])

            # Afișăm textarea cu datele extrase
            if "date_tata_text" in st.session_state:
                st.text_area("📋 Date extrase din buletin tată:",
                             st.session_state["date_tata_text"],
                             height=220)
        with col6:
            nume_mama = st.text_input("Nume mamă:", value="Elena Popescu", help="Apasă Enter pentru a aplica")

        # Buton pentru adăugare câmpuri noi
        if st.button("➕ Adaugă câmp nou"):
            st.info("Aici vom adăuga funcționalitatea pentru câmpuri noi")

        # Buton pentru generare
        if st.button("🚀 Generează declarația", type="primary"):
            st.success("Declarația se generează...")

    else:
        # Pentru celelalte acte, doar mesaj simplu
        st.header(f"{tip_act}")
        st.info("În dezvoltare - vom implementa în curând!")

with col_right:
    st.header("📋 Context")
    st.markdown("---")

    # Afișează contextul DOAR pentru Declarație
    if tip_act == "Declarație acord călătorie minor":
        st.write(f"**Destinația:** {destinatie}")
        st.write(f"**Perioada:** {perioada}")
        st.write(f"**Însoțitor:** {insotitor}")
        st.write(f"**Nume minor:** {nume_minor}")
        st.write(f"**Nume tată:** {nume_tata}")
        st.write(f"**Nume mamă:** {nume_mama}")
    else:
        st.write("Selectează 'Declarație acord călătorie minor' pentru a vedea contextul")

    st.markdown("---")
    st.info("ℹ️ Modifică un câmp și apasă Enter pentru a aplica")

st.markdown("---")
st.caption("Generator Acte Notariale v1.0")