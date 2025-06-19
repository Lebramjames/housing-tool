# %%
import  pandas as pd 
import numpy as np

from src.utils.get_url import get_html

OUTPUT_COLUMNS = [
    'broker_name',
    'broker_url',
    'full_adres',
    'url',
    'city',
    'price',
    'area',
    'num_rooms',
    'available'
]
INPUT_PATH = r'data/makelaars/input_makelaars_scrape.csv'

df = pd.read_csv(INPUT_PATH)

# # %%
# pages = np.arange(1, 20)
# url_format = 'https://kijck.nl/aanbod?page={pagina}'
# urls = [url_format.format(pagina=pagina) for pagina in pages]

# # first non nan row for pagina:
# row = df.iloc[-7]
# page1 = row['pagina']

# print(page1)

# %%
# html = get_html(page1)
# print(row['Makelaar'])
# first_street_to_find = 'landsmeer'
# # find the 10000 characters above and below the first occurrence of 'Sloterweg' in the first page
# first_page = html
# first_occurrence = first_page.lower().find(first_street_to_find.lower())
# # print if it was found
# if first_occurrence == -1:
#     print(f"'{first_street_to_find}' not found in the first page.")
# else:
#     print(f"'{first_street_to_find}' found at index {first_occurrence} in the first page.")
# start_index = max(0, first_occurrence - 10000)
# end_index = min(len(first_page), first_occurrence + 10000)
# print(first_page[start_index:end_index])
# # pages['https://kijck.nl/aanbod?page=1'] print first 1000 characters
# url = 'https://kijck.nl/aanbod?page=1'


# %%
import  pandas as pd 
import numpy as np

from bs4 import BeautifulSoup

from src.makelaar.kijck import  extract_kijck_data
from src.makelaar.hallie import extract_rijp_data, extract_house_hallie
from src.makelaar.koops import extract_koops_data
from src.makelaar.groot import extract_groot_data
from src.makelaar.scholten import extract_scholten_data
from src.makelaar.eleven import extract_eleven_data
from src.makelaar.pb import extract_pb_data
from src.makelaar.demakelaers import extract_demakelaers_data
from src.makelaar.wester import extract_wester_data
from src.makelaar.makelaars_in_amsterdam import extract_makelaarsadam_data
from src.makelaar.vanhuisuit import extract_vanhuisuit_data

from src.utils.get_url import get_html

OUTPUT_COLUMNS = [
    'broker_name',
    'broker_url',
    'full_adres',
    'url',
    'city',
    'price',
    'area',
    'num_rooms',
    'available'
]
INPUT_PATH = r'data/makelaars/input_makelaars_scrape.csv'

from bs4 import BeautifulSoup

import logging
logging.basicConfig(level=logging.INFO)



makelaars_processors = {
    'KIJCK. makelaars (Almere)': extract_kijck_data,
    'Hallie & Van Klooster Makelaardij': extract_rijp_data,
    'Koops Makelaardij (Amsterdam)': extract_koops_data,
    'Groot Amsterdam Makelaardij B.V.': extract_groot_data,
    'Scholten Makelaars': extract_scholten_data,
    'De Makelaers B.V.': extract_demakelaers_data,
    "Wester Makelaars": extract_wester_data,
    "PB Makelaars o.z.": extract_pb_data,
    "Van Huis Uit Makelaars": extract_vanhuisuit_data,
    "Makelaars van Amsterdam": extract_makelaarsadam_data,
    '11 Makelaars Baerz & Co': extract_eleven_data,
}


def scrape_makelaars_data(df: pd.DataFrame) -> pd.DataFrame:
    datafame = pd.DataFrame(columns=OUTPUT_COLUMNS)

    pages = np.arange(10)
    for makelaar, main_url, url_format1, url_format2 in zip(df['Makelaar'], df['Url'], df['pagina'], df['pagina_2']):

        # if makelaar != row['Makelaar']:
        #     continue

        print(f"Processing {makelaar} from {url_format1}")

        if url_format1 is None or pd.isna(url_format1):
            logging.warning(f"No URL format provided for {makelaar}. Skipping.")
            continue

        if url_format2 is not None:
            logging.info(f"Using pagination for {makelaar} with URL format: {url_format2}")
            try:
                
                urls = [url_format1.format(pagina=pagina) for pagina in pages]
            
            except Exception as e:
                logging.error(f"Error formatting URL for {makelaar}: {e}")
                continue
            print(len(urls), urls)
        else:
            logging.info(f"Using single URL for {makelaar} with URL format: {url_format1}")
            urls = [url_format1]

        print(f"Processing {makelaar} with URLs: {urls}")
        pages = {}

        for idx, url in enumerate(urls):
            print(f"Processing {url}")
            try:
                df_page = get_html(url)
                if df_page:
                    pages[url] = df_page
                    
            except Exception as e:
                logging.error(f"Error processing {url}: {e}")


        listings = []
        for url, html in pages.items():
            
            if makelaar in makelaars_processors:
                try:
                    listings.extend(makelaars_processors[makelaar](html))
                except Exception as e:
                    logging.error(f"Error extracting data for {makelaar} from {url}: {e}")
            else:
                logging.error(f"Unsupported makelaar: {makelaar}")
                continue
                
            listings_df = pd.DataFrame(listings)

            logging.info(f"Extracted {len(listings_df)} listings for {makelaar} from {url}")

            listings_df['broker_name'] = makelaar
            listings_df['broker_url'] = main_url
            datafame = pd.concat([datafame, listings_df], ignore_index=True)

    # datafame filter city == 'Amsterdam'
    datafame = datafame[datafame['city'] == 'Amsterdam']
    # € 1.950.000,- convert price to float
    # Remove euro signs, commas, dashes, and spaces, then convert to float
    datafame['price'] = (
        datafame['price']
        .astype(str)
        .str.replace(r'[€\s\-,]', '', regex=True)
        .str.replace('.', '', regex=False)
        # .str.replace(',', '.', regex=False)
        .astype(float)
    )
    # Convert 'area' column to float, handling values like '269 m2'
    datafame['area'] = (
        datafame['area']
        .astype(str)
        .str.extract(r'(\d+(?:[.,]\d+)?)')  # Extract numeric part
        .replace({',': '.'}, regex=True)
        .astype(float)
    )

    return datafame


from bs4 import BeautifulSoup
house_level = {
    'Hallie & Van Klooster Makelaardij': extract_house_hallie
}

def proces_house_extraction(datafame) -> pd.DataFrame:


    for idx, row in datafame.iterrows():
        if not pd.isna(row['area']):
            continue
        area_value = None
        print(f"Broker: {row['broker_name']}, URL: {row['url']}, Area: {row['area']}")
        if row['broker_name'] in house_level:
            print(f"Extracting area for {row['broker_name']} at {row['url']}")
            try:
                html = get_html(row['url'])
                print(f"Extracting area for {row['broker_name']} at {row['url']}")
                area = house_level[row['broker_name']](html)
                area_value = area.get('woonoppervlakte_m2', None)
            except Exception as e:
                logging.error(f"Error extracting area for {row['broker_name']} at {row['url']}: {e}")
        else:
            logging.warning(f"No area extraction function for {row['broker_name']}. Skipping.")
        datafame.at[idx, 'area'] = area_value
    datafame['price_per_m2'] = round(datafame['price'] / datafame['area'], 0)

    return datafame

today = pd.Timestamp.today().strftime('%Y-%m-%d')
output_path = f'data/makelaars/output_makelaars_scrape_{today}.csv'


df = pd.read_csv(INPUT_PATH)
df = df[df['Makelaar'].notna() & df['pagina_2'].notna()]

dataframe = scrape_makelaars_data(df)
dataframe.to_csv(output_path, index=False)

dataframe = proces_house_extraction(dataframe)
dataframe.to_csv(output_path, index=False)