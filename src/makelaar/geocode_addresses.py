# %%
import os
import re
import pandas as pd
import pickle
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def save_cache_to_disk(cache_dict, pickle_path, csv_path):
    # Save as pickle
    with open(pickle_path, "wb") as f:
        pickle.dump(cache_dict, f)
    
    # Save as CSV
    df = pd.DataFrame([
        {"full_address_processed": addr, "latitude": lat, "longitude": lon}
        for addr, (lat, lon) in cache_dict.items()
        if lat is not None and lon is not None
    ])
    df.to_csv(csv_path, index=False)


def geocode_addresses_with_history(results_df: pd.DataFrame, cache_path="data/geo_cache.pkl", history_dir="data/makelaars", temp_save_path="geocoding_progress.csv") -> pd.DataFrame:
    # Initialize geocoder
    geolocator = Nominatim(user_agent="funda_scraper")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # Load geo_cache if exists
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            geo_cache = pickle.load(f)
    else:
        geo_cache = {}

    # Step 1: Load all historical files
    historical_coords = pd.DataFrame()
    for fname in os.listdir(history_dir):
        if re.match(r"makelaar_scrape_output_\d{4}-\d{2}-\d{2}\.csv", fname):
            try:
                path = os.path.join(history_dir, fname)
                df_hist = pd.read_csv(path)
                required_cols = {'full_address_processed', 'latitude', 'longitude'}
                if required_cols.issubset(df_hist.columns):
                    historical_coords = pd.concat([historical_coords, df_hist[list(required_cols)]], ignore_index=True)
            except Exception as e:
                print(f"Could not read {fname}: {e}")

    # Step 2: Add historical coords to cache
    for _, row in historical_coords.dropna().iterrows():
        addr = row['full_address_processed']
        if addr not in geo_cache:
            geo_cache[addr] = (row['latitude'], row['longitude'])

    # Step 3: Geocode function using cache
    def get_lat_lon(address):
        if not isinstance(address, str) or address.strip() == "":
            return pd.Series([None, None])
        if address in geo_cache:
            return pd.Series(geo_cache[address])
        try:
            location = geocode(address)
            if location:
                lat_lon = (location.latitude, location.longitude)
                geo_cache[address] = lat_lon
                return pd.Series(lat_lon)
        except Exception as e:
            print(f"Error geocoding '{address}': {e}")
        geo_cache[address] = (None, None)
        return pd.Series([None, None])

    # Step 4: Get missing addresses
    results_df["full_address_processed"] = results_df["full_address_processed"].astype(str)
    missing_addresses = results_df[
        results_df["full_address_processed"].notna() &
        ~results_df["full_address_processed"].isin(geo_cache)
    ]["full_address_processed"].drop_duplicates().tolist()

    print(f"Geocoding {len(missing_addresses)} new addresses...")

    # Step 5: Incrementally geocode and save
    latlon_records = []
    for idx, address in enumerate(missing_addresses, 1):
        lat, lon = get_lat_lon(address)
        latlon_records.append((address, lat, lon))

        if idx % 50 == 0 or idx == len(missing_addresses):
            print(f"Processed {idx}/{len(missing_addresses)} addresses. Saving progress...")

            # Save intermediate geocoded addresses
            latlon_df = pd.DataFrame(latlon_records, columns=['full_address_processed', 'latitude', 'longitude'])
            latlon_df.to_csv(temp_save_path, index=False)

            # Save cache to both pickle and CSV
            save_cache_to_disk(geo_cache, cache_path, "geo_cache.csv")


    # Final merge of newly geocoded addresses
    latlon_df = pd.DataFrame(latlon_records, columns=['full_address_processed', 'latitude', 'longitude'])
    results_df = results_df.merge(latlon_df, on="full_address_processed", how="left")

    # Fill any remaining from the cache (those already geocoded)
    results_df[['latitude', 'longitude']] = results_df.apply(
        lambda row: pd.Series(geo_cache.get(row['full_address_processed'], (row.get('latitude'), row.get('longitude')))),
        axis=1
    )

    return results_df

if __name__ == "__main__":
    # Example usage
    results_df = pd.DataFrame({
        'full_address_processed': ['Van Hallstraat 1, Amsterdam', 'Damstraat 2, Amsterdam', 'Nieuwstraat 3, Amsterdam'],
        'price': [100000, 200000, None],
        'area': [50, 75, None]
    })
    
    results_df = geocode_addresses_with_history(results_df)
    print(results_df)