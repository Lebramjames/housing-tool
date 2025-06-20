# %%
from bs4 import BeautifulSoup
import re

def extract_vanoverbeek_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.vanoverbeek.nl"

    for obj in soup.select("article.woning"):
        try:
            # URL
            url_tag = obj.select_one("a.adres")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            street = url_tag.get_text(strip=True) if url_tag else None
            city_tag = obj.select_one("span.city")
            city = city_tag.get_text(strip=True) if city_tag else None
            full_adres = f"{street} in {city}" if street and city else None

            # Price
            price = None
            price_tag = obj.select_one("div.price span.value")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = None

            # Area
            area = None
            area_tag = obj.select_one("div.additional span:nth-of-type(1)")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("div.additional span:nth-of-type(2)")
            if room_tag:
                room_match = re.search(r"(\d+)\s+kamer", room_tag.text.lower())
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            status_tag = obj.select_one("span.status-label")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
            available = "Beschikbaar"
            if "verkocht" in status_text:
                available = "Verkocht"
            elif "onder bod" in status_text:
                available = "Onder bod"
            elif "nieuw" in status_text:
                available = "Nieuw"

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
    url ='https://www.vanoverbeek.nl/woningen/koop/'
    html = get_html(url)

    listings = extract_vanoverbeek_data(html)
    for listing in listings:
        print(listing)