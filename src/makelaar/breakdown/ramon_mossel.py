# %%
from bs4 import BeautifulSoup
import re

def extract_ramonmossel_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for article in soup.select("article.woning-item"):
        try:
            # URL
            a_tag = article.select_one("a[href]")
            url = a_tag["href"] if a_tag else None

            # Address
            title_tag = article.select_one("h2")
            full_adres = title_tag.get_text(strip=True) if title_tag else None

            # City (try to extract from address if consistently formatted)
            city = None
            if full_adres and "–" in full_adres:
                parts = full_adres.split("–")
                city = parts[-1].strip()
            
            # Specs block: area, rooms, price, neighborhood
            specs_text = article.select_one("div.specs").get_text(separator=" ", strip=True) if article.select_one("div.specs") else ""
            
            # Area
            area = None
            area_match = re.search(r"(\d+)\s*m", specs_text)
            if area_match:
                area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_match = re.search(r"(\d+)\s+(?:kamers|rooms)", specs_text, re.IGNORECASE)
            if room_match:
                num_rooms = int(room_match.group(1))

            # Price
            price = None
            price_match = re.search(r"€\s?([\d\.,]+)", specs_text)
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Availability
            available = "Beschikbaar"
            label = article.select_one("div.image span.label")
            if label:
                label_text = label.get_text(strip=True).lower()
                if "verkocht onder voorbehoud" in label_text:
                    available = "Verkocht onder voorbehoud"
                elif "verkocht" in label_text:
                    available = "Verkocht"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })

        except Exception:
            continue

    return listings

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://www.ramonmossel.nl/woningen/koop/?plaats=amsterdam&wijk=&minprijs%5Bmin%5D=&maxprijs%5Bmax%5D=498000&minoppervlakte%5Bmin%5D=&maxoppervlakte%5Bmax%5D=&slaapkamers=&orderby=publicatiedatum%3Adesc#search-form'
    html = get_html(url)
    listings = extract_ramonmossel_data(html)
    for listing in listings:
        print(listing)