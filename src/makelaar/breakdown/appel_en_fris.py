# %%
from bs4 import BeautifulSoup
import re

def extract_appelenfris_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.appelenfrismakelaars.nl"

    for obj in soup.select("div.blok.aanbodZoekResultaatBlok"):  # Listing block
        try:
            # Full address
            address_tag = obj.select_one("div.titel a")
            address_text = address_tag.get_text(strip=True) if address_tag else None

            # Assume address format like "Oranjestraat 12, Haarlem"
            full_adres = address_text
            city = None
            if address_text and "," in address_text:
                street_part, city = map(str.strip, address_text.split(",", 1))

            # URL
            url = address_tag["href"] if address_tag and address_tag.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("div.prijs span")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price = float(price_match.group(1).replace(".", "").replace(",", "."))

            # Area
            area = None
            area_tag = obj.select_one("div.oppervlakte")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m²", area_tag.text)
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            num_rooms = None
            rooms_tag = obj.select_one("div.kamers")
            if rooms_tag:
                rooms_match = re.search(r"(\d+)\s+kamer", rooms_tag.text)
                num_rooms = int(rooms_match.group(1)) if rooms_match else None

            # Availability (e.g., status label like 'Verkocht' or 'Onder bod')
            available = "Beschikbaar"
            status_tag = obj.select_one("div.status")
            if status_tag:
                status = status_tag.get_text(strip=True).lower()
                if "verkocht" in status:
                    available = "Verkocht"
                elif "onder bod" in status:
                    available = "Onder bod"

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
    url = 'https://www.appelenfrismakelaars.nl/aanbod/woningaanbod/'
    html = get_html(url)
    listings = extract_appelenfris_data(html)
    for listing in listings:
        print(listing)
# %%
def debug_appelenfris_structure(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for div in soup.find_all("div"):
        classes = div.get("class", [])
        if len(classes) >= 2:
            print("==== DIV CLASSES ====", classes)
            print(div.prettify()[:1000])  # limit output to avoid flooding

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://www.appelenfrismakelaars.nl/aanbod/woningaanbod/'
    html = get_html(url)
    debug_appelenfris_structure(html)