# %%
from bs4 import BeautifulSoup
import re

def extract_ikwilhuren_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://ikwilhuren.nu"

    for card in soup.select("div.card-woning"):
        try:
            # URL and Address from title link
            link = card.select_one("a.stretched-link")
            url = base_url + link["href"] if link else None
            title_text = link.get_text(strip=True) if link else ""
            address_line = card.select_one("span.card-title + span")
            address = address_line.get_text(strip=True) if address_line else ""
            full_adres = f"{title_text.strip()} {address.strip()}"

            # City extraction (from postal code)
            city_match = re.search(r"\d{4}[A-Z]{2}\s+(.+)", address)
            city = city_match.group(1).strip() if city_match else None

            # Price
            price_text = card.select_one("div.pt-4 span.fw-bold")
            price_match = re.search(r"€\s?([\d\.,]+)", price_text.text if price_text else "")
            price = None
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Area
            area = None
            area_text = ""
            for span in card.select("div.pt-4 span"):
                if "m²" in span.text or "m" in span.text:
                    area_text = span.text
                    break
            area_match = re.search(r"(\d+)\s*m", area_text)
            if area_match:
                area = int(area_match.group(1))

            # Number of rooms (bedrooms)
            rooms = None
            room_span = card.find("span", string=re.compile(r"\d+\s+slaapkamer", re.I))
            if room_span:
                room_match = re.search(r"(\d+)\s+slaapkamer", room_span.text)
                rooms = int(room_match.group(1)) if room_match else None

            # Availability
            availability = "Onbekend"
            avail_span = card.select_one("span.small span.d-flex")
            if avail_span:
                avail_text = avail_span.get_text(strip=True)
                if "beschikbaar vanaf" in avail_text.lower():
                    availability = avail_text.strip()

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": rooms,
                "available": availability
            })
        except Exception:
            continue

    return listings

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://ikwilhuren.nu/aanbod/'
    html = get_html(url)
    listings = extract_ikwilhuren_data(html)
    for listing in listings:
        print(listing)
    url_format = 'https://ikwilhuren.nu/aanbod/?page={page}'