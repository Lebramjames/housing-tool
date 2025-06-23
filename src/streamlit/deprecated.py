# %% MAP:
# # --- Plot map with gradient ---
# st.write("🗺️ Interactive Map (hover address, color by price/m²)")

# # Normalize price per m² to color scale (blue to red)
# def scale_color(val, vmin, vmax):
#     ratio = (val - vmin) / (vmax - vmin)
#     r = int(255 * ratio)
#     b = 255 - r
#     return [r, 100, b, 180]

# color_data = [
#     scale_color(val, selected_range[0], selected_range[1])
#     for val in map_df['price_per_m2']
# ]
# map_df = map_df.copy()
# map_df['color'] = color_data

# tooltip = {
#     "html": """
#         <b>{label}</b><br/>
#         €{price_str} - {area_str} m²<br/>
#         <b>€{price_per_m2_str}/m²</b>
#     """,
#     "style": {"backgroundColor": "black", "color": "white"}
# }
# # Add polygon layer to map for context
# region_layer = pdk.Layer(
#     "GeoJsonLayer",
#     geojson_data,
#     stroked=True,
#     filled=True,
#     get_fill_color=[200, 100, 100, 40],
#     get_line_color=[255, 0, 0],
#     line_width_min_pixels=1,
#     pickable=False,
# )
# layers=[
#     region_layer,
#     pdk.Layer(  # Your original ScatterplotLayer
#         "ScatterplotLayer",
#         data=filtered_df,
#         get_position='[lon, lat]',
#         get_radius=120,
#         get_fill_color='color',
#         pickable=True,
#     )
# ]

# st.pydeck_chart(pdk.Deck(
#     initial_view_state=pdk.ViewState(
#         latitude=map_df["lat"].mean(),
#         longitude=map_df["lon"].mean(),
#         zoom=12,
#         pitch=0,
#     ),
#     tooltip=tooltip,
#     layers=[
#         pdk.Layer(
#             "ScatterplotLayer",
#             data=map_df,
#             get_position='[lon, lat]',
#             get_radius=120,
#             get_fill_color='color',
#             pickable=True,
#         )
#     ]
# ))
# pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_radius=120, get_fill_color='color', pickable=True)
# pdk.Layer("HeatmapLayer", data=map_df, get_position='[lon, lat]', get_weight='price_per_m2', radius_pixels=50)

# %%