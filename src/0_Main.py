# %%
import streamlit as st
import pandas as pd
import pydeck as pdk
import os

import geopandas as gpd
import json
from shapely.geometry import Point

# add to the top of the page a title which date it was updated: 
st.title("Funda Listings in Amsterdam - Updated: " + pd.Timestamp.now().strftime('%Y-%m-%d'))
# and if it was able to find todays data
if not os.path.exists(os.path.join(os.getcwd(), 'data', f'funda_data_{pd.Timestamp.now().strftime("%Y-%m-%d")}.csv')):
    st.warning("No data found for today. Please run the scraper first to update the listings.")
else:
    st.success("Data for today found. You can filter the listings below.")

# --- Load data ---
today = pd.Timestamp.now().strftime('%Y-%m-%d')
input_path  = os.path.join(os.getcwd(), 'data', f'funda_data_{today}.csv')
df = pd.read_csv(input_path)

# check how many new companies (aangeboden_date = yesterday) are in the data
new_listings_count = df[df['aangeboden_date'] == pd.Timestamp.now().date() - pd.Timedelta(days=1)].shape[0]
st.sidebar.write(f"New listings for {pd.Timestamp.now().date() - pd.Timedelta(days=1)}: {new_listings_count}")

with open("data/neighborhoods_amsterdam.json", "r") as f:
    geojson_data = json.load(f)

# rename m2 to area for consistency
df.rename(columns={'m2': 'area'}, inplace=True)

# --- Check required columns ---
required_cols = ['lat', 'lon', 'street_name', 'number', 'price', 'area', 'url', 'neighborhood']
if not all(col in df.columns for col in required_cols):
    st.error("Missing required columns: lat, lon, street_name, number, price, area, url")
    st.stop()

# --- Calculate price per m² ---
df['price_per_m2'] = df['price'] / df['area']
df['label'] = df['street_name'] + ' ' + df['number']

# --- Filters ---
min_val, max_val = int(df['price_per_m2'].min()), int(df['price_per_m2'].max())
area_min, area_max = int(df['area'].min()), int(df['area'].max())
price_min, price_max = int(df['price'].min()), int(df['price'].max())

filter_beschikbaar = st.checkbox("✅ Only available listings", value=True)

# --- Filters with default values ---
area_range = st.slider(
    "📐 Filter by area (m²)",
    area_min,
    area_max,
    (max(area_min, 50), area_max)  # Default from 50 to max
)
price_range = st.slider(
    "💰 Filter by price (€)",
    price_min,
    price_max,
    (max(price_min, 250000), min(price_max, 450000))  # Default from 250k to 450k
)
selected_range = st.slider(
    "💸 Filter by price per m²",
    min_val,
    max_val,
    (min_val, min(max_val, 10000))  # Default up to 10,000 €/m²
)

filter_berging = st.checkbox("🧱 Only listings with berging (storage)", value=True)

# Servicekosten filter (< 100 or NaN)
filter_servicekosten = st.checkbox("💡 Servicekosten < €100 or missing", value=False)

# Kadaster ground rent (< 100 EUR)
filter_kadaster_lasten = st.checkbox("📜 Kadaster lasten < €100", value=False)

# Eigendom after 2035
filter_eigendom = st.checkbox("🏠 Erfpacht/eigendomjaar after 2035", value=False)

# Min rooms
min_kamers = st.slider("🛏️ Minimum number of rooms", min_value=0, max_value=int(df['num_kamers'].max()), value=0)

# Max woonlagen
max_woonlagen = st.slider("🏢 Max number of woonlagen", min_value=1, max_value=int(df['woonlagen_num'].max()), value=2)

# Date slider
# Ensure 'aangeboden_date' is datetime type for filtering
df['aangeboden_date'] = pd.to_datetime(df['aangeboden_date'])

min_date = df['aangeboden_date'].min().date()
max_date = df['aangeboden_date'].max().date()

# Streamlit date slider
date_range = st.slider(
    "📆 Aangeboden tussen",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="DD-MM-YYYY"
)

# Convert date_range to pandas.Timestamp for comparison
date_range = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))


regions_available = sorted(str(x) for x in df["neighborhood"].dropna().unique())
# Pre-select specific neighborhoods if present
preselect = [
    "Baarsjes", 
    "Erasmusbuurt", 
    "Staatsliedenbuurt", 
    "Bos en Lommer",
    'Unknown',
    'Spaarndammerbuurt',
    'Postjesweg',
]
default_regions = [r for r in regions_available if r.lower() in [x.lower() for x in preselect]]
# --- Neighborhood multiselect with "Select All" button ---
# --- Neighborhood multiselect with "Select All/Unselect All" toggle ---
if "all_selected" not in st.session_state:
    st.session_state["all_selected"] = False

def toggle_select_all():
    st.session_state["all_selected"] = not st.session_state["all_selected"]

select_all = st.button(
    "Select All Neighborhoods" if not st.session_state["all_selected"] else "Unselect All Neighborhoods",
    on_click=toggle_select_all
)

selected_regions = st.multiselect(
    "🗺️ Filter by neighborhood",
    regions_available,
    default=regions_available if st.session_state["all_selected"] else default_regions if default_regions else [],
    key="neigh_multiselect"
)


filtered_df = df[
    ((df['price_per_m2'] >= selected_range[0]) & (df['price_per_m2'] <= selected_range[1]) | (df['price_per_m2'].isna())) &
    ((df['area'] >= area_range[0]) & (df['area'] <= area_range[1]) | (df['area'].isna())) &
    ((df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) | (df['price'].isna())) &
    ((df['neighborhood'].isin(selected_regions)) if selected_regions else True)
]


if filter_berging:
    filtered_df = filtered_df[filtered_df['has_berging'] == True]

if filter_servicekosten:
    filtered_df = filtered_df[
        (filtered_df['servicekosten_num'] < 100) | (filtered_df['servicekosten_num'].isna())
    ]

if filter_beschikbaar:
    filtered_df = filtered_df[filtered_df['beschikbaar'] == True]
    
if filter_kadaster_lasten:
    filtered_df = filtered_df[
        (filtered_df['kadaster_lasten_price'] < 100) | (filtered_df['kadaster_lasten_price'].isna())
    ]

if filter_eigendom:
    filtered_df = filtered_df[filtered_df['eigendom_year'] > 2035]

filtered_df = filtered_df[
    ((filtered_df['num_kamers'] > min_kamers) | (filtered_df['num_kamers'].isna())) &
    ((filtered_df['woonlagen_num'] < max_woonlagen) | (filtered_df['woonlagen_num'].isna())) &
    ((filtered_df['aangeboden_date'] >= date_range[0]) & (filtered_df['aangeboden_date'] <= date_range[1]))
]



map_df = filtered_df.dropna(subset=["lat", "lon"])
map_df = map_df.copy()
map_df['price'] = pd.to_numeric(map_df['price'], errors='coerce')
map_df['area'] = pd.to_numeric(map_df['area'], errors='coerce')
map_df['price_per_m2'] = (map_df['price'] / map_df['area']).round(0)
map_df['price_per_m2_str'] = map_df['price_per_m2'].astype(int).astype(str)
map_df['price_str'] = map_df['price'].astype(int).astype(str)
map_df['area_str'] = map_df['area'].astype(int).astype(str)

# --- Show DataFrame ---
st.write("📄 Filtered Listings")
# Show DataFrame with clickable URLs
def make_clickable(val):
    return f'<a href="{val}" target="_blank">Link</a>'


display_df = filtered_df[
    [
        "label",
        "neighborhood",
        "price",
        "area",
        "price_per_m2",
        "has_berging",
        "aangeboden_date",
        "servicekosten_num",
        'energy_label',
        "eigendom_year",
        "num_kamers",
        "woonlagen_num",
        "beschikbaar",
        "url"
    ]
].rename(columns={
    "label": "full_address",
    "price_per_m2": "price/m2",
    "aangeboden_date": "aangeboden sinds",
    "servicekosten_num": "service_kosten_num",
    "woonlagen_num": "woonlaag_num"
}).copy()

# Round price/m2 to 0 decimals
display_df["price/m2"] = display_df["price/m2"].round(0).astype(int)

display_df["url"] = display_df["url"].apply(make_clickable)

# Center the table using HTML/CSS
st.write(
    f"""
    <div style="display: flex; justify-content: center;">
        <div>
            {display_df.to_html(escape=False, index=False)}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Plot map with gradient ---
if not map_df.empty:
    st.write("🗺️ Interactive Map (hover address, color by price/m²)")

    # Normalize price per m² to color scale (blue to red)
    def scale_color(val, vmin, vmax):
        ratio = (val - vmin) / (vmax - vmin)
        r = int(255 * ratio)
        b = 255 - r
        return [r, 100, b, 180]

    color_data = [
        scale_color(val, selected_range[0], selected_range[1])
        for val in map_df['price_per_m2']
    ]
    map_df = map_df.copy()
    map_df['color'] = color_data

    tooltip = {
        "html": """
            <b>{label}</b><br/>
            €{price_str} - {area_str} m²<br/>
            <b>€{price_per_m2_str}/m²</b>
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }
    # Add polygon layer to map for context
    region_layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        stroked=True,
        filled=True,
        get_fill_color=[200, 100, 100, 40],
        get_line_color=[255, 0, 0],
        line_width_min_pixels=1,
        pickable=False,
    )
    layers=[
        region_layer,
        pdk.Layer(  # Your original ScatterplotLayer
            "ScatterplotLayer",
            data=filtered_df,
            get_position='[lon, lat]',
            get_radius=120,
            get_fill_color='color',
            pickable=True,
        )
    ]

    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=12,
            pitch=0,
        ),
        tooltip=tooltip,
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='[lon, lat]',
                get_radius=120,
                get_fill_color='color',
                pickable=True,
            )
        ]
    ))
    pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_radius=120, get_fill_color='color', pickable=True)
    pdk.Layer("HeatmapLayer", data=map_df, get_position='[lon, lat]', get_weight='price_per_m2', radius_pixels=50)


    # --- Clickable links below map ---
    st.markdown("### 🔗 Listings")
    for _, row in map_df.sort_values("price_per_m2").iterrows():
        st.markdown(f"- [{row['label']} - €{int(row['price'])} ({int(row['price_per_m2'])}/m²)]({row['url']})")
else:
    st.warning("No listings match your filter.")
