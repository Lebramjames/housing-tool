# %% Combiner: 
import pandas as pd

def retreve_most_recent_funda_file():
    import os
    import glob

    # Use glob to find all files matching the pattern
    pattern = os.path.join('data', 'funda', 'funda_data_*.csv')
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError("No Funda makelaars files found.")

    # Sort the files by modification time and get the most recent one
    most_recent_file = max(files, key=os.path.getmtime)
    
    return most_recent_file

def retrieve_most_recent_makelaar_file():
    import os
    import glob

    # Get the current working directory
    current_directory = os.getcwd()

    # Use glob to find all files matching the pattern
    pattern = os.path.join('data', 'makelaar', 'makelaar_results_*.csv')
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError("No Makelaars files found.")

    # Sort the files by modification time and get the most recent one
    most_recent_file = max(files, key=os.path.getmtime)
    
    return most_recent_file

# most_recent_funda = retreve_most_recent_funda_file()
# most_recent_makelaar = retrieve_most_recent_makelaar_file()

# df_funda = pd.read_csv(most_recent_funda)
# df_makelaar = pd.read_csv(most_recent_makelaar)
# df_funda = df_funda.rename(columns={
#     "street_name": "street",
#     "number": "number_extension",
#     "full_address": "full_address",
#     "city": "city",
#     "country": "country",
#     "lat": "latitude",
#     "lon": "longitude",
#     "listing_data_soort_appartement": "appartment_type",
#     "listing_data_soort_bouw": "building_type",
#     "listing_data_bouwjaar": "year_built",
#     "listing_data_soort_dak": "roof_type",
#     "listing_data_gebouwgebonden_buitenruimte_m2": "building_attached_outdoor_space_m2",
#     "listing_data_externe_bergruimte_m2": "external_storage_space_m2",
#     "listing_data_inhoud_m3": "volume_m3",
#     "price": "asking_price",
#     "overdracht_prijs_per_m2": "price_per_m2",
#     "overdracht_aangeboden_sinds": "offered_since",
#     "overdracht_status": "status",
#     "overdracht_aanvaarding": "acceptance",
#     "overdracht_servicekosten": "service_costs",
#     "surface_gebouwgebonden_buitenruimte_m2": "surface_building_attached_outdoor_space_m2",
#     "surface_externe_bergruimte_m2": "surface_external_storage_space_m2",
#     "surface_inhoud_m3": "surface_volume_m3",
#     "popularity_bekeken": "views",
#     "popularity_bewaard": "saved",
#     "omschrijving_omschrijving": "description",
#     "buurt_neighborhood_fallback_name": "neighborhood_fallback_name",
#     "buurt_neighborhood_fallback_url": "neighborhood_fallback_url",
#     "energy_label": "energy_label"
# })

# df_makelaar = df_makelaar.rename(columns={
#     "python_file": "broker_name",
#     "url": "url",
#     "area": 'm2',
#     "street": "street",
#     "number_extension": "number_extension",
#     "full_address_processed": "full_address",
#     "city": "city",
#     "price": "price",
#     "area": "area",
#     "num_rooms": "num_rooms",
#     "available": "available"
# })

# # %%
# # Merge DataFrames on latitude and longitude, keeping all columns from both
# df_combined = pd.merge(
#     df_funda,
#     df_makelaar,
#     on=["latitude", "longitude"],
#     how="outer",
#     suffixes=('_funda', '_makelaar')
# )

# # Combine key columns, prioritizing funda, then makelaar
# df_combined['street'] = df_combined['street_funda'].combine_first(df_combined['street_makelaar'])
# df_combined['number_extension'] = df_combined['number_extension_funda'].combine_first(df_combined['number_extension_makelaar'])
# df_combined['city'] = df_combined['city_funda'].combine_first(df_combined['city_makelaar'])
# df_combined['url'] = df_combined['url_funda'].combine_first(df_combined['url_makelaar'])
# df_combined['price'] = df_combined['asking_price'].combine_first(df_combined['price'])
# df_combined['m2'] = df_combined['surface_building_attached_outdoor_space_m2'].combine_first(df_combined['area'])

# # Add a source column: funda, makelaar, or both
# df_combined['source'] = df_combined.apply(
#     lambda row: 'both' if pd.notna(row.get('url_funda')) and pd.notna(row.get('url_makelaar')) else
#                 'funda' if pd.notna(row.get('url_funda')) else
#                 'makelaar' if pd.notna(row.get('url_makelaar')) else
#                 None,
#     axis=1
# )
# # add these to the front of the dataframe and remove the old columns
# df_combined = df_combined[[
#     'street', 'number_extension', "url", 'city', 'price', 'm2',
#     'latitude', 'longitude', 'source'
# ] + [col for col in df_combined.columns if col not in ['street', 
#                                                         'number_extension', "url", 'city', 'price', 
#                                                         'm2', 'latitude', 'longitude', 'source']]]
# df_combined.to_clipboard()
# # %%
# # df_combined filter city in Amsterdam
# df_amsterdam = df_combined[df_combined['city'].str.contains('Amsterdam', case=False, na=False)]
# # df_amsterdam price must have a value
# df_amsterdam = df_amsterdam[df_amsterdam['price'].notna()]
# df_amsterdam

# from src.funda.scrape_main_page import add_neighborhood_info

# # rename lattitude and longitude to lat and lon
# df_amsterdam = df_amsterdam.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
# df = add_neighborhood_info(df_amsterdam)

# # df['max price of 550,000'] 
# df = df[df['price'] <= 550000]
# df['price/m2'] = df['price'] / df['m2']
# # df available == "beschikbaar"
# # df drop neighborhood make neighborhood_right the neighborhood
# # df = df[df['available'] == "beschikbaar"]
# df = df.drop(columns=['neighborhood'])
# df = df.rename(columns={'neighborhood_right': 'neighborhood'})

# df_final = df[['street', 'number_extension', 'url', 'city', 'price', 'm2', 'lat',
#                'lon', 'source', 'price/m2', 'indeling_kamers',
#                 'indeling_badkamers', 'indeling_voorzieningen', 'indeling_woonlagen',
#                 'indeling_verdieping', 'indeling_energielabel', 'indeling_isolatie',
#                 'indeling_verwarming', 'indeling_warm_water',
#                 'kadaster_eigendomssituatie', 'kadaster_lasten', 'appartment_type',
#                 'building_type', 'year_built', 'roof_type',
#                 'building_attached_outdoor_space_m2', 'external_storage_space_m2',
#                 'volume_m3','offered_since', 'status', 'acceptance', 'service_costs',
#                 'surface_building_attached_outdoor_space_m2',   
#                 'surface_external_storage_space_m2', 'surface_volume_m3', 'views',
#                 'saved', 'description', 'neighborhood_fallback_name',
#                 'neighborhood_fallback_url', 'energy_label', 'broker_name',
#                 'neighborhood']]

# today = pd.Timestamp.now().strftime('%Y-%m-%d')
# df_final.to_csv('data/funda_makelaars_combined_{}.csv'.format(today), index=False)
# print("Combined DataFrame saved to 'data/funda_makelaars_combined_{}.csv'".format(today))

# # %%
