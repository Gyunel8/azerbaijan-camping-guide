import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import requests
import glob

st.set_page_config(
    page_title="Azerbaijan Camping Guide",
    page_icon="🏕️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #faf6ee;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif;
    color: #4a3728;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #8b7355 !important;
    color: #faf6ee;
}
[data-testid="stSidebar"] * {
    color: #faf6ee !important;
}
[data-testid="stSidebar"] label {
    color: #f0e8d8 !important;
    font-weight: 500;
}
[data-testid="stSidebar"] .stRadio label {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown small {
    color: #e8dfc8 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #a08060;
}

/* Main background */
[data-testid="stAppViewContainer"] {
    background-color: #faf6ee;
}
[data-testid="stHeader"] {
    background-color: #faf6ee;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background-color: #f0e8d8;
    border: 1px solid #d4c4a8;
    border-radius: 10px;
    padding: 12px;
}

/* Buttons */
div.stButton > button {
    background-color: #a08060;
    color: #faf6ee;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 8px 20px;
}
div.stButton > button:hover {
    background-color: #8b7355;
    color: #ffffff;
}

/* Text input */
div[data-testid="stTextInput"] input {
    background-color: #f5f0e8;
    border: 1px solid #c4b090;
    border-radius: 8px;
    color: #4a3728;
}

/* Select & multiselect */
div[data-testid="stSelectbox"] > div,
div[data-testid="stMultiSelect"] > div {
    background-color: #f5f0e8;
    border-color: #c4b090;
}

/* Slider */
div[data-testid="stSlider"] > div > div > div {
    background-color: #a08060;
}

/* Info/success/warning boxes */
div[data-testid="stInfo"] {
    background-color: #ede4d0;
    border-left-color: #a08060;
    color: #4a3728;
}
div[data-testid="stSuccess"] {
    background-color: #e8f0d8;
    border-left-color: #6b8540;
    color: #3a4a20;
}
div[data-testid="stWarning"] {
    background-color: #f5e8c8;
    border-left-color: #c8943a;
}
div[data-testid="stError"] {
    background-color: #f5e0d8;
    border-left-color: #c05030;
}

/* Expander */
details {
    background-color: #f0e8d8;
    border: 1px solid #d4c4a8;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation_probability"
        r = requests.get(url, timeout=5)
        data = r.json()
        w = data["current_weather"]
        precip = data["hourly"]["precipitation_probability"][0]
        return {"temp": w["temperature"], "wind": w["windspeed"], "precip": precip}
    except:
        return None

@st.cache_data
def load_data():
    data = [
        {"name": "Yeddiler Mountain", "region": "Quba", "type": "Wild Camping", "lat": 41.36, "lon": 48.52, "price_azn": 70, "rating": 5.0, "season": ["Spring","Summer","Autumn","Winter"], "highlight": "Dense mountain forest, total wilderness", "transport": "Bus + GAZ-66", "difficulty": "Hard", "favorite": False, "mosquitoes": False, "distance_km": 181, "description": "Remote mountain area accessible only by Soviet off-road truck. Pure wilderness with no facilities — real adventure camping."},
        {"name": "Tovuz Highlands", "region": "Tovuz", "type": "Wild Camping", "lat": 40.99, "lon": 45.63, "price_azn": 70, "rating": 4.0, "season": ["Summer"], "highlight": "Stunning sunset views", "transport": "Bus + transfer", "difficulty": "Medium", "favorite": False, "mosquitoes": False, "distance_km": 474, "description": "High altitude means cold nights even in August. Famous for breathtaking sunsets over the mountains."},
        {"name": "Canyon to Babadağ", "region": "İsmayıllı", "type": "Wild Camping", "lat": 40.79, "lon": 48.14, "price_azn": 70, "rating": 5.0, "season": ["Summer"], "highlight": "Dramatic canyon + epic thunderstorm", "transport": "Bus + transfer", "difficulty": "Medium", "favorite": False, "mosquitoes": False, "distance_km": 172, "description": "Camped in a canyon on the trail to Babadağ peak. Experienced an all-night thunderstorm — terrifying and unforgettable."},
        {"name": "Zirəvun Pass", "region": "İsmayıllı", "type": "Cabin", "lat": 40.72, "lon": 48.01, "price_azn": 70, "rating": 4.0, "season": ["Winter"], "highlight": "Snow-covered mountain pass in winter", "transport": "Bus + GAZ-66", "difficulty": "Hard", "favorite": False, "mosquitoes": False, "distance_km": 172, "description": "High mountain pass on the İsmayıllı–Qəbələ road. Snow in winter, accessible only by GAZ-66 off-road truck."},
        {"name": "Hamosham Valley", "region": "Lerik", "type": "Wild Camping", "lat": 38.63, "lon": 48.42, "price_azn": 70, "rating": 5.0, "season": ["Spring"], "highlight": "Camping ABOVE the clouds ☁️", "transport": "Bus + transfer", "difficulty": "Hard", "favorite": True, "mosquitoes": False, "distance_km": 304, "description": "Author's favourite place. A cliff-top valley in the subtropical south. In April, you camp literally above the clouds."},
        {"name": "Xızı Colourful Hills", "region": "Xızı", "type": "Wild Camping", "lat": 40.91, "lon": 49.07, "price_azn": 70, "rating": 3.0, "season": ["Autumn"], "highlight": "Multicoloured clay hills on the way", "transport": "Bus + transfer", "difficulty": "Easy", "favorite": False, "mosquitoes": False, "distance_km": 106, "description": "Forest camping near the Caspian. The journey features stunning multicoloured hills — almost like a lunar landscape."},
        {"name": "Daşkəsən River Valley", "region": "Daşkəsən", "type": "Wild Camping", "lat": 40.52, "lon": 46.08, "price_azn": 70, "rating": 4.0, "season": ["Summer"], "highlight": "Beautiful mountain rivers", "transport": "Bus + transfer", "difficulty": "Medium", "favorite": False, "mosquitoes": False, "distance_km": 422, "description": "Camping along mountain rivers in the lesser-visited Daşkəsən district. Fresh water and lush green valleys."},
        {"name": "Xaçmaz Forest & Sea", "region": "Xaçmaz", "type": "Wild Camping", "lat": 41.46, "lon": 48.80, "price_azn": 70, "rating": 4.0, "season": ["Summer"], "highlight": "Beautiful forest near the Caspian Sea", "transport": "Bus", "difficulty": "Easy", "favorite": False, "mosquitoes": True, "distance_km": 169, "description": "Northern coast of Azerbaijan. Lovely forest but prepare for serious mosquitoes in summer. Sea swimming possible."},
        {"name": "Kəpəz Mountain (Göygöl)", "region": "Gəncə / Gədəbəy", "type": "Wild Camping", "lat": 40.59, "lon": 46.35, "price_azn": 70, "rating": 5.0, "season": ["Spring"], "highlight": "4am summit hike at sunrise", "transport": "Bus + transfer", "difficulty": "Hard", "favorite": False, "mosquitoes": False, "distance_km": 367, "description": "Camp at the base of Kəpəz mountain near the famous Göygöl lake. Wake at 4am for the summit hike and watch the sunrise from the top."},
    ]
    return pd.DataFrame(data)

df = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏕️ Azerbaijan\nCamping Guide")
    st.markdown("---")
    page = st.radio("Navigate", ["🔍 Find a Camp", "🗺️ Map View", "📊 Analytics"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### Filters")
    all_regions = sorted(df["region"].unique())
    selected_regions = st.multiselect("Region", all_regions, default=all_regions)
    selected_season = st.selectbox("Season", ["All", "Spring", "Summer", "Autumn", "Winter"])
    selected_type = st.selectbox("Camp Type", ["All"] + sorted(df["type"].unique()))
    selected_difficulty = st.selectbox("Difficulty to Reach", ["All", "Easy", "Medium", "Hard"])
    min_rating = st.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.5)
    hide_mosquitoes = st.checkbox("🦟 Hide places with mosquitoes", value=False)
    st.markdown("---")
    st.markdown("### 🏕️ About")
    st.markdown("<small style='color:#e8dfc8'>Created by an aspiring data analyst passionate about travel and outdoor exploration in Azerbaijan.<br><br>All camping spots were personally visited — this is not just a project, it's a travel diary turned into data.<br><br><b>Data Source:</b> Dataset was manually curated using personal travel experience.<br><br>🚀 <b>V2 coming:</b> AI recommendations, weather API, route planning</small>", unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────────────────
filtered = df[df["region"].isin(selected_regions)]
filtered = filtered[filtered["rating"] >= min_rating]
if selected_season != "All":
    filtered = filtered[filtered["season"].apply(lambda s: selected_season in s)]
if selected_type != "All":
    filtered = filtered[filtered["type"] == selected_type]
if selected_difficulty != "All":
    filtered = filtered[filtered["difficulty"] == selected_difficulty]
if hide_mosquitoes:
    filtered = filtered[filtered["mosquitoes"] == False]

def stars(rating):
    full = int(rating)
    return "★" * full + "☆" * (5 - full)

# ── CARD COLOR PALETTE ────────────────────────────────────────────────────────
CARD_BG        = "#fdf8f0"
CARD_BORDER    = "#c4b090"
CARD_TITLE     = "#4a3728"
CARD_META      = "#6b5840"
ACCENT         = "#a08060"
HIGHLIGHT_BG   = "#ede4d0"
WEATHER_BG     = "#f0e8d8"

# ── PAGE 1: Find a Camp ───────────────────────────────────────────────────────
if page == "🔍 Find a Camp":
    st.markdown("# 🏕️ Find Your Camp in Azerbaijan")
    st.markdown(f"""> *This project helps travelers discover camping destinations in Azerbaijan based on budget, difficulty, and season.*
> *All data is based on real personal experience — 9 places visited over multiple years of camping across the country.*""")
    st.markdown("---")

    st.markdown("### 💡 Key Insights")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🌍 Most camps are in **northern Azerbaijan** (Quba, İsmayıllı, Xaçmaz)")
    with col2:
        st.info("☀️ **Summer** is the most popular season for camping")
    with col3:
        st.info("🏔️ Hard-to-reach places average **4.8⭐** vs Easy places **3.5⭐**")

    st.markdown("---")
    st.markdown("### 🎯 Quick Picks")
    qc1, qc2, qc3, qc4, qc5 = st.columns(5)
    _card = lambda bg, icon, title, sub: f'<div style="background:{bg};border-radius:8px;padding:12px;text-align:center;border:1px solid {CARD_BORDER};">{icon}<br><b style="color:{CARD_TITLE};">{title}</b><br><small style="color:{CARD_META};">{sub}</small></div>'
    with qc1:
        st.markdown(_card("#eaf3de","🌱","Best for Beginners","Xızı · Easy · 106km"), unsafe_allow_html=True)
    with qc2:
        st.markdown(_card("#e8f0ff","❄️","Best Winter Camp","Zirəvun · Cabin · 172km"), unsafe_allow_html=True)
    with qc3:
        st.markdown(_card("#fff3e0","☁️","Most Magical","Hamosham · Above clouds · 304km"), unsafe_allow_html=True)
    with qc4:
        st.markdown(_card("#fce4ec","🏆","Highest Rated","Yeddiler · 5.0⭐ · 181km"), unsafe_allow_html=True)
    with qc5:
        st.markdown(_card("#f3e5f5","🚗","Closest to Baku","Xızı · 106km · Easy"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🤖 Ask AI for a Recommendation")
    user_query = st.text_input("Describe what you're looking for:", placeholder="e.g. I want a peaceful place near water, not too far from Baku")
    if user_query:
        with st.spinner("AI is thinking... 🤔"):
            try:
                groq_key = st.secrets["GROQ_API_KEY"]
                camps_summary = df[["name","region","type","rating","difficulty","season","highlight","distance_km","description"]].to_string(index=False)
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {groq_key}"},
                    json={
                        "model": "llama-3.1-8b-instant",
                        "max_tokens": 300,
                        "messages": [{"role": "user", "content": f"You are a camping guide for Azerbaijan. Based on this list of camps:\n{camps_summary}\n\nUser request: {user_query}\n\nRecommend the best camp and explain why in 2-3 sentences. Be friendly and specific."}]
                    }
                )
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                st.success(f"🏕️ {answer}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")
    col_sur, col_txt = st.columns([1, 4])
    with col_sur:
        surprise = st.button("🎲 Surprise Me!")
    with col_txt:
        st.markdown(f"**{len(filtered)} place{'s' if len(filtered) != 1 else ''} match your filters** — all visited personally, all real experiences.")
    st.markdown("---")

    if surprise and not filtered.empty:
        pick = filtered.sample(1).iloc[0]
        st.success(f"🎲 How about **{pick['name']}** in {pick['region']}? {pick['highlight']} — {pick['distance_km']} km from Baku!")
        st.markdown("---")

    if filtered.empty:
        st.warning("No camps match your current filters. Try adjusting them in the sidebar.")
    else:
        for _, row in filtered.iterrows():
            fav_badge = f'<span style="background:#c0392b;color:white;border-radius:4px;padding:2px 7px;font-size:0.75rem;margin-left:8px;">❤️ Favourite</span>' if row["favorite"] else ""
            mosquito_warn = f'<span style="color:#c0392b;font-size:0.8rem"> 🦟 mosquitoes in summer</span>' if row["mosquitoes"] else ""
            seasons_str = " · ".join(row["season"])

            card_html = f"""<div style="background:{CARD_BG};border-left:4px solid {ACCENT};border-radius:8px;padding:18px 20px;margin-bottom:8px;box-shadow:0 2px 8px rgba(139,115,85,0.10);border:1px solid {CARD_BORDER};border-left:4px solid {ACCENT};">
<div style="font-family:Georgia,serif;color:{CARD_TITLE};font-size:1.1rem;font-weight:bold;margin-bottom:6px;">{row['name']} {fav_badge}</div>
<div style="color:{CARD_META};font-size:0.85rem;margin-bottom:6px;">📍 {row['region']} &nbsp;|&nbsp; 🏷️ {row['type']} &nbsp;|&nbsp; 🚌 {row['transport']} &nbsp;|&nbsp; 💰 {row['price_azn']} AZN/person &nbsp;|&nbsp; 🌡️ {seasons_str} &nbsp;|&nbsp; 🚗 {row['distance_km']} km from Baku {mosquito_warn}</div>
<div style="color:#c8943a;font-size:1rem;">{stars(row['rating'])} &nbsp;<span style="color:{CARD_META};font-size:0.85rem">{row['rating']}/5 · Difficulty: {row['difficulty']}</span></div>
<p style="margin:8px 0 4px 0;color:{CARD_TITLE};font-size:0.9rem">{row['description']}</p>
<span style="background:{HIGHLIGHT_BG};color:{CARD_META};border-radius:4px;padding:3px 8px;font-size:0.8rem;border:1px solid {CARD_BORDER};">✨ {row['highlight']}</span>
</div>"""
            st.markdown(card_html, unsafe_allow_html=True)

            weather = get_weather(row["lat"], row["lon"])
            if weather:
                st.markdown(f'<div style="background:{WEATHER_BG};border-radius:6px;padding:6px 12px;margin-top:-6px;margin-bottom:6px;font-size:0.82rem;color:{CARD_META};border:1px solid {CARD_BORDER};">🌡️ <b>{weather["temp"]}°C</b> &nbsp;|&nbsp; 💨 {weather["wind"]} km/h &nbsp;|&nbsp; 🌧️ {weather["precip"]}% rain chance today</div>', unsafe_allow_html=True)

            baku_lat, baku_lon = 40.4093, 49.8671
            maps_url = f"https://www.google.com/maps/dir/{baku_lat},{baku_lon}/{row['lat']},{row['lon']}"
            st.markdown(f'<a href="{maps_url}" target="_blank" style="background:{ACCENT};color:white;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:0.85rem;margin-bottom:10px;display:inline-block;">🗺️ Get Directions from Baku</a>', unsafe_allow_html=True)

            photo_key = row["region"].lower().split("/")[0].strip().split()[0]
            photo_key = photo_key.replace("İ".lower(),"i").replace("i\u0307","i")
            for ch, rep in [("ə","e"),("ı","i"),("ş","s"),("ç","c"),("ğ","g"),("ö","o"),("ü","u")]:
                photo_key = photo_key.replace(ch, rep)
            photo_files = sorted(glob.glob(f"photos/{photo_key}_*.jpg") + glob.glob(f"photos/{photo_key}_*.jpeg") + glob.glob(f"photos/{photo_key}.jpg"))
            if photo_files:
                with st.expander(f"📸 Show Photos ({len(photo_files)})"):
                    cols = st.columns(min(len(photo_files), 3))
                    for i, photo in enumerate(photo_files):
                        with cols[i % 3]:
                            st.image(photo, width=220)

            st.markdown("<br>", unsafe_allow_html=True)

# ── PAGE 2: Map View ──────────────────────────────────────────────────────────
elif page == "🗺️ Map View":
    st.markdown("# 🗺️ Camps on the Map")
    st.markdown(f"Showing **{len(filtered)}** locations. Click markers for details.")

    m = folium.Map(location=[40.4, 47.5], zoom_start=7, tiles="CartoDB positron")
    for _, row in filtered.iterrows():
        color = "red" if row["favorite"] else "beige"
        popup_html = f"<b>{row['name']}</b><br>⭐ {row['rating']}/5 &nbsp;|&nbsp; 💰 {row['price_azn']} AZN<br>🏷️ {row['type']}<br>✨ {row['highlight']}"
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=row["name"],
            icon=folium.Icon(color=color, icon="leaf", prefix="fa")
        ).add_to(m)

    st_folium(m, width=None, height=520)
    st.markdown("**Legend:** 🔴 Author's favourite &nbsp;|&nbsp; 🟤 All other camps")

# ── PAGE 3: Analytics ─────────────────────────────────────────────────────────
elif page == "📊 Analytics":
    st.markdown("# 📊 Camping Analytics")
    st.markdown("Insights from personal camping experiences across Azerbaijan.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    _metric = lambda val, label: f'<div style="background:{HIGHLIGHT_BG};border-radius:10px;padding:20px;text-align:center;border:1px solid {CARD_BORDER};"><div style="font-family:Georgia,serif;font-size:2rem;color:{ACCENT};">{val}</div><div style="font-size:0.8rem;color:{CARD_META};">{label}</div></div>'
    with col1:
        st.markdown(_metric(len(df), "Places Visited"), unsafe_allow_html=True)
    with col2:
        st.markdown(_metric(df["region"].nunique(), "Regions Explored"), unsafe_allow_html=True)
    with col3:
        st.markdown(_metric(f'{df["rating"].mean():.1f}⭐', "Average Rating"), unsafe_allow_html=True)
    with col4:
        st.markdown(_metric("70 ₼", "Price per Trip"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    CHART_COLOR_SCALE = ["#e8dfc8", "#a08060"]
    CHART_COLORS      = ["#a08060", "#c4b090", "#e8dfc8"]

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Rating by Region")
        region_rating = df.groupby("region")["rating"].mean().sort_values(ascending=True).reset_index()
        fig1 = px.bar(
            region_rating, x="rating", y="region", orientation="h",
            color="rating", color_continuous_scale=CHART_COLOR_SCALE,
            labels={"rating": "Avg Rating", "region": ""}
        )
        fig1.update_layout(
            plot_bgcolor="#faf6ee", paper_bgcolor="#faf6ee",
            coloraxis_showscale=False, height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 5.5], gridcolor="#e8dfc8"),
            font=dict(color="#4a3728")
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown("### Camp Type Distribution")
        type_counts = df["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig2 = px.pie(
            type_counts, values="count", names="type",
            color_discrete_sequence=CHART_COLORS, hole=0.45
        )
        fig2.update_layout(
            plot_bgcolor="#faf6ee", paper_bgcolor="#faf6ee",
            height=360, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            font=dict(color="#4a3728")
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Difficulty to Reach vs Rating")
    difficulty_order = ["Easy", "Medium", "Hard"]
    diff_df = df.copy()
    diff_df["difficulty"] = pd.Categorical(diff_df["difficulty"], categories=difficulty_order, ordered=True)
    diff_avg = diff_df.groupby("difficulty", observed=True)["rating"].mean().reset_index()
    fig3 = px.bar(
        diff_avg, x="difficulty", y="rating",
        color="rating", color_continuous_scale=CHART_COLOR_SCALE,
        labels={"rating": "Avg Rating", "difficulty": "Difficulty to Reach"},
        text="rating"
    )
    fig3.update_traces(texttemplate="%{text:.1f} ⭐", textposition="outside")
    fig3.update_layout(
        plot_bgcolor="#faf6ee", paper_bgcolor="#faf6ee",
        coloraxis_showscale=False, height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[0, 6], gridcolor="#e8dfc8"),
        font=dict(color="#4a3728")
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""> **💡 Key Insight:** Hard-to-reach places tend to get higher ratings — the more effort required, the more rewarding the experience.""")
