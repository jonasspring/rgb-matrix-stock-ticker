import streamlit as st
import json
import requests
import pandas as pd

def load_config():
    with open("config.json") as f:
        config = json.load(f)
    st.session_state.config = config

    with open("popular_stocks.json") as f:
        popular_stocks = json.load(f)
    st.session_state.popular_stocks = popular_stocks

def save_config():
    try:
        with open("config.json", "w") as f: 
            json.dump(st.session_state.config, f)
        st.toast("Saving successful!")
    except:
        st.error("Saving failed!")

def save_popular_stocks():
    try:
        with open("popular_stocks.json", "w") as f: 
            json.dump(st.session_state.popular_stocks, f)
    except:
            st.error("Saving failed!")

def update_config():
    st.session_state.config["brightness"] = st.session_state.bright_slider
    st.session_state.config["app_change_freq"] = st.session_state.app_change_freq
    st.session_state.config["stock_app"]["change_interval_sec"] = st.session_state.stock_change_interval_sec
    st.session_state.config["stock_app"]["period"] = st.session_state.stock_period_selectbox
    st.session_state.config["stock_app"]["fetch_interval"] = st.session_state.stock_fetch_interval_min * 60

    st.session_state.config["clock_app"]["change_interval_sec"] = st.session_state.clock_change_interval_sec
    st.session_state.config["clock_app"]["active"] = st.session_state.toggle_clock_app
    

@st.dialog("Select new stock")
def select_new_stock():
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Enter company name", label_visibility="collapsed")
    with col2:
        search_clicked = st.button("Search")
    if search_clicked and search_query:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={search_query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(url, headers=headers).json()
            quotes = response.get('quotes', [])
            st.session_state["stock_search_results"] = quotes
        except Exception as e:
            st.error("Error during search")

    quotes = st.session_state.get("stock_search_results", [])

    if quotes:
        st.write("**Results:**")
        for q in quotes:
            #if q.get('quoteType') == 'EQUITY':
            symbol = q.get('symbol')
            name = q.get('shortname', 'unknown')
            exchange = q.get('exchDisp', '')
            
            # + to add to the list
            if st.button(f"➕ {name} ({symbol}) - {exchange}", key=symbol):
                st.success(f"{symbol} added to config!")

                if symbol not in st.session_state.config["stock_app"]["stocks"].keys():
                    st.session_state.config["stock_app"]["stocks"][symbol] = {"active": True}

                st.session_state.popular_stocks[f"{name} ({symbol})"] = symbol
                save_popular_stocks()
                st.rerun()
    

if "config" not in st.session_state.keys():
    load_config()

# 1. Seitenkonfiguration (sollte immer der erste Streamlit-Befehl sein)
st.set_page_config(page_title="LED Matrix Controller", page_icon="💡", layout="centered")

# 2. Titel und Beschreibung
st.title("LED Matrix Controller")
st.markdown("Verwalte die Anzeigen für deine Raspberry Pi LED Matrix.")

# 3. Layout-Struktur mit Tabs für gute Übersichtlichkeit
tab_stocks, tab_clock, tab_weather, tab_settings = st.tabs(["📈 Stocks", "🕒 Clock", "🌤️ Weather", "⚙️ System"])

# --- TAB 1: AKTIEN ---
with tab_stocks:
    st.header("Stock-Tracker")

    st.slider("Display time per stock (seconds)", min_value=5, max_value=60, value=st.session_state.config["stock_app"]["change_interval_sec"], 
              key="stock_change_interval_sec", on_change=update_config)

    st.slider("Stock update interval", min_value=5, max_value=60, value=st.session_state.config["stock_app"]["fetch_interval"]//60, 
                  key="stock_fetch_interval_min", on_change=update_config)

    stock_period_options = ["1d", "1mo", "1y", "max"] # st.session_state.config["stock_app"]["period"]
    if st.session_state.config["stock_app"]["period"] in stock_period_options:
        idx_sel = stock_period_options.index(st.session_state.config["stock_app"]["period"])
    else:
        idx_sel = 0

    st.selectbox("Display Period", stock_period_options, index=idx_sel, key="stock_period_selectbox", on_change=update_config)

    stock_select_options = [f"**NEUE AKTIE HINZUFÜGEN**"] + list(st.session_state.popular_stocks)

    selected_stock = st.selectbox(
        "Aktie suchen und auswählen", 
        options=stock_select_options,
        placeholder="Tippe 'Apple' oder 'SAP'...",
        index=None # Zeigt den Placeholder am Anfang
    )

    if selected_stock == f"**NEUE AKTIE HINZUFÜGEN**":
        select_new_stock()
    elif selected_stock:
        if st.button("Add stock to active list"):
            symbol_selected = st.session_state.popular_stocks[selected_stock]
            if symbol_selected in st.session_state.config["stock_app"]["stocks"].keys():
                st.error("Stock is already in the list")
            else:
                st.session_state.config["stock_app"]["stocks"][symbol_selected] = {"active": True}
                st.toast("Success")

    # Platzhalter für eine Tabelle/Liste der aktuell gewählten Aktien
    st.divider()
    st.subheader("Aktive Aktien")

    # Über die Aktien iterieren und für jede eine "Karte" (Zeile) zeichnen
    for stock, stock_settings in st.session_state.config["stock_app"]["stocks"].items():
        # Spalten-Layout: 3 Teile für Text, 1 Teil für Toggle, 1 Teil für Löschen
        col1, col2, col3 = st.columns([3, 1, 1], vertical_alignment="center")
        
        with col1:
            st.write(f"**{stock}**")
            
        with col2:
            # Toggle (Schalter) zum schnellen Ausblenden ohne zu löschen
            is_active = st.toggle( 
                "Active", 
                value=stock_settings["active"], 
                key=f"toggle_{stock}", 
                label_visibility="collapsed"
            )
            st.session_state.config["stock_app"]["stocks"][stock]["active"] = is_active
            
        with col3:
            if st.button("❌", key=f"delete_{stock}", help="Remove stock"):
                st.session_state.config["stock_app"]["stocks"].pop(stock)
                st.rerun()

with tab_clock:
    st.header("Clock App")

    st.toggle( "Active", value=st.session_state.config["clock_app"]["active"], 
              key=f"toggle_clock_app", label_visibility="collapsed", on_change=update_config)

    st.slider("Time for Time/Date (seconds)", min_value=5, max_value=60, value=st.session_state.config["clock_app"]["change_interval_sec"], 
                  key="clock_change_interval_sec", on_change=update_config)

    #"active": true,
    #    "change_interval_sec":10,
# --- TAB 2: WETTER (Beispiel für spätere Erweiterung) ---
with tab_weather:
    st.header("Weather App")
    st.header("Work in progress")
    
    # Platzhalter für Eingaben
    #st.checkbox("Wetter-App aktivieren")
    #st.text_input("Stadt")

# --- TAB 3: SYSTEM/EINSTELLUNGEN ---
with tab_settings:
    st.header("General settings")
    #st.info(st.session_state)

    st.slider("☀️ Brightness", 10, 100, key="bright_slider", value=st.session_state.config["brightness"], on_change=update_config)

    st.number_input("⏱️ App change frequency", min_value=5, max_value=3600, key="app_change_freq", 
                    value=st.session_state.config["app_change_freq"], on_change=update_config)


# 4. Globaler Speicher-Button (außerhalb der Tabs)
st.divider()
if st.button("Save configuration", type="primary"):
    
    try:
        save_config()
        st.success("Configuration saved successfully")
    except:
        st.error("Saving failed!")