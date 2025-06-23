# %%
from bs4 import BeautifulSoup
import re

def extract_edens_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.edensmakelaardij.nl"

    for obj in soup.select("li.al2woning.aanbodEntry"):
        try:
            # URL
            link_tag = obj.select_one("a.aanbodEntryLink[href]")
            url = link_tag["href"] if link_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            street_tag = obj.select_one("h3.street-address")
            zip_tag = obj.select_one("span.postal-code")
            city_tag = obj.select_one("span.locality")
            street = street_tag.text.strip() if street_tag else ""
            zip_code = zip_tag.text.strip() if zip_tag else ""
            city = city_tag.text.strip() if city_tag else ""
            full_adres = f"{street} in {city} {zip_code}" if street and city else None

            # Price
            price_tag = obj.select_one("span.koopprijs .kenmerkValue")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = None
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Area (woonoppervlakte)
            area_tag = obj.select_one("span.woonoppervlakte .kenmerkValue")
            area_text = area_tag.get_text(strip=True) if area_tag else ""
            area_match = re.search(r"(\d+)\s*m", area_text)
            area = int(area_match.group(1)) if area_match else None

            # Number of rooms (Aantal kamers)
            room_tag = obj.select_one("span.aantalkamers .kenmerkValue")
            room_text = room_tag.get_text(strip=True) if room_tag else ""
            room_match = re.search(r"(\d+)", room_text)
            num_rooms = int(room_match.group(1)) if room_match else None

            # Availability
            status_banner = obj.select_one("span.objectstatusbanner")
            status_text = status_banner.get_text(strip=True).lower() if status_banner else ""
            available = "Beschikbaar"
            if "verkocht" in status_text:
                available = "Verkocht"
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
    url = 'https://www.edensmakelaardij.nl/aanbod/woningaanbod/AMSTERDAM/koop-huur/'
    html = get_html(url)
    listings = extract_edens_data(html)
    for listing in listings:
        print(listing)
    # url_format = 'https://www.edensmakelaardij.nl/aanbod/woningaanbod/AMSTERDAM/koop-huur/pagina-{page}/