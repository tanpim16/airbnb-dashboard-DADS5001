import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color Palette ─────────────────────────────────────────────────────────────
C_PRIMARY  = "#fe595f"
C_DARK     = "#c73d42"
C_DARKEST  = "#7a1920"
C_LIGHT    = "#ff8a8e"
C_LIGHTER  = "#ffb3b6"
C_LIGHTEST = "#ffd6d8"

GRAD_SCALE = [
    [0.00, C_LIGHTEST],
    [0.35, C_LIGHTER],
    [0.65, C_PRIMARY],
    [1.00, C_DARKEST],
]
QUAL_COLORS = [C_PRIMARY, C_LIGHT, C_LIGHTER, C_DARK, "#ff6b70", C_DARKEST, "#ffc5c7"]


def apply_chart_style(fig, height=340):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,8,10,0.5)",
        font=dict(color="#e0cccc", family="Inter, sans-serif", size=11),
        margin=dict(l=8, r=8, t=8, b=8),
        height=height,
        xaxis=dict(
            gridcolor="rgba(254,89,95,0.12)",
            zerolinecolor="rgba(254,89,95,0.2)",
            tickfont=dict(color="#ccaaaa", size=10),
            title_font=dict(color="#bb9999", size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(254,89,95,0.12)",
            zerolinecolor="rgba(254,89,95,0.2)",
            tickfont=dict(color="#ccaaaa", size=10),
            title_font=dict(color="#bb9999", size=11),
        ),
        legend=dict(
            font=dict(color="#ddc0c0", size=10),
            bgcolor="rgba(20,5,8,0.6)",
            bordercolor="rgba(254,89,95,0.2)",
            borderwidth=1,
        ),
        coloraxis=dict(
            colorbar=dict(
                tickfont=dict(color="#ccaaaa", size=9),
                title_font=dict(color="#ccaaaa", size=10),
                outlinewidth=0,
                bgcolor="rgba(0,0,0,0)",
            )
        ),
    )
    return fig


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], [class*="st-"] {{
    font-family: 'Inter', sans-serif !important;
}}

/* App background */
.stApp {{ background: #0d0709; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: linear-gradient(175deg, #1c090d 0%, #2a1015 60%, #1a080c 100%);
    border-right: 1px solid rgba(254,89,95,0.18);
}}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {{
    color: #ffcccc !important;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label {{
    color: #ffaaaa !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {{
    background: #280d10 !important;
    border-color: rgba(254,89,95,0.25) !important;
    color: #ffe0e0 !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {{
    fill: {C_PRIMARY} !important;
}}
[data-testid="stSidebarContent"] .stSlider [data-baseweb="slider"] {{
    --accent: {C_PRIMARY};
}}

/* ── KPI Metric Cards ── */
[data-testid="metric-container"] {{
    background: linear-gradient(135deg, #1f0c0f 0%, #2d131a 100%);
    border: 1px solid rgba(254,89,95,0.22);
    border-radius: 16px;
    padding: 20px 16px !important;
    box-shadow: 0 4px 24px rgba(254,89,95,0.08), 0 1px 6px rgba(0,0,0,0.5);
    transition: box-shadow 0.25s ease, transform 0.2s ease;
}}
[data-testid="metric-container"]:hover {{
    box-shadow: 0 8px 36px rgba(254,89,95,0.22);
    transform: translateY(-2px);
}}
[data-testid="stMetricLabel"] > div {{
    color: {C_LIGHT} !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}}
[data-testid="stMetricValue"] > div {{
    color: {C_PRIMARY} !important;
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    line-height: 1.15;
}}

/* ── Alert / Success ── */
[data-testid="stAlert"] {{
    background: rgba(254,89,95,0.07) !important;
    border: 1px solid rgba(254,89,95,0.25) !important;
    border-radius: 10px !important;
    color: {C_LIGHT} !important;
}}

/* ── Divider ── */
hr {{ border-color: rgba(254,89,95,0.15) !important; margin: 10px 0 !important; }}

/* ── Dataframe ── */
[data-testid="stDataFrameResizable"] {{
    border: 1px solid rgba(254,89,95,0.2) !important;
    border-radius: 12px !important;
    overflow: hidden;
}}

/* ── Charts border ── */
.stPlotlyChart {{
    border: 1px solid rgba(254,89,95,0.12);
    border-radius: 14px;
    overflow: hidden;
    background: linear-gradient(135deg, #1a090c 0%, #240d12 100%);
    padding: 4px;
}}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: {C_PRIMARY} !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #1a090c; }}
::-webkit-scrollbar-thumb {{
    background: rgba(254,89,95,0.4);
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {C_PRIMARY}; }}

/* ── Text selection ── */
::selection {{ background: rgba(254,89,95,0.3); }}
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="
    background: linear-gradient(135deg, #1f0c0f 0%, #2d1318 50%, #1f0c0f 100%);
    border: 1px solid rgba(254,89,95,0.25);
    border-radius: 20px;
    padding: 30px 36px 24px;
    margin-bottom: 24px;
    box-shadow: 0 8px 40px rgba(254,89,95,0.1), inset 0 1px 0 rgba(255,255,255,0.04);
    text-align: center;
">
    <div style="
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(120deg, #fe595f 0%, #ff8a8e 50%, #c73d42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.15;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    ">
        🏠 Airbnb Analytics Dashboard
    </div>
    <div style="color: #888; font-size: 0.88rem; font-weight: 400; letter-spacing: 0.02em;">
        Exploratory Data Analysis · MongoDB Atlas <span style="color: rgba(254,89,95,0.5);">|</span> sample_airbnb · listingsAndReviews
    </div>
    <div style="margin-top: 14px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
        <span style="
            background: rgba(254,89,95,0.12);
            border: 1px solid rgba(254,89,95,0.28);
            color: #ff8a8e;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 0.73rem;
            font-weight: 600;
            letter-spacing: 0.05em;
        ">LIVE DATA</span>
        <span style="
            background: rgba(254,89,95,0.08);
            border: 1px solid rgba(254,89,95,0.18);
            color: #cc7077;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 0.73rem;
            font-weight: 600;
            letter-spacing: 0.05em;
        ">DADS5001 · DATA VISUALIZATION</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── MongoDB Connection ─────────────────────────────────────────────────────────
@st.cache_resource
def init_connection():
    uri = st.secrets["mongo"]["uri"]
    return MongoClient(uri)


client = init_connection()
db = client["sample_airbnb"]
collection = db["listingsAndReviews"]


@st.cache_data(ttl=600)
def load_data(limit=1000):
    fields = {
        "_id": 0, "name": 1, "property_type": 1, "room_type": 1,
        "bedrooms": 1, "bathrooms": 1, "price": 1, "review_scores": 1,
        "address": 1, "accommodates": 1,
    }
    cursor = collection.find({}, fields, limit=limit)
    df = pd.DataFrame(list(cursor))

    if "address" in df.columns:
        df["country"] = df["address"].apply(
            lambda x: x.get("country", "") if isinstance(x, dict) else ""
        )
        df["market"] = df["address"].apply(
            lambda x: x.get("market", "") if isinstance(x, dict) else ""
        )
        df.drop(columns=["address"], inplace=True)

    if "review_scores" in df.columns:
        df["rating"] = df["review_scores"].apply(
            lambda x: x.get("review_scores_rating", None) if isinstance(x, dict) else None
        )
        df.drop(columns=["review_scores"], inplace=True)

    df["price"]       = pd.to_numeric(df["price"].astype(str), errors="coerce")
    df["bedrooms"]    = pd.to_numeric(df["bedrooms"], errors="coerce")
    df["bathrooms"]   = pd.to_numeric(df["bathrooms"].astype(str), errors="coerce")
    df["rating"]      = pd.to_numeric(df["rating"], errors="coerce")
    df["accommodates"] = pd.to_numeric(df["accommodates"], errors="coerce")
    return df


with st.spinner("Connecting to MongoDB Atlas and loading listings..."):
    df = load_data()

st.success(f"✓  {len(df):,} listings loaded from MongoDB Atlas · sample_airbnb")

# ── Sidebar Filters ────────────────────────────────────────────────────────────
st.sidebar.markdown(
    """
<div style="
    background: linear-gradient(135deg, #2a0e12 0%, #380f16 100%);
    border: 1px solid rgba(254,89,95,0.25);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 18px;
">
    <div style="
        color: #fe595f;
        font-size: 1rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    ">🔍 Filter Panel</div>
    <div style="color: #aa6666; font-size: 0.73rem;">Adjust to refine analysis</div>
</div>
""",
    unsafe_allow_html=True,
)

countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("🌍  Country", countries)

property_types = ["All"] + sorted(df["property_type"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("🏘  Property Type", property_types)

room_types = ["All"] + sorted(df["room_type"].dropna().unique().tolist())
selected_room = st.sidebar.selectbox("🚪  Room Type", room_types)

max_price = int(df["price"].dropna().quantile(0.95))
price_range = st.sidebar.slider("💰  Price Range ($/night)", 0, max_price, (0, 300))

st.sidebar.divider()

# Creator credit in sidebar
st.sidebar.markdown(
    """
<div style="
    background: linear-gradient(135deg, #250c0f 0%, #1e080b 100%);
    border: 1px solid rgba(254,89,95,0.2);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
">
    <div style="color: rgba(254,89,95,0.5); font-size: 0.65rem; font-weight: 700;
                letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px;">
        Created by
    </div>
    <div style="color: #fe595f; font-size: 0.82rem; font-weight: 700; line-height: 1.4;">
        Pimkanit Thongsrikaew
    </div>
    <div style="color: #cc7077; font-size: 0.72rem; font-weight: 500;">
        6810422011
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Apply Filters ─────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_country != "All":
    filtered = filtered[filtered["country"] == selected_country]
if selected_type != "All":
    filtered = filtered[filtered["property_type"] == selected_type]
if selected_room != "All":
    filtered = filtered[filtered["room_type"] == selected_room]
filtered = filtered[
    (filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])
]

# ── KPI Metrics ───────────────────────────────────────────────────────────────
st.markdown(
    '<div style="color:#fe595f;font-size:0.78rem;font-weight:700;text-transform:uppercase;'
    'letter-spacing:0.1em;border-left:3px solid #fe595f;padding-left:10px;margin-bottom:14px;">'
    "KEY PERFORMANCE INDICATORS</div>",
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📋  Total Listings",       f"{len(filtered):,}")
c2.metric("💰  Avg Price / night",    f"${filtered['price'].mean():.0f}"          if len(filtered) else "N/A")
c3.metric("⭐  Avg Rating",           f"{filtered['rating'].mean():.1f}"           if filtered["rating"].notna().any() else "N/A")
c4.metric("🛏  Avg Bedrooms",         f"{filtered['bedrooms'].mean():.1f}"         if filtered["bedrooms"].notna().any() else "N/A")
c5.metric("👥  Avg Accommodates",     f"{filtered['accommodates'].mean():.1f}"     if filtered["accommodates"].notna().any() else "N/A")

st.divider()

# ── Row 1 : Property Type  &  Room Distribution ───────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        '<p style="color:#fe595f;font-size:0.78rem;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.09em;'
        'border-left:3px solid #fe595f;padding-left:9px;margin-bottom:6px;">'
        "🏘  Listings by Property Type</p>",
        unsafe_allow_html=True,
    )
    prop_count = filtered["property_type"].value_counts().head(10).reset_index()
    prop_count.columns = ["Property Type", "Count"]
    fig1 = px.bar(
        prop_count, x="Count", y="Property Type", orientation="h",
        color="Count", color_continuous_scale=GRAD_SCALE,
    )
    fig1.update_traces(marker_line_width=0)
    fig1 = apply_chart_style(fig1)
    fig1.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown(
        '<p style="color:#fe595f;font-size:0.78rem;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.09em;'
        'border-left:3px solid #fe595f;padding-left:9px;margin-bottom:6px;">'
        "🚪  Room Type Distribution</p>",
        unsafe_allow_html=True,
    )
    room_count = filtered["room_type"].value_counts().reset_index()
    room_count.columns = ["Room Type", "Count"]
    fig2 = px.pie(
        room_count, names="Room Type", values="Count",
        hole=0.52, color_discrete_sequence=QUAL_COLORS,
    )
    fig2.update_traces(
        textfont=dict(color="#fff", size=11),
        marker=dict(line=dict(color="#0d0709", width=2)),
        pull=[0.04] + [0] * (len(room_count) - 1),
    )
    fig2 = apply_chart_style(fig2)
    fig2.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2 : Price by Country  &  Price Distribution ──────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown(
        '<p style="color:#fe595f;font-size:0.78rem;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.09em;'
        'border-left:3px solid #fe595f;padding-left:9px;margin-bottom:6px;">'
        "🌍  Average Price by Country</p>",
        unsafe_allow_html=True,
    )
    price_country = (
        filtered.groupby("country")["price"]
        .mean()
        .reset_index()
        .rename(columns={"price": "Avg Price ($)"})
        .sort_values("Avg Price ($)", ascending=False)
    )
    fig3 = px.bar(
        price_country, x="country", y="Avg Price ($)",
        color="Avg Price ($)", color_continuous_scale=GRAD_SCALE,
        labels={"country": "Country"},
    )
    fig3.update_traces(marker_line_width=0)
    fig3 = apply_chart_style(fig3)
    fig3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown(
        '<p style="color:#fe595f;font-size:0.78rem;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.09em;'
        'border-left:3px solid #fe595f;padding-left:9px;margin-bottom:6px;">'
        "💰  Price Distribution ($/night)</p>",
        unsafe_allow_html=True,
    )
    price_data = filtered["price"].dropna()
    fig4 = px.histogram(
        price_data, nbins=40,
        color_discrete_sequence=[C_PRIMARY],
        labels={"value": "Price ($/night)", "count": "Listings"},
    )
    fig4.update_traces(
        marker_line_color=C_DARK, marker_line_width=0.5,
        opacity=0.85,
    )
    fig4 = apply_chart_style(fig4)
    fig4.update_layout(showlegend=False, bargap=0.04)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3 : Price vs Rating  &  Avg Price by Bedrooms ────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown(
        '<p style="color:#fe595f;font-size:0.78rem;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.09em;'
        'border-left:3px solid #fe595f;padding-left:9px;margin-bottom:6px;">'
        "⭐  Price vs Review Score</p>",
        unsafe_allow_html=True,
    )
    scatter_data = filtered.dropna(subset=["price", "rating"])
    if len(scatter_data) > 0:
        fig5 = px.scatter(
            scatter_data, x="rating", y="price",
            color="room_type",
            color_discrete_sequence=QUAL_COLORS,
            hover_data=["name", "country"],
            opacity=0.65,
            labels={"rating": "Review Score", "price": "Price ($/night)", "room_type": "Room Type"},
        )
        fig5.update_traces(marker=dict(size=6, line=dict(width=0.5, color="rgba(0,0,0,0.3)")))
        fig5 = apply_chart_style(fig5)
        st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown(
        '<p style="color:#fe595f;font-size:0.78rem;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.09em;'
        'border-left:3px solid #fe595f;padding-left:9px;margin-bottom:6px;">'
        "🛏  Avg Price by Number of Bedrooms</p>",
        unsafe_allow_html=True,
    )
    bed_price = (
        filtered.groupby("bedrooms")["price"]
        .mean()
        .reset_index()
        .dropna()
        .rename(columns={"bedrooms": "Bedrooms", "price": "Avg Price ($)"})
    )
    bed_price = bed_price[bed_price["Bedrooms"] <= 6].sort_values("Bedrooms")
    fig6 = go.Figure()
    fig6.add_trace(
        go.Scatter(
            x=bed_price["Bedrooms"],
            y=bed_price["Avg Price ($)"],
            mode="lines+markers",
            line=dict(color=C_PRIMARY, width=2.5),
            marker=dict(
                color=bed_price["Avg Price ($)"],
                colorscale=[[0, C_LIGHTEST], [0.5, C_PRIMARY], [1, C_DARKEST]],
                size=10,
                line=dict(color=C_DARK, width=1.5),
            ),
            fill="tozeroy",
            fillcolor="rgba(254,89,95,0.08)",
        )
    )
    fig6.update_layout(
        xaxis_title="Bedrooms",
        yaxis_title="Avg Price ($)",
        showlegend=False,
    )
    fig6 = apply_chart_style(fig6)
    st.plotly_chart(fig6, use_container_width=True)

# ── Data Table ────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="color:#fe595f;font-size:0.78rem;font-weight:700;'
    'text-transform:uppercase;letter-spacing:0.09em;'
    'border-left:3px solid #fe595f;padding-left:9px;margin-bottom:10px;">'
    "📋  Listings Data Table</p>",
    unsafe_allow_html=True,
)

cols_show = ["name", "property_type", "room_type", "bedrooms", "bathrooms",
             "accommodates", "price", "rating", "country", "market"]
cols_available = [c for c in cols_show if c in filtered.columns]
st.dataframe(
    filtered[cols_available].sort_values("price", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=380,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="
    margin-top: 32px;
    padding: 20px 24px;
    background: linear-gradient(135deg, #1f0c0f 0%, #2a1015 100%);
    border: 1px solid rgba(254,89,95,0.18);
    border-radius: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
">
    <div style="color: #664450; font-size: 0.75rem; font-weight: 500;">
        Built with <span style="color: #fe595f;">Streamlit</span> +
        <span style="color: #fe595f;">MongoDB Atlas</span> +
        <span style="color: #fe595f;">Plotly</span>
        &nbsp;·&nbsp; sample_airbnb dataset
    </div>
    <div style="text-align: right;">
        <div style="color: rgba(254,89,95,0.5); font-size: 0.65rem; font-weight: 700;
                    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 2px;">
            Created by
        </div>
        <div style="color: #fe595f; font-size: 0.85rem; font-weight: 700;">
            Pimkanit Thongsrikaew
        </div>
        <div style="color: #aa5560; font-size: 0.75rem; font-weight: 500;">
            6810422011 · DADS5001
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
