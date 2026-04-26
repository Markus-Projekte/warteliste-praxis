import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Akut-Termine Warteliste", layout="centered")

# CSS für ein professionelles Design (optional)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Verbindung zu Google Sheets
# WICHTIG: Die Zugangsdaten kommen später in die Streamlit Cloud "Secrets"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION ---
page = st.sidebar.selectbox("Menü", ["Anmeldung für Patienten", "Interne Ansicht"])

if page == "Anmeldung für Patienten":
    st.title("🏥 Warteliste Osteopathie")
    st.write("Bitte tragen Sie sich hier ein, wenn Sie einen akuten Termin benötigen. Ich melde mich bei Ihnen, sobald eine Lücke frei wird.")
    
    with st.form("patient_form", clear_on_submit=True):
        name = st.text_input("Name (Vor- und Nachname)*")
        phone = st.text_input("Telefonnummer (für Rückruf)*")
        availability = st.text_area("Wann passen Termine bei Ihnen am besten? (z.B. Mo-Do ab 15 Uhr)")
        reason = st.text_input("Kurzer Grund (z.B. akute Blockade)")
        
        st.caption("* Pflichtfelder")
        submitted = st.form_submit_button("Auf Warteliste setzen")
        
        if submitted:
            if name and phone:
                try:
                    # Daten aus dem Sheet lesen
                    df_existing = conn.read(worksheet="Daten")
                    
                    # Neuen Eintrag erstellen
                    new_data = pd.DataFrame([{
                        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "Name": name,
                        "Telefon": phone,
                        "Verfügbarkeit": availability,
                        "Grund": reason,
                        "Status": "Offen"
                    }])
                    
                    # Zusammenfügen und hochladen
                    updated_df = pd.concat([df_existing, new_data], ignore_index=True)
                    conn.update(worksheet="Daten", data=updated_df)
                    
                    st.success(f"Vielen Dank, {name}! Sie wurden erfolgreich eingetragen.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
            else:
                st.warning("Bitte füllen Sie Name und Telefonnummer aus.")

elif page == "Interne Ansicht":
    st.title("📂 Interne Warteliste")
    
    # Simpler Passwortschutz
    password = st.text_input("Passwort eingeben", type="password")
    if password == "MeinPraxisPasswort2024": # Ändere dieses Passwort!
        try:
            df = conn.read(worksheet="Daten")
            
            if not df.empty:
                st.dataframe(df.sort_values(by="Zeitstempel", ascending=False))
                
                st.info("Sie können die Daten auch direkt in Ihrer Google Tabelle bearbeiten oder löschen.")
                st.link_button("Zur Google Tabelle", "HIER_DEINE_TABELLEN_URL_EINFÜGEN")
            else:
                st.write("Aktuell keine Einträge vorhanden.")
        except:
            st.write("Tabelle konnte nicht geladen werden. Prüfen Sie die Verbindung.")
