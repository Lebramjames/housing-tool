# %%
from bs4 import BeautifulSoup
import re

def extract_damesvanvermeer_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for article in soup.select("article.woning"):
        try:
            # URL
            a_tag = article.select_one("h1 a")
            url = a_tag["href"] if a_tag else None

            # Full address (e.g. "Amsterdam – Van Gentstraat 12-2")
            full_adres = a_tag.get_text(strip=True) if a_tag else None

            # City from address or <p>
            city = None
            if full_adres:
                city_match = re.match(r"([A-Za-z\s]+)\s+–", full_adres)
                if city_match:
                    city = city_match.group(1).strip()

            # Entry content paragraphs
            p_tags = article.select("div.entry-content p")
            postcode_city = p_tags[0].get_text(strip=True) if len(p_tags) > 0 else ""
            area_rooms = p_tags[1].get_text(strip=True) if len(p_tags) > 1 else ""
            price_text = p_tags[2].get_text(strip=True) if len(p_tags) > 2 else ""

            # Area (e.g. "60 m2")
            area = None
            area_match = re.search(r"(\d+)\s*m", area_rooms)
            if area_match:
                area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_match = re.search(r"(\d+)\s+kamers?", area_rooms.lower())
            if room_match:
                num_rooms = int(room_match.group(1))

            # Price
            price = None
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Availability (Dames van Vermeer shows only available listings on this page)
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

    url = "https://www.damesvanvermeer.nl/aanbod/"
    html = get_html(url)
    listings = extract_damesvanvermeer_data(html)
    for listing in listings:
        print(listing)