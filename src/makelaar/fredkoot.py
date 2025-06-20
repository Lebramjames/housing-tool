# %%
from bs4 import BeautifulSoup
import re

def extract_fredkoot_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.fredkootmakelaardij.nl"

    for li in soup.select("li.al2woning.aanbodEntry"):
        try:
            # URL
            url_tag = li.select_one("a.aanbodEntryLink[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address & city
            street_tag = li.select_one("h3.street-address")
            postal_tag = li.select_one("span.postal-code")
            city_tag = li.select_one("span.locality")

            street = street_tag.get_text(strip=True) if street_tag else ""
            postal = postal_tag.get_text(strip=True) if postal_tag else ""
            city = city_tag.get_text(strip=True) if city_tag else ""
            full_adres = f"{street} in {city} {postal}".strip() if street and city else None

            # Price
            price_tag = li.select_one("span.koopprijs span.kenmerkValue")
            price = None
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                match = re.search(r"€\s?([\d\.,]+)", price_text)
                if match:
                    price_str = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area_tag = li.select_one("span.woonoppervlakte span.kenmerkValue")
            area = None
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.get_text())
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            rooms_tag = li.select_one("span.aantalkamers span.kenmerkValue")
            num_rooms = None
            if rooms_tag:
                rooms_match = re.search(r"(\d+)", rooms_tag.get_text())
                if rooms_match:
                    num_rooms = int(rooms_match.group(1))

            # Availability
            status_tag = li.select_one("span.objectstatusbanner")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
            available = "Beschikbaar"
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
    url ='https://www.fredkootmakelaardij.nl/aanbod/woningaanbod/AMSTERDAM/koop/'
    html = get_html(url)
    import pyperclip
    pyperclip.copy(html)
    listings = extract_fredkoot_data(html)
    for listing in listings:
        print(listing)
    url_format ='https://www.fredkootmakelaardij.nl/aanbod/woningaanbod/AMSTERDAM/koop/pagina-{page}/'