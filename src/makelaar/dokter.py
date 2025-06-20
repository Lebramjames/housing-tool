# %%
from bs4 import BeautifulSoup
import re

def extract_dokter_listings(html: str):
    return None
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.doktermakelaars.nl"

    for blok in soup.select("div.blok"):
        try:
            # URL
            a_tag = blok.select_one("a[href]")
            url = a_tag["href"] if a_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Full text block
            text = blok.get_text(" ", strip=True)

            # Full address: match street + number + postcode + city
            address_match = re.search(
                r"([A-Z][a-z]+(?:\s+[A-Z]?[a-z]+)*\s+\d+[A-Z]?[\w\-]*)\s+(\d{4}\s?[A-Z]{2})\s+([A-Z][a-z]+)", text
            )
            if address_match:
                street = address_match.group(1)
                postcode = address_match.group(2)
                city = address_match.group(3)
                full_adres = f"{street} {postcode} {city}"
            else:
                full_adres = None
                city = None

            # Price
            price_match = re.search(r"€\s?([\d\.,]+)", text)
            price = float(price_match.group(1).replace(".", "").replace(",", ".")) if price_match else None

            # Area
            area_match = re.search(r"Woonoppervlakte\s*(\d+)\s*m²", text)
            area = int(area_match.group(1)) if area_match else None

            # Rooms
            room_match = re.search(r"Aantal kamers\s*(\d+)", text)
            num_rooms = int(room_match.group(1)) if room_match else None

            # Status
            if "verkocht" in text.lower():
                available = "Verkocht"
            elif "onder bod" in text.lower():
                available = "Onder bod"
            else:
                available = "Beschikbaar"

            # Skip if it's clearly a page nav or fake listing
            if full_adres is None or url is None or url.endswith("/koop/") or re.match(r".*/pagina-\d+/?$", url):
                continue

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available,
            })

        except Exception:
            continue

    return listings


if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://www.doktermakelaars.nl/aanbod/woningaanbod/-500000/koop/'
    html = get_html(url)
    listings = extract_dokter_data(html)
    for listing in listings:
        print(listing)