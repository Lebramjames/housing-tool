# %%
import pandas as pd
import re
import numpy as np
import os
from datetime import datetime, timedelta

def get_aangeboden_date(val, reference_date=None):
    """
    Converts Dutch 'aangeboden sinds' values to datetime.
    Handles both exact dates (e.g. '6 juni 2025') and relative terms (e.g. '3 weken').
    """
    if reference_date is None:
        reference_date = pd.Timestamp.today().normalize()

    val = str(val).strip().lower()

    # Handle relative expressions BEFORE translating months
    if 'vandaag' in val:
        return reference_date
    if '6+' in val and 'maand' in val:
        return reference_date - pd.DateOffset(months=6)
    if 'week' in val:
        match = re.search(r'(\d+)', val)
        if match:
            weeks = int(match.group(1))
            return reference_date - timedelta(weeks=weeks)
    if 'weken' in val:
        match = re.search(r'(\d+)', val)
        if match:
            weeks = int(match.group(1))
            return reference_date - timedelta(weeks=weeks)
    if 'maand' in val:
        match = re.search(r'(\d+)', val)
        if match:
            months = int(match.group(1))
            return reference_date - pd.DateOffset(months=months)

    # Translate Dutch month names to English for date parsing
    dutch_to_english = {
        "januari": "january", "februari": "february", "maart": "march", "april": "april",
        "mei": "may", "juni": "june", "juli": "july", "augustus": "august",
        "september": "september", "oktober": "october", "november": "november", "december": "december"
    }
    for dutch, english in dutch_to_english.items():
        val = val.replace(dutch, english)

    # Try parsing an exact date
    try:
        return pd.to_datetime(val, dayfirst=True, errors='raise')
    except Exception:
        return pd.NaT


def extract_servicekosten(val):
    if pd.isna(val):
        return None
    match = re.search(r'([\d\.,]+)', str(val).replace('.', '').replace(',', '.'))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def parse_lasten_split(text):
    """
    Splits 'kadaster_lasten' into:
    - year_kadaster: 2099 or parsed year if afgekocht
    - price_kadaster: EUR amount, or 0 if afgekocht
    Returns (price_kadaster, year_kadaster)
    """
    if pd.isna(text):
        return (np.nan, np.nan)

    text = str(text).strip().lower()

    if "eeuwigdurend afgekocht" in text:
        return (0.0, 2099)

    if "afgekocht tot" in text:
        match = re.search(r'afgekocht tot (\d{2}-\d{2}-\d{4})', text)
        if match:
            try:
                year = pd.to_datetime(match.group(1), dayfirst=True).year
                return (0.0, year)
            except:
                return (0.0, 2099)
        return (0.0, 2099)

    # Regular price entry
    match = re.search(r'€\s*([\d\.,]+)', text)
    if match:
        number = match.group(1).replace('.', '').replace(',', '.')
        return (float(number), np.nan)

    return (np.nan, np.nan)

def parse_eigendomssituatie_year(text):
    """
    Extracts erfpacht end year or ownership type from eigendomssituatie text.
    - 'einddatum erfpacht: DD-MM-YYYY' → YYYY
    - 'Volle eigendom' → 9999
    - 'Lidmaatschapsrecht' → -1 (optional special code)
    - 'Zie akte' or unknown → NaN
    """
    if pd.isna(text):
        return np.nan

    text = str(text).lower()

    if 'volle eigendom' in text:
        return 9999
    elif 'lidmaatschapsrecht' in text:
        return -1  # use -1 or any other special code if desired
    elif 'einddatum erfpacht' in text:
        match = re.search(r'einddatum erfpacht:\s*(\d{2}-\d{2}-\d{4})', text)
        if match:
            try:
                return pd.to_datetime(match.group(1), dayfirst=True).year
            except:
                return np.nan
    elif 'erfpacht' in text:
        return 0  # erfpacht, but no end date specified

    return np.nan

def parse_woonlaag_to_floor(text):
    """
    Converts 'Gelegen op' values to a numeric floor number.
    - 'Begane grond' → 0
    - '1e woonlaag' → 1
    - '5e woonlaag' → 5
    - NaN or unmatched → np.nan
    """
    if pd.isna(text):
        return np.nan

    text = str(text).strip().lower()

    if 'begane grond' in text:
        return 0

    match = re.search(r'(\d+)e woonlaag', text)
    if match:
        return int(match.group(1))

    return np.nan


def parse_woonlagen_count(text):
    """
    Extracts number of main woonlagen (living floors) from Dutch text.
    Examples:
    - '1 woonlaag' → 1
    - '2 woonlagen en een zolder' → 2
    - NaN or unmatched → np.nan
    """
    if pd.isna(text):
        return np.nan

    text = str(text).strip().lower()
    match = re.search(r'(\d+)\s+woonlaag', text)
    if match:
        return int(match.group(1))

    return np.nan

def parse_kamers_badkamers(text):
    """
    Parses a string to extract number of rooms and bathrooms.
    Returns a tuple: (num_kamers, num_badkamers)
    """
    if pd.isna(text):
        return (np.nan, np.nan)

    text = str(text).lower()

    # Match "X kamer(s)"
    kamer_match = re.search(r'(\d+)\s+kamer', text)
    num_kamers = int(kamer_match.group(1)) if kamer_match else np.nan

    # Match "X badkamer(s)"
    badkamer_match = re.search(r'(\d+)\s+badkamer', text)
    num_badkamers = int(badkamer_match.group(1)) if badkamer_match else 0  # assume 0 if not mentioned

    return (num_kamers, num_badkamers)

# popularity_bekeken,popularity_bewaard
def parse_popularity_data(text):
    """
    Parses popularity data from a string.
    Returns a tuple: (popularity_bekeken, popularity_bewaard)
    """
    if pd.isna(text):
        return (np.nan, np.nan)

    text = str(text).lower()

    # Match "bekeken X keer"
    bekeken_match = re.search(r'bekeken\s+(\d+)\s+keer', text)
    popularity_bekeken = int(bekeken_match.group(1)) if bekeken_match else 0

    # Match "bewaard X keer"
    bewaard_match = re.search(r'bewaard\s+(\d+)\s+keer', text)
    popularity_bewaard = int(bewaard_match.group(1)) if bewaard_match else 0

    return (popularity_bekeken, popularity_bewaard)

def clean_company_scrape():
    """
    Clean the scraped data from Funda company page.
    """
    # Load the data

    date = pd.Timestamp.now().strftime('%Y-%m-%d')
    output_path = f"data/funda_data_{date}.csv"
    # output_path = f'data/funda_data_working_2025-06-18.csv'
    df = pd.read_csv(output_path)
    # Apply the function to the 'overdracht_aangeboden_sinds' column
    df['aangeboden_date'] = df['overdracht_aangeboden_sinds'].apply(
        lambda x: get_aangeboden_date(x, reference_date=pd.Timestamp.today().normalize())
    )
    # Clean 'overdracht_servicekosten' to extract the numeric value as float (EUR/month)
    df['servicekosten_num'] = df['overdracht_servicekosten'].apply(extract_servicekosten)
    df['servicekosten_num']

    df['has_berging'] = (
        df['listing_data_externe_bergruimte_m2'].notna()
    )
    df['has_balkon'] = (
        df['listing_data_gebouwgebonden_buitenruimte_m2'].notna()
    )
    df['listing_data_bouwjaar'] = pd.to_numeric(
        df['listing_data_bouwjaar'], errors='coerce'
    ).astype('Int64')  # Use Int64 to allow NaN values
    df[['kadaster_lasten_price', 'kadaster_lasten_year']] = df['kadaster_lasten'].apply(
        parse_lasten_split
    ).apply(pd.Series)
    df['beschikbaar'] = df['overdracht_status'].apply(lambda x: True if str(x).strip().lower() == 'beschikbaar' else False)

    df['eigendom_year'] = df['kadaster_eigendomssituatie'].apply(parse_eigendomssituatie_year)
    df['eigendom_year'] = df['eigendom_year'].astype('Int64')  # Use Int64 to allow NaN values
    df['woonlaag_num'] = df['indeling_verdieping'].apply(parse_woonlaag_to_floor)
    df[['num_kamers', 'num_badkamers']] = df['indeling_kamers'].apply(parse_kamers_badkamers).apply(pd.Series).astype('Int64')  # Use Int64 to allow NaN values
    df['woonlagen_num'] = df['indeling_woonlagen'].apply(parse_woonlagen_count).astype('Int64') 
    df['bekeken'] = df['popularity_bekeken'].apply(
        lambda x: int(str(x).replace('.', '').replace('x', '').strip()) if pd.notna(x) else 0
    )
    df['bewaard'] = df['popularity_bewaard'].apply(
        lambda x: int(str(x).replace('.', '').replace('x', '').strip()) if pd.notna(x) else 0
    )

    # Calculate the ratio of 'bekeken' to 'bewaard', avoiding division by zero and infinite values
    df['bewaard_bekeken_ratio'] = df['bewaard'] / df['bekeken'].replace({0: np.nan})
    df.to_csv(output_path, index=False)
    print(f"Data cleaned and saved to {output_path}")

if __name__ == "__main__":
    clean_company_scrape()
    print("Company data cleaning completed successfully!")
    