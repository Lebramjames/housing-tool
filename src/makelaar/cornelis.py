# %%
from bs4 import BeautifulSoup
import re

def extract_hoen_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.hoenmakelaars.nl"

    for obj in soup.select("div.card.shadow"):
        try:
            # Address and city
            h3 = obj.select_one("h3.card-text")
            if h3:
                lines = h3.decode_contents().split("<br>")
                street = lines[0].strip()
                city_postcode = lines[1].strip() if len(lines) > 1 else ""
                full_adres = f"{street} in {city_postcode}"
                city = city_postcode.split()[-1] if city_postcode else None
            else:
                full_adres = None
                city = None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("span.text-blue")
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
            card_text = obj.select_one("div.card-body p.card-text")
            if card_text:
                area_match = re.search(r"(\d+)\s*m", card_text.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            if card_text:
                room_match = re.search(r"(\d+)\s+kamer", card_text.text.lower())
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            available = "Beschikbaar"
            if "onder bod" in card_text.text.lower():
                available = "Onder bod"
            elif "verkocht" in card_text.text.lower():
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
    url ='https://www.hoenmakelaars.nl/koopwoningen'
    html = get_html(url)
    
    listings = extract_hoen_data(html)
    for listing in listings:
        print(listing)
    url_format ='https://www.hoenmakelaars.nl/koopwoningen?plaats=&prijsMinimum=&prijsMaximum=&oppervlakte=&objectType=&status=&page={page}'