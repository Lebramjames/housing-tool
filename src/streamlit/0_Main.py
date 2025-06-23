# %%
import streamlit as st
import pandas as pd
import pydeck as pdk
import os

import geopandas as gpd
import json
from shapely.geometry import Point
from datetime import timedelta
import plotly.express as px
import streamlit.components.v1 as components

# add to the top of the page a title which date it was updated: 
# --- Find latest available data file ---

st.title("Funda Listings in Amsterdam")

def load_data():

    data_dir = os.path.join(os.getcwd(), 'data', 'funda')
    base_name = 'funda_data_'
    ext = '.csv'

    today = pd.Timestamp.now().date()
    max_days_back = 30  # How many days to look back

    found_date = None
    for i in range(max_days_back):
        check_date = today - timedelta(days=i)
        file_name = f"{base_name}{check_date.strftime('%Y-%m-%d')}{ext}"
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            found_date = check_date
            break

    if found_date is None:
        st.error("No data file found in the last 30 days. Please run the scraper to update the listings.")
        st.stop()
    else:
        if found_date == today:
            st.success(f"Using data from: {found_date.strftime('%Y-%m-%d')}, Data for today found. You can filter the listings below.")
        else:
            st.warning(f"Using data from: {found_date.strftime('%Y-%m-%d')}, No data for today. Showing latest available data from {found_date.strftime('%Y-%m-%d')}.")

    # --- Load data ---
    input_path = os.path.join(data_dir, f"{base_name}{found_date.strftime('%Y-%m-%d')}{ext}")
    df = pd.read_csv(input_path)
    df['aangeboden_date'] = pd.to_datetime(df['aangeboden_date'])  # Ensure datetime type
    last_week = df[df['aangeboden_date'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
    # number of new listings this week: 
    # new_listings_count = len(last_week)
    # st.success(f"New listings this week: {new_listings_count}")

    return df

df = load_data()

# check how many new companies (aangeboden_date = yesterday) are in the data

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
from src.streamlit.side_bar import side_bar_filters

filtered_df, selected_range = side_bar_filters(df)

def figure_map():
    map_df = filtered_df.dropna(subset=["lat", "lon"]).copy()
    map_df['price'] = pd.to_numeric(map_df['price'], errors='coerce')
    map_df['area'] = pd.to_numeric(map_df['area'], errors='coerce')
    map_df['price_per_m2'] = (map_df['price'] / map_df['area']).round(0)
    map_df['price_per_m2_str'] = map_df['price_per_m2'].astype(int).astype(str)
    map_df['price_str'] = map_df['price'].astype(int).astype(str)
    map_df['area_str'] = map_df['area'].astype(int).astype(str)

    # Add color scale based on price_per_m2
    min_val = map_df['price_per_m2'].min()
    max_val = map_df['price_per_m2'].max()

    def scale_color(val):
        ratio = (val - min_val) / (max_val - min_val) if max_val > min_val else 0.5
        r = int(255 * ratio)
        b = 255 - r
        return [r, 100, b, 180]

    map_df['color'] = map_df['price_per_m2'].apply(scale_color)

    # Table for display
    def make_clickable(val):
        return f'<a href="{val}" target="_blank">Link</a>'

    display_df = filtered_df[
        [
            "label", "url", "price_per_m2", "num_kamers", "price", "area", "neighborhood",
            "has_berging", "aangeboden_date", "servicekosten_num", "energy_label",
            "eigendom_year", "woonlagen_num", "beschikbaar",
        ]
    ].rename(columns={
        "label": "full_address",
        "price_per_m2": "price/m2",
        "aangeboden_date": "aangeboden sinds",
        "servicekosten_num": "service_kosten_num",
        "woonlagen_num": "woonlaag_num"
    }).copy()

    display_df["price/m2"] = display_df["price/m2"].round(0).astype(int)
    display_df["url"] = display_df["url"].apply(make_clickable)

    return map_df, display_df

map_df, display_df = figure_map()

# --- Scatter plot: price vs area ---
col1, col2 = st.columns([3, 2])

with col1:
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

    tooltip = {
        "html": """
            <b>{label}</b><br/>
            €{price_str} - {area_str} m²<br/>
            <b>€{price_per_m2_str}/m²</b>
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }

    st.write("🗺️ Interactive Map (hover address, color by price/m²)")
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=12,
            pitch=0,
        ),
        tooltip=tooltip,
        layers=[
            region_layer,
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

    with col2:
        st.write("📊 Price vs Area (click dot to open listing)")
        fig = px.scatter(
            map_df,
            x="area",
            y="price",
            hover_name="label",
            hover_data={"price": True, "area": True, "price_per_m2": True, "neighborhood": True},
            custom_data=["url"],  # For click behavior
            labels={"price": "Price (€)", "area": "Area (m²)"},
            height=450,
        )

        fig.update_traces(marker=dict(size=10, color="orange"))

        fig.update_layout(clickmode='event+select')

        # Display Plotly chart
        scatter_click = st.plotly_chart(fig, use_container_width=True)

        # JavaScript for opening URL on click
        components.html("""
        <script>
        const streamlitEvents = window.streamlitEvents || [];

        document.addEventListener('plotly_click', function(e) {
            const url = e.detail.points[0].customdata[0];
            window.open(url, '_blank');
        });

        streamlitEvents.push({
            event: 'plotly_click',
            handler: function(e) {
                const url = e.points[0].customdata[0];
                window.open(url, '_blank');
            }
        });

        window.streamlitEvents = streamlitEvents;
        </script>
        """, height=0)


st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# --- Clickable links below map ---
st.markdown("### 🔗 Listings")
for _, row in map_df.sort_values("price_per_m2").iterrows():
    st.markdown(f"- [{row['label']} - €{int(row['price'])} ({int(row['price_per_m2'])}/m²)]({row['url']})")
