import streamlit as st
import json

def load_config():
    with open("config.json") as f:
        config = json.load(f)
    st.session_state.config = config

def save_config():
    try:
        with open("config.json", "w") as f: 
            json.dump(st.session_state.config, f)
        st.toast("Saving successful!")
    except:
        st.error("Saving failed!")


def update_config():
    st.session_state.config["brightness"] = st.session_state.bright_slider
    st.session_state.config["app_change_freq"] = st.session_state.app_change_freq
    

if "config" not in st.session_state.keys():
    load_config()

# 1. Seitenkonfiguration (sollte immer der erste Streamlit-Befehl sein)
st.set_page_config(page_title="LED Matrix Controller", page_icon="💡", layout="centered")

with st.sidebar:
    st.header("Settings")
    st.info(st.session_state)

    st.slider("☀️ Brightness", 10, 100, key="bright_slider", value=st.session_state.config["brightness"], on_change=update_config)

    st.number_input("⏱️ App change frequency", min_value=5, max_value=3600, key="app_change_freq", 
                    value=st.session_state.config["app_change_freq"], on_change=update_config)

    st.button("Save Settings", on_click=save_config)

# 2. Titel und Beschreibung
st.title("LED Matrix Controller")
st.markdown("Verwalte die Anzeigen für deine Raspberry Pi LED Matrix.")

# 3. Layout-Struktur mit Tabs für gute Übersichtlichkeit
tab_stocks, tab_weather, tab_settings = st.tabs(["📈 Aktien", "🌤️ Wetter", "⚙️ System"])

# --- TAB 1: AKTIEN ---
with tab_stocks:
    st.header("Aktien-Tracker")
    
    # Platzhalter für Eingaben
    st.text_input("Ticker-Symbole (z.B. AAPL, GOOGL, MSFT)")
    st.slider("Anzeigedauer pro Aktie (Sekunden)", min_value=5, max_value=60, value=15)
    
    # Platzhalter für eine Tabelle/Liste der aktuell gewählten Aktien
    st.divider()
    st.subheader("Aktive Aktien")
    # ... hier später die dynamische Liste aus der config anzeigen ...

# --- TAB 2: WETTER (Beispiel für spätere Erweiterung) ---
with tab_weather:
    st.header("Wetter-Anzeige")
    
    # Platzhalter für Eingaben
    st.checkbox("Wetter-App aktivieren")
    st.text_input("Stadt")

# --- TAB 3: SYSTEM/EINSTELLUNGEN ---
with tab_settings:
    st.header("Allgemeine Einstellungen")
    
    # Platzhalter für Hardware-Settings
    st.slider("Display-Helligkeit (%)", min_value=10, max_value=100, value=50)
    st.checkbox("Display über Nacht ausschalten (z.B. 22:00 - 06:00 Uhr)")

# 4. Globaler Speicher-Button (außerhalb der Tabs)
st.divider()
if st.button("Konfiguration speichern", type="primary"):
    # Hier kommt später die Logik hin, die alle Eingaben sammelt 
    # und in die config.json auf dem Raspberry Pi schreibt.
    
    # Feedback für den User:
    st.success("Die Konfiguration wurde erfolgreich gespeichert. Das Display aktualisiert sich in Kürze!")