import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Azerbaijan Camping Guide",
    page_icon="🏕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1a2e1a;
    color: #e8f0e8;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #c8dfc8 !important;
    font-weight: 500;
}

/* Cards */
.camp-card {
    background: #ffffff;
    border-left: 4px solid #3d6b3d;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    transition: box-shadow 0.2s;
}
.camp-card:hover {
    box-shadow: 0 4px 16px rgba(61,107,61,0.15);
}
.camp-card h4 {
    font-family: 'Playfair Display', serif;
    color: #1a2e1a;
    margin: 0 0 6px 0;
    font-size: 1.1rem;
}
.camp-card .meta {
    color: #555;
    font-size: 0.85rem;
    margin-bottom: 6px;
}
.camp-card .highlight {
    background: #eaf3ea;
    color: #2d5a2d;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 0.8rem;
    display: inline-block;
    margin-top: 4px;
}
.stars { color: #e8a020; font-size: 1rem; }
.fav-badge {
    background: #c0392b;
    color: white;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 0.75rem;
    margin-left: 8px;
}

/* Metric cards */
.metric-box {
    background: #f4f8f4;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    border: 1px solid #d0e4d0;
}
.metric-box .value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #3d6b3d;
    line-height: 1;
}
.metric-box .label {
    font-size: 0.8rem;
    color: #666;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    data = [
        {
            "name": "Yeddiler Mountain",
            "region": "Quba",
            "type": "Wild Camping",
            "lat": 41.36, "lon": 48.52,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 5.0,
            "season": ["Spring", "Summer", "Autumn", "Winter"],
            "highlight": "Dense mountain forest, total wilderness",
            "transport": "Bus + GAZ-66",
            "nights": 1,
            "difficulty": "Hard",
            "favorite": False,
            "mosquitoes": False,
            "description": "Remote mountain area accessible only by Soviet off-road truck. Pure wilderness with no facilities — real adventure camping."
        },
        {
            "name": "Tovuz Highlands",
            "region": "Tovuz",
            "type": "Wild Camping",
            "lat": 40.99, "lon": 45.63,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 4.0,
            "season": ["Summer"],
            "highlight": "Stunning sunset views",
            "transport": "Bus + transfer",
            "nights": 1,
            "difficulty": "Medium",
            "favorite": False,
            "mosquitoes": False,
            "description": "High altitude means cold nights even in August. Famous for breathtaking sunsets over the mountains."
        },
        {
            "name": "Canyon to Babadağ",
            "region": "İsmayıllı",
            "type": "Wild Camping",
            "lat": 40.79, "lon": 48.14,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 5.0,
            "season": ["Summer"],
            "highlight": "Dramatic canyon + epic thunderstorm",
            "transport": "Bus + transfer",
            "nights": 1,
            "difficulty": "Medium",
            "favorite": False,
            "mosquitoes": False,
            "description": "Camped in a canyon on the trail to Babadağ peak. Experienced an all-night thunderstorm — terrifying and unforgettable."
        },
        {
            "name": "Zirəvun Pass",
            "region": "İsmayıllı",
            "type": "Cabin / Guesthouse",
            "lat": 40.72, "lon": 48.01,
            "price_azn": 70,
            "amenities": "Cabin with walls and roof 😄",
            "rating": 4.0,
            "season": ["Winter"],
            "highlight": "Snow-covered mountain pass in winter",
            "transport": "Bus + GAZ-66",
            "nights": 1,
            "difficulty": "Hard",
            "favorite": False,
            "mosquitoes": False,
            "description": "High mountain pass on the İsmayıllı–Qəbələ road. Snow in winter, accessible only by GAZ-66 off-road truck."
        },
        {
            "name": "Hamışam Valley",
            "region": "Lerik / Astara",
            "type": "Wild Camping",
            "lat": 38.63, "lon": 48.42,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 5.0,
            "season": ["Spring"],
            "highlight": "Camping ABOVE the clouds ☁️",
            "transport": "Bus + transfer",
            "nights": 1,
            "difficulty": "Hard",
            "favorite": True,
            "mosquitoes": False,
            "description": "Author's favourite place. A cliff-top valley in the subtropical south. In April, you camp literally above the clouds — one of the most magical experiences in Azerbaijan."
        },
        {
            "name": "Xızı Colourful Hills",
            "region": "Xızı",
            "type": "Wild Camping",
            "lat": 40.91, "lon": 49.07,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 3.0,
            "season": ["Autumn"],
            "highlight": "Multicoloured clay hills on the way",
            "transport": "Bus + transfer",
            "nights": 1,
            "difficulty": "Easy",
            "favorite": False,
            "mosquitoes": False,
            "description": "Forest camping near the Caspian. The journey features stunning multicoloured hills — almost like a lunar landscape."
        },
        {
            "name": "Daşkəsən River Valley",
            "region": "Daşkəsən",
            "type": "Wild Camping",
            "lat": 40.52, "lon": 46.08,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 4.0,
            "season": ["Summer"],
            "highlight": "Beautiful mountain rivers",
            "transport": "Bus + transfer",
            "nights": 1,
            "difficulty": "Medium",
            "favorite": False,
            "mosquitoes": False,
            "description": "Camping along mountain rivers in the lesser-visited Daşkəsən district. Fresh water and lush green valleys."
        },
        {
            "name": "Xaçmaz Forest & Sea",
            "region": "Xaçmaz",
            "type": "Wild Camping",
            "lat": 41.46, "lon": 48.80,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 4.0,
            "season": ["Summer"],
            "highlight": "Beautiful forest near the Caspian Sea",
            "transport": "Bus",
            "nights": 1,
            "difficulty": "Easy",
            "favorite": False,
            "mosquitoes": True,
            "description": "Northern coast of Azerbaijan. Lovely forest but prepare for serious mosquitoes in summer. Sea swimming possible."
        },
        {
            "name": "Kəpəz Mountain (Göygöl)",
            "region": "Gəncə / Gədəbəy",
            "type": "Wild Camping",
            "lat": 40.59, "lon": 46.35,
            "price_azn": 70,
            "amenities": "None (bring everything)",
            "rating": 5.0,
            "season": ["Spring"],
            "highlight": "4am summit hike at sunrise",
            "transport": "Bus + transfer",
            "nights": 1,
            "difficulty": "Hard",
            "favorite": False,
            "mosquitoes": False,
            "description": "Camp at the base of Kəpəz mountain near the famous Göygöl lake. Wake at 4am for the summit hike and watch the sunrise from the top."
        },
    ]
    return pd.DataFrame(data)

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏕️ Azerbaijan\nCamping Guide")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🔍 Find a Camp", "🗺️ Map View", "📊 Analytics"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### Filters")

    all_regions = sorted(df["region"].unique())
    selected_regions = st.multiselect("Region", all_regions, default=all_regions)

    all_seasons = ["Spring", "Summer", "Autumn", "Winter"]
    selected_season = st.selectbox("Season", ["All"] + all_seasons)

    all_types = sorted(df["type"].unique())
    selected_type = st.selectbox("Camp Type", ["All"] + all_types)

    difficulty_options = ["All", "Easy", "Medium", "Hard"]
    selected_difficulty = st.selectbox("Difficulty to Reach", difficulty_options)

    min_rating = st.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.5)

    hide_mosquitoes = st.checkbox("🦟 Hide places with mosquitoes", value=False)

    st.markdown("---")
    st.markdown("<small style='color:#a0b8a0'>Based on real personal experience<br>by an Azerbaijani camper 🏕️</small>", unsafe_allow_html=True)

# ── Filter data ───────────────────────────────────────────────────────────────
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

# ── Helper ────────────────────────────────────────────────────────────────────
def stars(rating):
    full = int(rating)
    return "★" * full + "☆" * (5 - full)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — FIND A CAMP
# ══════════════════════════════════════════════════════════════════════════════
if page == "🔍 Find a Camp":
    st.markdown("# 🏕️ Find Your Camp in Azerbaijan")
    st.markdown(f"**{len(filtered)} place{'s' if len(filtered) != 1 else ''} match your filters** — all visited personally, all real experiences.")
    st.markdown("---")

    if filtered.empty:
        st.warning("No camps match your current filters. Try adjusting them in the sidebar.")
    else:
        for _, row in filtered.iterrows():
            fav_badge = '<span class="fav-badge">❤️ Author\'s Favourite</span>' if row["favorite"] else ""
            mosquito_warn = '<span style="color:#c0392b; font-size:0.8rem"> 🦟 mosquitoes in summer</span>' if row["mosquitoes"] else ""
            seasons_str = " · ".join(row["season"])

            st.markdown(f"""
            <div class="camp-card">
                <h4>{row['name']} {fav_badge}</h4>
                <div class="meta">
                    📍 {row['region']} &nbsp;|&nbsp;
                    🏷️ {row['type']} &nbsp;|&nbsp;
                    🚌 {row['transport']} &nbsp;|&nbsp;
                    💰 {row['price_azn']} AZN/person &nbsp;|&nbsp;
                    🌡️ {seasons_str}
                    {mosquito_warn}
                </div>
                <div class="stars">{stars(row['rating'])} &nbsp;<span style="color:#333;font-size:0.85rem">{row['rating']}/5 · Difficulty: {row['difficulty']}</span></div>
                <p style="margin:8px 0 4px 0; color:#333; font-size:0.9rem">{row['description']}</p>
                <span class="highlight">✨ {row['highlight']}</span>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MAP VIEW
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Map View":
    st.markdown("# 🗺️ Camps on the Map")
    st.markdown(f"Showing **{len(filtered)}** location{'s' if len(filtered) != 1 else ''}. Click markers for details.")

    m = folium.Map(location=[40.4, 47.5], zoom_start=7, tiles="CartoDB positron")

    for _, row in filtered.iterrows():
        color = "red" if row["favorite"] else "darkgreen"
        icon = "heart" if row["favorite"] else "tree-conifer"
        popup_html = f"""
        <b style='font-size:13px'>{row['name']}</b><br>
        ⭐ {row['rating']}/5 &nbsp;|&nbsp; 💰 {row['price_azn']} AZN<br>
        🏷️ {row['type']}<br>
        ✨ {row['highlight']}
        """
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=row["name"],
            icon=folium.Icon(color=color, icon="leaf", prefix="fa"),
        ).add_to(m)

    st_folium(m, width=None, height=520)

    st.markdown("---")
    st.markdown("**Legend:** 🔴 Author's favourite &nbsp;|&nbsp; 🟢 All other camps")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics":
    st.markdown("# 📊 Camping Analytics")
    st.markdown("Insights from personal camping experiences across Azerbaijan.")
    st.markdown("---")

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-box"><div class="value">{len(df)}</div><div class="label">Places Visited</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="value">{df["region"].nunique()}</div><div class="label">Regions Explored</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><div class="value">{df["rating"].mean():.1f}⭐</div><div class="label">Average Rating</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-box"><div class="value">70 ₼</div><div class="label">Price per Trip</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Rating by Region")
        region_rating = df.groupby("region")["rating"].mean().sort_values(ascending=True).reset_index()
        fig1 = px.bar(
            region_rating, x="rating", y="region", orientation="h",
            color="rating", color_continuous_scale=["#c8dfc8", "#3d6b3d"],
            labels={"rating": "Avg Rating", "region": ""},
        )
        fig1.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False, height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 5.5])
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown("### Camp Type Distribution")
        type_counts = df["type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig2 = px.pie(
            type_counts, values="count", names="type",
            color_discrete_sequence=["#3d6b3d", "#7aad7a", "#c8dfc8"],
            hole=0.45,
        )
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=360, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Difficulty to Reach vs Rating")
    difficulty_order = ["Easy", "Medium", "Hard"]
    diff_df = df.copy()
    diff_df["difficulty"] = pd.Categorical(diff_df["difficulty"], categories=difficulty_order, ordered=True)
    diff_avg = diff_df.groupby("difficulty", observed=True)["rating"].mean().reset_index()

    fig3 = px.bar(
        diff_avg, x="difficulty", y="rating",
        color="rating", color_continuous_scale=["#c8dfc8", "#3d6b3d"],
        labels={"rating": "Avg Rating", "difficulty": "Difficulty to Reach"},
        text="rating"
    )
    fig3.update_traces(texttemplate="%{text:.1f} ⭐", textposition="outside")
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[0, 6])
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    > **💡 Key Insight:** Hard-to-reach places tend to get higher ratings —
    > the more effort required, the more rewarding the experience.
    > This matches real camper behaviour: difficulty filters out casual visitors
    > and attracts those who truly appreciate nature.
    """)
