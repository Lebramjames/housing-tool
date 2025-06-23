# %%
from bs4 import BeautifulSoup
import re

def extract_remax_royal_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://makelaar-amsterdam-royal.remax.nl"

    for obj in soup.select("div.object-wrapper a.property"):
        try:
            # URL
            url = obj["href"]
            if not url.startswith("http"):
                url = base_url + url

            # Address & City
            street_tag = obj.select_one("span.title")
            city_tag = obj.select_one("span.city")
            street = street_tag.get_text(strip=True) if street_tag else None
            city = city_tag.get_text(strip=True) if city_tag else None
            full_adres = f"{street} in {city}" if street and city else None

            # Price
            price = None
            price_tag = obj.select_one("span.price")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area
            area = None
            area_tag = obj.select_one("div.info-specs span:nth-of-type(1)")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            rooms_tag = obj.select_one("div.info-specs span:nth-of-type(2)")
            if rooms_tag:
                room_match = re.search(r"(\d+)", rooms_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Available status – no clear "verkocht" or "onder bod" indicators in this HTML
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
        except Exception as e:
            continue

    return listings

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url ='https://makelaar-amsterdam-royal.remax.nl/aanbod/koopwoningen?plaats=Amsterdam'
    html = get_html(url)
    listings = extract_remax_royal_data(html)
    for listing in listings:
        print(listing)

    # https://makelaar-amsterdam-royal.remax.nl/aanbod/koopwoningen?plaats=Amsterdam&page=2