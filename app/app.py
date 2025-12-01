import streamlit as st
from buletin_easyocr import BuletinExtractor

# Inițializare extractor OCR
if "extractor" not in st.session_state:
    st.session_state.extractor = BuletinExtractor()

# Inițializare stare selecție
if "tip_act_selectat" not in st.session_state:
    st.session_state.tip_act_selectat = None

# Setare pagină
st.set_page_config(
    page_title="Generator Acte Notariale cu AI",
    page_icon="🏛️",
    layout="wide"
)


# Funcție pentru resetare la Home
def reset_home():
    st.session_state.tip_act_selectat = None


# ================= HEADER =================
# Titlu cu tip act selectat
if st.session_state.tip_act_selectat:
    col_icon, col_title = st.columns([0.5, 9.5])
    with col_icon:
        st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
        if st.button("🏛️", help="Înapoi la meniu principal"):
            reset_home()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col_title:
        st.markdown(
            f"<h1 style='margin-top:-10px;'>Generator Acte Notariale cu AI - {st.session_state.tip_act_selectat}</h1>",
            unsafe_allow_html=True)
else:
    st.markdown("<h1 style='margin-top:-40px;'>🏛️ Generator Acte Notariale cu AI</h1>", unsafe_allow_html=True)

st.markdown("---")

# ================= HOME PAGE (butoane radio neselectate) =================
if st.session_state.tip_act_selectat is None:
    # Butoane radio pentru selecție
    tip_act = st.radio(
        "Selectează tipul actului:",
        ["Declarație acord călătorie minor", "Contract vânzare-cumpărare", "Procura", "Donatie"],
        index=None,  # Nici unul selectat implicit
        horizontal=True
    )

    # Actualizare stare când se selectează
    if tip_act:
        st.session_state.tip_act_selectat = tip_act
        st.rerun()
# ================= FORMULARUL =================
elif st.session_state.tip_act_selectat == "Declarație acord călătorie minor":
    col_left, col_right = st.columns([3, 1])

    # ==========================================================
    #                          STÂNGA
    # ==========================================================
    with col_left:
            st.subheader("🌍 Date persoane")

            # Rând cu 4 coloane
            c1, c2, c3, c4 = st.columns(4)

            # ========== MINOR ==========
            with c1:
                nume_minor = st.text_input("Nume minor:", value="Maria Popescu")

                uploaded_minor = st.file_uploader("Încarcă buletin minor", type=["jpg", "jpeg", "png"], key="upload_minor")

                if uploaded_minor and st.button("📄 Adaugă buletin minor", key="btn_minor"):
                    import tempfile
                    with st.spinner("Se procesează buletinul minorului..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(uploaded_minor.read())
                            cale_temp = tmp.name

                        date_minor = st.session_state.extractor.proceseaza_buletin(cale_temp)

                        if date_minor.get("nume") and date_minor.get("prenume"):
                            st.session_state["nume_minor"] = f"{date_minor['nume']} {date_minor['prenume']}"

                        st.session_state["date_minor_text"] = "\n".join([
                            f"Nume: {date_minor.get('nume','')}",
                            f"Prenume: {date_minor.get('prenume','')}",
                            f"CNP: {date_minor.get('cnp','')}",
                            f"Data naștere: {date_minor.get('data_nastere','')}",
                            f"Loc naștere: {date_minor.get('loc_nastere','')}",
                            f"Domiciliu: {date_minor.get('domiciliu','')}",
                            f"Serie/Număr: {date_minor.get('serie_numar','')}",
                            f"Emisă de: {date_minor.get('emisa','')}",
                            f"La data: {date_minor.get('ladata','')}",
                        ])

                if "date_minor_text" in st.session_state:
                    st.text_area("📋 Date extrase", st.session_state["date_minor_text"], height=200, key="text_minor")

            # ========== TATĂ ==========
            with c2:
                nume_tata = st.text_input("Nume tată:", value="Ion Popescu")

                uploaded_tata = st.file_uploader("Încarcă buletin tată", type=["jpg", "jpeg", "png"], key="upload_tata")

                if uploaded_tata and st.button("📄 Adaugă buletin tată", key="btn_tata"):
                    import tempfile
                    with st.spinner("Se procesează buletinul tatălui..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(uploaded_tata.read())
                            cale_temp = tmp.name

                        date_tata = st.session_state.extractor.proceseaza_buletin(cale_temp)

                        if date_tata.get("nume") and date_tata.get("prenume"):
                            st.session_state["nume_tata"] = f"{date_tata['nume']} {date_tata['prenume']}"

                        st.session_state["date_tata_text"] = "\n".join([
                            f"Nume: {date_tata.get('nume','')}",
                            f"Prenume: {date_tata.get('prenume','')}",
                            f"CNP: {date_tata.get('cnp','')}",
                            f"Data naștere: {date_tata.get('data_nastere','')}",
                            f"Loc naștere: {date_tata.get('loc_nastere','')}",
                            f"Domiciliu: {date_tata.get('domiciliu','')}",
                            f"Serie/Număr: {date_tata.get('serie_numar','')}",
                            f"Emisă de: {date_tata.get('emisa','')}",
                            f"La data: {date_tata.get('ladata','')}",
                        ])

                if "date_tata_text" in st.session_state:
                    st.text_area("📋 Date extrase", st.session_state["date_tata_text"], height=200, key="text_tata")

            # ========== MAMĂ ==========
            with c3:
                nume_mama = st.text_input("Nume mamă:", value="Elena Popescu")

                uploaded_mama = st.file_uploader("Încarcă buletin mamă", type=["jpg", "jpeg", "png"], key="upload_mama")

                if uploaded_mama and st.button("📄 Adaugă buletin mamă", key="btn_mama"):
                    import tempfile
                    with st.spinner("Se procesează buletinul mamei..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(uploaded_mama.read())
                            cale_temp = tmp.name

                        date_mama = st.session_state.extractor.proceseaza_buletin(cale_temp)

                        if date_mama.get("nume") and date_mama.get("prenume"):
                            st.session_state["nume_mama"] = f"{date_mama['nume']} {date_mama['prenume']}"

                        st.session_state["date_mama_text"] = "\n".join([
                            f"Nume: {date_mama.get('nume','')}",
                            f"Prenume: {date_mama.get('prenume','')}",
                            f"CNP: {date_mama.get('cnp','')}",
                            f"Data naștere: {date_mama.get('data_nastere','')}",
                            f"Loc naștere: {date_mama.get('loc_nastere','')}",
                            f"Domiciliu: {date_mama.get('domiciliu','')}",
                            f"Serie/Număr: {date_mama.get('serie_numar','')}",
                            f"Emisă de: {date_mama.get('emisa','')}",
                            f"La data: {date_mama.get('ladata','')}",
                        ])

                if "date_mama_text" in st.session_state:
                    st.text_area("📋 Date extrase", st.session_state["date_mama_text"], height=200, key="text_mama")

            # ========== ÎNSOȚITOR ==========
            with c4:
                insotitor = st.text_input("Însoțitor:", value="Elena Popescu")

                uploaded_insotitor = st.file_uploader("Încarcă buletin însoțitor", type=["jpg", "jpeg", "png"], key="upload_insotitor")

                if uploaded_insotitor and st.button("📄 Adaugă buletin însoțitor", key="btn_insotitor"):
                    import tempfile
                    with st.spinner("Se procesează buletinul însoțitorului..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(uploaded_insotitor.read())
                            cale_temp = tmp.name

                        date_insotitor = st.session_state.extractor.proceseaza_buletin(cale_temp)

                        if date_insotitor.get("nume") and date_insotitor.get("prenume"):
                            st.session_state["insotitor"] = f"{date_insotitor['nume']} {date_insotitor['prenume']}"

                        st.session_state["date_insotitor_text"] = "\n".join([
                            f"Nume: {date_insotitor.get('nume','')}",
                            f"Prenume: {date_insotitor.get('prenume','')}",
                            f"CNP: {date_insotitor.get('cnp','')}",
                            f"Data naștere: {date_insotitor.get('data_nastere','')}",
                            f"Loc naștere: {date_insotitor.get('loc_nastere','')}",
                            f"Domiciliu: {date_insotitor.get('domiciliu','')}",
                            f"Serie/Număr: {date_insotitor.get('serie_numar','')}",
                            f"Emisă de: {date_insotitor.get('emisa','')}",
                            f"La data: {date_insotitor.get('ladata','')}",
                        ])

                if "date_insotitor_text" in st.session_state:
                    st.text_area("📋 Date extrase", st.session_state["date_insotitor_text"], height=200, key="text_insotitor")

            # Buton generare
            st.markdown("---")
            if st.button("🚀 Generează declarația", type="primary"):
                st.success("Declarația se generează...")



    # ==========================================================
    #                          DREAPTA (Context)
    # ==========================================================
    with col_right:

        st.header("📋 Context")
        st.markdown("---")

        destinatie = st.text_input("Destinația:", value="Italia")
        perioada = st.text_input("Perioada:", value="01-15 August 2024")

        if st.button("➕ Adaugă câmp nou (context)"):
            st.info("Funcționalitate în dezvoltare")

        st.markdown("---")

        # Afișăm contextul efectiv
        st.write(f"**Destinația:** {destinatie}")
        st.write(f"**Perioada:** {perioada}")
        st.write(f"**Nume minor:** {nume_minor}")
        st.write(f"**Nume tată:** {nume_tata}")
        st.write(f"**Nume mamă:** {nume_mama}")
        st.write(f"**Însoțitor:** {insotitor}")

# ================= ALTE ACTE (mesaj simplu) =================
else:
    st.info(f"Formularul pentru '{st.session_state.tip_act_selectat}' este în curs de dezvoltare.")
    st.write("Această funcționalitate va fi disponibilă în curând.")

st.markdown("---")
st.caption("Generator Acte Notariale v1.0")