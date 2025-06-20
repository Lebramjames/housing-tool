# %%
from bs4 import BeautifulSoup
import re

def extract_burgerelkerbout_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://www.burgerelkerbout.nl"
    listings = []

    for obj in soup.select("div.object.object-element1"):
        try:
            # URL and address
            adres_tag = obj.select_one("div.object-adres a.adreslink")
            url = adres_tag['href'].strip() if adres_tag and adres_tag.get("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            address_tag = obj.select_one("h4 span.adres")
            city_tag = obj.select_one("h4 span.plaatsnaam")
            address = address_tag.get_text(strip=True) if address_tag else None
            city = city_tag.get_text(strip=True) if city_tag else None
            full_adres = f"{address} in {city}" if address and city else None

            # Price
            price_tag = obj.select_one("span.element_prijs2")
            price = None
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (Woonoppervlakte)
            area = None
            area_tag = obj.select_one("div.row.Woonoppervlakte .features-info")
            if area_tag:
                area_text = area_tag.get_text()
                area_match = re.search(r"(\d+)\s*m", area_text)
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms (Aantal kamers)
            num_rooms = None
            rooms_tag = obj.select_one("div.row.Aantal_kamers .features-info")
            if rooms_tag:
                rooms_text = rooms_tag.get_text()
                rooms_match = re.search(r"(\d+)", rooms_text)
                num_rooms = int(rooms_match.group(1)) if rooms_match else None

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one("div.status span")
            if status_tag:
                status_text = status_tag.get_text(strip=True).lower()
                if "verkocht" in status_text:
                    available = "Verkocht"
                elif "verhuurd" in status_text:
                    available = "Verhuurd"
                elif "onder bod" in status_text:
                    available = "Onder bod"

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
    url ='https://www.burgerelkerbout.nl/koopwoningen-in-amsterdam'

    html = get_html(url)
    listings = extract_burgerelkerbout_data(html)
    for listing in listings:
        print(listing)
        