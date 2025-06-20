# %%
from bs4 import BeautifulSoup
import re

def extract_brinkborgh_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.brinkborgh.nl"

    for obj in soup.select("a.card-property"):
        try:
            # URL
            url = obj.get("href", "")
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            title = obj.select_one("div.card-property__title h5")
            address_parts = title.stripped_strings if title else []
            address_parts = list(address_parts)
            full_adres = " ".join(address_parts) if address_parts else None

            # City (always last part of the title)
            city = address_parts[-1] if address_parts else None

            # Price
            price = None
            price_tag = obj.select_one("div.card-property__price")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("li:has(i.icon-house)")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("li:has(i.icon-bad)")
            if room_tag:
                room_match = re.search(r"(\d+)\s+slaapkamer", room_tag.text.lower())
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one("div.card-property__label")
            if status_tag:
                status_text = status_tag.get_text(strip=True).lower()
                if "onder bod" in status_text:
                    available = "Onder bod"
                elif "verkocht" in status_text:
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
    url ='https://www.brinkborgh.nl/wonen/zoeken/heel-nederland/koop/'
    html = get_html(url)
    listings = extract_brinkborgh_data(html)
    for listing in listings:
        print(listing)
    
    url_format ='https://www.brinkborgh.nl/wonen/zoeken/heel-nederland/koop/page/{page}/'