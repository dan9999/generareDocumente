import streamlit as st

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