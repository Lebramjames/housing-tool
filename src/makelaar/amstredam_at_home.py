# %%
from bs4 import BeautifulSoup
import re

def extract_makelaaramsterdam_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.makelaaramsterdam.nl"

    for obj in soup.select("a.object"):
        try:
            # URL
            url = obj["href"] if obj.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            street_tag = obj.select_one("h3.entry-title")
            number_tag = obj.select_one("h3.entry-title .h-nr")
            street = street_tag.get_text(strip=True).replace(number_tag.get_text(strip=True), "") if street_tag and number_tag else None
            number = number_tag.get_text(strip=True) if number_tag else ""
            city = "Amsterdam"  # consistent in all entries

            full_adres = f"{street.strip()} {number} in {city}" if street else None

            # Price
            price_tag = obj.select_one("p.prijs span.w-price")
            price = None
            if price_tag:
                try:
                    price = float(price_tag.text.replace(".", "").replace(",", "."))
                except ValueError:
                    pass

            # Area
            area_tag = obj.select_one("p.oppervlakte")
            area = None
            if area_tag:
                match = re.search(r"(\d+)", area_tag.text)
                if match:
                    area = int(match.group(1))

            # Number of rooms
            room_tag = obj.select_one("p.kamers")
            num_rooms = None
            if room_tag:
                match = re.search(r"(\d+)", room_tag.text)
                if match:
                    num_rooms = int(match.group(1))

            # Status — only "Beschikbaar" is directly visible; others like "Verkocht" or "Onder bod" need page-level scraping
            available = "Beschikbaar"

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
    url = 'https://www.makelaaramsterdam.nl/woning-aanbod/?_sf_s=amsterdam'
    html = get_html(url)
    listings = extract_makelaaramsterdam_data(html)
    for listing in listings:
        print(listing)