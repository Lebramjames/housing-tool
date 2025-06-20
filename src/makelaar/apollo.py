# %%
from bs4 import BeautifulSoup
import re

def extract_apollo_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.apollomakelaardij.nl"

    for obj in soup.select("div.property-item"):
        try:
            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"].strip() if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Full address
            address_tag = obj.select_one("h4.address")
            full_adres = address_tag.get_text(strip=True) if address_tag else None

            # City
            city_tag = obj.select_one("div.property-title > div.subtitle")
            city = city_tag.get_text(strip=True) if city_tag else None

            # Price
            price = None
            price_tag = obj.select_one("div.property-price .price-tag")
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("div.meta-title:has(i.fa-expand) + div.meta-data")
            if not area_tag:
                area_tag = obj.find("div", title="Oppervlakte")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            rooms_tag = obj.select_one("div.meta-title:has(i.fa-building-o) + div.meta-data")
            if not rooms_tag:
                rooms_tag = obj.find("div", title="Kamers")
            if rooms_tag:
                rooms_match = re.search(r"(\d+)", rooms_tag.text)
                if rooms_match:
                    num_rooms = int(rooms_match.group(1))

            # Availability
            status_tag = obj.select_one("span.property-status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"
            elif "te koop" in status_text:
                available = "Beschikbaar"
            elif "verhuurd" in status_text or "te huur" in status_text:
                available = "Verhuurd"

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
    url ='https://www.apollomakelaardij.nl/379-2/?location=amsterdam&status=te-koop&max-price=&min-rooms=&orderby=date-new'
    html = get_html(url)
    listings = extract_apollo_data(html)
    for listing in listings:
        print(listing)
    url_format ='https://www.apollomakelaardij.nl/379-2/page/{page}/?location=amsterdam&status=te-koop&max-price&min-rooms&orderby=date-new#038;status=te-koop&max-price&min-rooms&orderby=date-new'
