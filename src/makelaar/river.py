# %%
from bs4 import BeautifulSoup
import re

def extract_river_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for card in soup.select("div.card"):
        try:
            # URL and Address (title structure: Amsterdam – Streetname 123)
            title_tag = card.select_one("a.card__title")
            url = title_tag["href"] if title_tag and "href" in title_tag.attrs else None
            title_text = title_tag.get_text(strip=True) if title_tag else ""
            city, address = title_text.split("–") if "–" in title_text else (None, title_text)
            full_adres = f"{address.strip()} in {city.strip()}" if city else address.strip()

            # Price
            price_tag = card.select_one("div.card__price")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = float(price_match.group(1).replace(".", "").replace(",", ".")) if price_match else None

            # Area
            area = None
            area_tag = card.select_one("div.details__item:has(img[src*='oppervlak']) span")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.get_text())
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            num_rooms = None
            room_tag = card.select_one("div.details__item:has(img[src*='kamers']) span")
            if room_tag:
                room_match = re.search(r"(\d+)", room_tag.get_text())
                num_rooms = int(room_match.group(1)) if room_match else None

            # Availability (assume always "Beschikbaar" unless marked)
            available = "Beschikbaar"  # this site may not show status; could enhance later with sold overlay

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city.strip() if city else None,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })
        except Exception as e:
            continue

    return listings


# Example usage:
if __name__ == "__main__":
    # set base directory as working directory
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.utils.get_url import get_html

    url = 'https://www.rivermakelaardij.nl/en/koopwoningen/#HYyxDsIwDAX_5c0ZWFjyKwghN7GqQBNbsSNAVf-d0BvvpNuhG5Eb4g1UzblnqrgHvERUe3nOsqPSBxHXyx8cAdIz9-U7XRrmUh-niGQp6Fi2ksgLZ_JRY2ZLCFBaea7O7VtaaSs3HD8'
    html = get_html(url)
    listings = extract_river_data(html)
    for listing in listings:
        print(listing)
        