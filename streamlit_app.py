import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Warteliste Osteopathie", layout="centered")

# Verbindung zu Google Sheets herstellen
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION IN DER SEITENLEISTE ---
page = st.sidebar.radio("Navigation", ["Patienten-Anmeldung", "Interne Warteliste"])

# --- SEITE 1: PATIENTEN-ANMELDUNG ---
if page == "Patienten-Anmeldung":
    st.header("🏥 Akut-Warteliste")
    st.write("Bitte tragen Sie sich hier ein. Ich melde mich bei Ihnen, sobald eine Lücke frei wird.")
    
    with st.form("warteliste_form", clear_on_submit=True):
        name = st.text_input("Name*")
        phone = st.text_input("Telefonnummer*")
        availability = st.text_area("Wann passen Termine? (z.B. Mo-Do ab 15 Uhr)")
        reason = st.text_input("Kurzer Grund (z.B. akute Schmerzen)")
        
        st.caption("* Pflichtfelder")
        submitted = st.form_submit_button("Auf Warteliste setzen")
        
        if submitted:
            if name and phone:
                # Bestehende Daten aus dem Google Sheet lesen
                # Falls das Sheet leer ist, erstellen wir eine leere Tabelle mit Spalten
                try:
                    existing_data = conn.read(worksheet="Daten", ttl=0)
                except:
                    existing_data = pd.DataFrame(columns=["Zeitstempel", "Name", "Telefon", "Verfügbarkeit", "Grund", "Status"])

                # Neuen Eintrag erstellen
                new_entry = pd.DataFrame([{
                    "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "Name": name,
                    "Telefon": phone,
                    "Verfügbarkeit": availability,
                    "Grund": reason,
                    "Status": "Offen"
                }])
                
                # Daten zusammenführen
                updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                
                # Zurück in Google Sheets schreiben
                conn.update(worksheet="Daten", data=updated_df)
                
                st.success(f"Vielen Dank, {name}. Sie sind auf der Liste!")
                st.balloons()
            else:
                st.error("Bitte mindestens Name und Telefonnummer angeben.")

# --- SEITE 2: INTERNE WARTELISTE ---
elif page == "Interne Warteliste":
    st.header("📂 Aktuelle Akut-Anfragen")
    
    # Passwortschutz für den internen Bereich
    password = st.text_input("Admin-Passwort", type="password")
    if password == "Nuessle3": # <-- ÄNDERE DIESES PASSWORT!
        try:
            df = conn.read(worksheet="Daten", ttl=0)
            if not df.empty:
                st.dataframe(df)
                st.info("Sie können Einträge direkt in Ihrer Google Tabelle löschen oder bearbeiten.")
            else:
                st.write("Die Liste ist aktuell leer.")
        except:
            st.warning("Keine Daten gefunden. Haben Sie das Tabellenblatt in Google Sheets 'Daten' genannt?")
