
from bs4 import BeautifulSoup

def extract_rijp_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    cards = soup.select("div.object.object-fade")

    for card in cards:
        try:
            # Address parts
            street = card.select_one("span.object-street")
            house_number = card.select_one("span.object-housenumber")
            addition = card.select_one("span.object-housenumber-addition")
            city = card.select_one("span.object-place")

            full_adres = " ".join(filter(None, [
                street.text.strip() if street else "",
                house_number.text.strip() if house_number else "",
                addition.text.strip() if addition else ""
            ])).strip()

            city_name = city.text.strip() if city else "Onbekend"

            # URL
            url_tag = card.select_one("a[href]")
            url = url_tag["href"] if url_tag else None

            # Availability (e.g. "Verkocht", "Beschikbaar", etc.)
            status_elem = card.select_one("div.object-status")
            available = status_elem.text.strip() if status_elem else "Onbekend"

            # Price (may include value and price type like 'k.k.')
            price_elem = card.select_one("span.object-price-value")
            price = price_elem.text.strip() if price_elem else None
            # convert € 400.000 into float
            if price:
                price = price.replace('€', '').replace('.', '').replace(',', '.').strip()
                try:
                    price = float(price)
                except ValueError:
                    price = None

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city_name,
                "price": price,
                "available": available
            })
        except Exception as e:
            print(f"Skipping a listing due to error: {e}")

    return listings

def extract_house_hallie(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    # Woonoppervlakte
    woon = soup.select_one('.object-feature-woonoppervlakte .object-feature-info')
    
    if woon:
        # return woon.text.strip().replace('m²', '').replace('m&sup2;', '').strip()
        result['woonoppervlakte_m2'] = woon.text.strip().replace('m²', '').replace('m&sup2;', '').strip()

    # Inhoud
    inhoud = soup.select_one('.object-feature-inhoud .object-feature-info')
    if inhoud:
        result['inhoud_m3'] = inhoud.text.strip().replace('m³', '').replace('m&sup3;', '').strip()

    # Aantal kamers
    kamers = soup.select_one('.object-feature-aantalkamers .object-feature-info')
    if kamers:
        result['kamers'] = kamers.text.strip()

    # Energielabel
    energielabel = soup.select_one('.object-features-energy .object-feature-info')
    if energielabel:
        result['energielabel'] = energielabel.text.strip()

    # Verwarming
    verwarming = soup.select_one('.object-feature-verwarmingsoorten .object-feature-info')
    if verwarming:
        result['verwarming'] = verwarming.text.strip()

    # Warm water
    warm_water = soup.select_one('.object-feature-warmwatersoorten .object-feature-info')
    if warm_water:
        result['warm_water'] = warm_water.text.strip()

    # Voorzieningen
    voorzieningen = soup.select_one('.object-feature-voorzieningenwonen .object-feature-info')
    if voorzieningen:
        result['voorzieningen'] = voorzieningen.text.strip()

    # Ligging
    ligging = soup.select_one('.object-feature-ligging .object-feature-info')
    if ligging:
        result['ligging'] = ligging.text.strip()

    # Omschrijving (text block)
    omschrijving = soup.select_one('div.object-description')
    if omschrijving:
        result['omschrijving'] = omschrijving.text.strip()

    return result
