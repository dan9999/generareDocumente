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

            with c1:
                nume_minor = st.text_input("Nume minor:", value="Maria Popescu")

            with c2:
                nume_tata = st.text_input("Nume tată:", value="Ion Popescu")

                uploaded_tata = st.file_uploader("Încarcă buletin tată", type=["jpg", "jpeg", "png"])

                if uploaded_tata and st.button("📄 Adaugă buletin tată"):
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
                    st.text_area("📋 Date extrase", st.session_state["date_tata_text"], height=200)

            with c3:
                nume_mama = st.text_input("Nume mamă:", value="Elena Popescu")

            with c4:
                insotitor = st.text_input("Însoțitor:", value="Elena Popescu")

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
