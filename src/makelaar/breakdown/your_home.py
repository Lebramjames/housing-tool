# %%
from bs4 import BeautifulSoup
import re

def extract_yourhome_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://yourhome.nl"

    for obj in soup.select("div.house"):
        try:
            # Address and City
            address_tag = obj.select_one("h4.house__address")
            city_tag = obj.select_one("h4.house__place")
            street = address_tag.text.strip() if address_tag else None
            city = city_tag.text.strip() if city_tag else None
            full_adres = f"{street} in {city}" if street and city else None

            # URL
            url_tag = obj.select_one("a.house__link")
            url = url_tag["href"] if url_tag and url_tag.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("li:has(span.listing__label:contains('Vraagprijs')) span.listing__value")
            if not price_tag:
                # fallback for broader structure
                price_tag = obj.find("span", string=re.compile("€"))
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.get_text())
                if price_match:
                    price = float(price_match.group(1).replace(".", "").replace(",", "."))

            # Area
            area = None
            area_tag = obj.find("li", string=re.compile("Woonoppervlak"))
            if area_tag is None:
                area_tag = obj.find("span", string=re.compile(r"\d+\s*m"))
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.get_text())
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.find("li", string=re.compile("Slaapkamers"))
            if room_tag:
                num_match = re.search(r"(\d+)", room_tag.get_text())
                if num_match:
                    num_rooms = int(num_match.group(1))

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one("h6.house__status")
            if status_tag:
                status_text = status_tag.get_text(strip=True).lower()
                if "onder bod" in status_text:
                    available = "Onder bod"
                elif "verkocht" in status_text or "ingetrokken" in status_text:
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

if __name__ == '__main__':
    from src.utils.get_url import get_html
    url ='https://yourhome.nl/aanbod/#q1YqqSxIVbJSys7PLyjPz8vMS0_NU9JRyi9KSS1KqgRKJJcWl-TnxoMFrBKLk5VqAQ'

    html = get_html(url)
    listings = extract_yourhome_data(html)
    for listing in listings:
        print(listing)
            