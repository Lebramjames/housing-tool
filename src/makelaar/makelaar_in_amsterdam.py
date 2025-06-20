# %%
from bs4 import BeautifulSoup
import re

def extract_makelaarinamsterdam_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://makelaarinamsterdam.nl"

    for obj in soup.select("div.objectcontainer"):
        try:
            # Address and city
            street_tag = obj.select_one("h5.objecttitle span")
            city_tag = obj.select_one("a.straatnaamwoonplaats span.sub")
            street = street_tag.text.strip() if street_tag else None
            city = city_tag.text.strip() if city_tag else None
            full_adres = f"{street} in {city}" if street and city else None

            # URL
            url_tag = obj.select_one("a.straatnaamwoonplaats")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("span.prijsje")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("li:has(span:contains('Woonoppervlakte')) small")
            if not area_tag:
                area_tag = obj.find("li", string=re.compile("Woonoppervlakte"))
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("li:has(span:contains('Slaapkamers')) small")
            if not room_tag:
                room_tag = obj.find("li", string=re.compile("Slaapkamers"))
            if room_tag:
                room_match = re.search(r"(\d+)", room_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one("h6.objectstatus")
            if status_tag:
                status_text = status_tag.text.strip().lower()
                if "onder bod" in status_text:
                    available = "Onder bod"
                elif "verkocht" in status_text or "verhuurd" in status_text:
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
    url ='https://makelaarinamsterdam.nl/aanbod/?_locaties=amsterdam&_koopprijs=%2C500000'
    html = get_html(url)
    listings = extract_makelaarinamsterdam_data(html)
    for listing in listings:
        print(listing)
        
