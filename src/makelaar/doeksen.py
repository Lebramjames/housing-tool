# %%
from bs4 import BeautifulSoup
import re

def extract_doeksenklein_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.doeksenklein.nl"

    for obj in soup.select("div.object"):
        try:
            # Address
            street_tag = obj.select_one("span.adres")
            city_tag = obj.select_one("span.plaatsnaam")
            full_adres = f"{street_tag.text.strip()} in {city_tag.text.strip()}" if street_tag and city_tag else None
            city = city_tag.text.strip() if city_tag else None

            # URL
            url_tag = obj.select_one("a.adreslink[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price from hidden input (more reliable than div)
            input_tag = obj.find("input", {"type": "hidden", "id": re.compile(r"^mgmMarker")})
            price = None
            if input_tag:
                value = input_tag.get("value", "")
                match = re.search(r"~(\d{5,7})~k\.k\.~", value)
                if match:
                    try:
                        price = float(match.group(1))
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("div.row.Woonoppervlakte .features-info")
            if area_tag:
                match = re.search(r"(\d+)\s*m", area_tag.text)
                area = int(match.group(1)) if match else None

            # Number of rooms
            num_rooms = None
            rooms_tag = obj.select_one("div.row.Aantal_kamers .features-info")
            if rooms_tag:
                match = re.search(r"(\d+)", rooms_tag.text)
                num_rooms = int(match.group(1)) if match else None

            # Status
            status_tag = obj.select_one("div.status span, div.status-text span")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"
            else:
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
    url = 'https://www.doeksenklein.nl/aanbod'
    html = get_html(url)
    listings = extract_doeksenklein_data(html)
    for listing in listings:
        print(listing)
        