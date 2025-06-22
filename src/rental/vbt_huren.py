# %%
from bs4 import BeautifulSoup
import json
import re

def extract_vbtverhuurmakelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.vbtverhuurmakelaars.nl"

    # Locate <script> tag containing __SAPPER__ object
    script_tag = None
    for s in soup.find_all("script"):
        if s.string and "__SAPPER__=" in s.string:
            script_tag = s.string
            break

    if not script_tag:
        return listings

    try:
        # Extract JSON part inside __SAPPER__
        json_match = re.search(r'__SAPPER__=\{.*?preloaded:\[.*?,(\{.*?\})\]\}', script_tag, re.DOTALL)
        if not json_match:
            return listings

        data_str = json_match.group(1)
        # Safely replace JS undefineds and booleans to be JSON-compatible
        data_str = re.sub(r'\bundefined\b', 'null', data_str)
        data_str = data_str.replace("true", "true").replace("false", "false")

        # Try loading houses list manually (due to nonstandard JSON)
        house_data_matches = re.findall(r'\{address:\{.*?externalLink:"(.*?)".*?\}', data_str)
        house_blocks = re.findall(r'address:\{.*?\},prices:\{.*?\},.*?externalLink:"(.*?)"', data_str)

        # Alternatively, parse the 'houses' array using pattern matching:
        houses = re.findall(r'\{address:(\{.*?\}),prices:(\{.*?\}),.*?rooms:([^,]+),.*?acceptance:"(.*?)".*?externalLink:"(.*?)"', data_str)

        for address_raw, prices_raw, rooms, acceptance, link in houses:
            # Extract address
            house_match = re.search(r'house:"([^"]+)"', address_raw)
            city_match = re.search(r'city:"([^"]+)"', address_raw)
            house = house_match.group(1) if house_match else None
            city = city_match.group(1) if city_match else None
            full_adres = f"{house} in {city}" if house and city else None

            # URL
            url = link if link else None

            # Price
            price_match = re.search(r'price:(\d+)', prices_raw)
            price = int(price_match.group(1)) if price_match else None

            # Area
            plot_match = re.search(r'plot:(\d+)', data_str)
            area = int(plot_match.group(1)) if plot_match else None

            # Rooms
            try:
                num_rooms = int(rooms)
            except ValueError:
                num_rooms = None

            # Availability
            available = f"Beschikbaar vanaf {acceptance[:10]}" if acceptance and acceptance != "null" else "Onbekend"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })
    except Exception as e:
        print(f"Error parsing listings: {e}")

    return listings

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://vbtverhuurmakelaars.nl/woningen'
    html = get_html(url)
    listings = extract_vbtverhuurmakelaars_data(html)
    for listing in listings:
        print(listing)
    url_format = "https://vbtverhuurmakelaars.nl/woningen/{page}"