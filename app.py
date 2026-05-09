import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

st.set_page_config(
    page_title="Airbnb Dashboard",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Airbnb Listings Dashboard")
st.markdown("**Data source:** MongoDB Atlas · sample_airbnb · listingsAndReviews")

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
        df["country"] = df["address"].apply(lambda x: x.get("country", "") if isinstance(x, dict) else "")
        df["market"] = df["address"].apply(lambda x: x.get("market", "") if isinstance(x, dict) else "")
        df.drop(columns=["address"], inplace=True)

    if "review_scores" in df.columns:
        df["rating"] = df["review_scores"].apply(
            lambda x: x.get("review_scores_rating", None) if isinstance(x, dict) else None
        )
        df.drop(columns=["review_scores"], inplace=True)

    df["price"] = pd.to_numeric(df["price"].astype(str), errors="coerce")
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce")
    df["bathrooms"] = pd.to_numeric(df["bathrooms"].astype(str), errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["accommodates"] = pd.to_numeric(df["accommodates"], errors="coerce")
    return df

with st.spinner("Loading data from MongoDB..."):
    df = load_data()

st.success(f"Loaded {len(df):,} listings from MongoDB Atlas")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("🌍 Country", countries)
property_types = ["All"] + sorted(df["property_type"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("🏘 Property Type", property_types)
room_types = ["All"] + sorted(df["room_type"].dropna().unique().tolist())
selected_room = st.sidebar.selectbox("🚪 Room Type", room_types)
max_price = int(df["price"].dropna().quantile(0.95))
price_range = st.sidebar.slider("💰 Price Range ($/night)", 0, max_price, (0, 300))

filtered = df.copy()
if selected_country != "All":
    filtered = filtered[filtered["country"] == selected_country]
if selected_type != "All":
    filtered = filtered[filtered["property_type"] == selected_type]
if selected_room != "All":
    filtered = filtered[filtered["room_type"] == selected_room]
filtered = filtered[(filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])]

# KPI
st.subheader("📊 Overview Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📋 Listings", f"{len(filtered):,}")
c2.metric("💰 Avg Price", f"${filtered['price'].mean():.0f}" if len(filtered) else "N/A")
c3.metric("⭐ Avg Rating", f"{filtered['rating'].mean():.1f}" if filtered['rating'].notna().any() else "N/A")
c4.metric("🛏 Avg Bedrooms", f"{filtered['bedrooms'].mean():.1f}" if filtered['bedrooms'].notna().any() else "N/A")
c5.metric("👥 Avg Accommodates", f"{filtered['accommodates'].mean():.1f}" if filtered['accommodates'].notna().any() else "N/A")

st.divider()

# Charts
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏘 Listings by Property Type")
    prop_count = filtered["property_type"].value_counts().head(10).reset_index()
    prop_count.columns = ["Property Type", "Count"]
    fig1 = px.bar(prop_count, x="Count", y="Property Type", orientation="h",
                  color="Count", color_continuous_scale="Teal")
    fig1.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🚪 Room Type Distribution")
    room_count = filtered["room_type"].value_counts().reset_index()
    room_count.columns = ["Room Type", "Count"]
    fig2 = px.pie(room_count, names="Room Type", values="Count",
                  hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("🌍 Average Price by Country")
    price_country = filtered.groupby("country")["price"].mean().reset_index()
    price_country.columns = ["Country", "Avg Price ($)"]
    price_country = price_country.sort_values("Avg Price ($)", ascending=False)
    fig3 = px.bar(price_country, x="Country", y="Avg Price ($)",
                  color="Avg Price ($)", color_continuous_scale="Oranges")
    fig3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("💰 Price Distribution")
    price_data = filtered["price"].dropna()
    fig4 = px.histogram(price_data, nbins=40, color_discrete_sequence=["#00b4d8"],
                        labels={"value": "Price ($/night)", "count": "Count"})
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.subheader("⭐ Price vs Rating")
    scatter_data = filtered.dropna(subset=["price", "rating"])
    if len(scatter_data) > 0:
        fig5 = px.scatter(scatter_data, x="rating", y="price", color="room_type",
                          hover_data=["name", "country"], opacity=0.6,
                          labels={"rating": "Review Score", "price": "Price ($/night)"})
        st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("🛏 Avg Price by Bedrooms")
    bed_price = filtered.groupby("bedrooms")["price"].mean().reset_index().dropna()
    bed_price.columns = ["Bedrooms", "Avg Price ($)"]
    bed_price = bed_price[bed_price["Bedrooms"] <= 6].sort_values("Bedrooms")
    fig6 = px.line(bed_price, x="Bedrooms", y="Avg Price ($)", markers=True,
                   color_discrete_sequence=["#e63946"])
    st.plotly_chart(fig6, use_container_width=True)

# Data Table
st.subheader("📋 Raw Data Table")
cols_show = ["name", "property_type", "room_type", "bedrooms", "bathrooms",
             "accommodates", "price", "rating", "country", "market"]
cols_available = [c for c in cols_show if c in filtered.columns]
st.dataframe(
    filtered[cols_available].sort_values("price", ascending=False).reset_index(drop=True),
    use_container_width=True, height=400
)

st.caption("Dashboard built with Streamlit + MongoDB Atlas | sample_airbnb dataset")