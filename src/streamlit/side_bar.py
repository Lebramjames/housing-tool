# %%
import streamlit as st
import pandas as pd
import os
from datetime import timedelta


def side_bar_filters(df):
    with st.sidebar:
        st.header("Filters")
        st.markdown("Use the filters below to narrow down the listings.")

        min_val, max_val = int(df['price_per_m2'].min()), int(df['price_per_m2'].max())
        area_min, area_max = int(df['area'].min()), int(df['area'].max())
        price_min, price_max = int(df['price'].min()), int(df['price'].max())

        filter_beschikbaar = st.checkbox("✅ Only available listings", value=True)

        # filter_source including makelaar data or not (make default funda and both, if True then also include makelaar)
        filter_source = st.checkbox("🔗 Include listings from makelaars", value=True)

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

        # Eigendom after 2035 (input box, default 2035)
        eigendom_year_threshold = st.number_input("🏠 Eigendomjaar after...", min_value=1900, max_value=2100, value=2035, step=1)
        filter_eigendom = st.checkbox(f"Filter eigendomjaar > {eigendom_year_threshold}", value=False)

        # Min rooms
        # min_kamers = st.slider("🛏️ Minimum number of rooms", min_value=0, max_value=int(df['num_kamers'].max()), value=0)

        # Max woonlagen
        # max_woonlagen = st.slider("🏢 Max number of woonlagen", min_value=1, max_value=int(df['woonlagen_num'].max()), value=2)

        # Date slider
        # Ensure 'aangeboden_date' is datetime type for filtering
        df['aangeboden_date'] = pd.to_datetime(df['aangeboden_date'])

        min_date = df['aangeboden_date'].min().date()
        max_date = df['aangeboden_date'].max().date()

        # # Streamlit date slider
        # date_range = st.slider(
        #     "📆 Aangeboden tussen",
        #     min_value=min_date,
        #     max_value=max_date,
        #     value=(min_date, max_date),
        #     format="DD-MM-YYYY"
        # )

        # Convert date_range to pandas.Timestamp for comparison
        # date_range = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))


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

    # external_storage_space_m2 if >0 make has_berging True
    filtered_df['has_berging'] = filtered_df['external_storage_space_m2'].apply(lambda x: x > 0 if pd.notna(x) else False)

    # if acceptance or status is beschikbaar than make beschikbaar True
    filtered_df['beschikbaar'] = filtered_df.apply(
        lambda row: (
            (str(row['acceptance']).lower() == 'beschikbaar' if pd.notna(row['acceptance']) else False) or
            (str(row['status']).lower() == 'beschikbaar' if pd.notna(row['status']) else False)
        ),
        axis=1
    )

    if filter_berging:
        filtered_df = filtered_df[filtered_df['has_berging'] == True]

    if filter_servicekosten:
        filtered_df = filtered_df[
            (filtered_df['servicekosten_num'] < 100) | (filtered_df['servicekosten_num'].isna())
        ]
    

    if filter_beschikbaar:
        filtered_df = filtered_df[filtered_df['beschikbaar'] == True]
    if filter_source:
        filtered_df = filtered_df[filtered_df['source'].isin(['funda', 'makelaar', 'both'])]
    else:
        filtered_df = filtered_df[filtered_df['source'].isin(['funda', 'both'])]
    if filter_kadaster_lasten:
        filtered_df = filtered_df[
            (filtered_df['kadaster_lasten_price'] < 100) | (filtered_df['kadaster_lasten_price'].isna())
        ]

    if filter_eigendom:
        filtered_df = filtered_df[filtered_df['eigendom_year'] > 2035]

    # filtered_df = filtered_df[
    #     # ((filtered_df['num_kamers'] > min_kamers) | (filtered_df['num_kamers'].isna())) &
    #     # ((filtered_df['woonlagen_num'] < max_woonlagen) | (filtered_df['woonlagen_num'].isna())) &
    #     ((filtered_df['aangeboden_date'] >= date_range[0]) & (filtered_df['aangeboden_date'] <= date_range[1]))
    # ]
    return filtered_df, selected_range
