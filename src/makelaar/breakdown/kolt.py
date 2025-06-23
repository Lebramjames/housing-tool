# %%
from bs4 import BeautifulSoup
import re

def extract_kolt_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.koltmakelaardij.nl"

    for li in soup.select("li.al2woning"):
        try:
            # URL
            url_tag = li.select_one("a.aanbodEntryLink[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            street_tag = li.select_one("h3.street-address")
            city_tag = li.select_one("span.locality")
            full_adres = f"{street_tag.text.strip()} in {city_tag.text.strip()}" if street_tag and city_tag else None

            # City
            city = city_tag.text.strip() if city_tag else None

            # Price
            price = None
            price_tag = li.select_one("span.kenmerk.koopprijs span.kenmerkValue")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price = float(price_match.group(1).replace(".", "").replace(",", "."))

            # Area
            area = None
            area_tag = li.select_one("span.kenmerk.woonoppervlakte span.kenmerkValue")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = li.select_one("span.kenmerk.aantalkamers span.kenmerkValue")
            if room_tag:
                room_match = re.search(r"(\d+)", room_tag.text.strip())
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            available = "Beschikbaar"
            status_tag = li.select_one("div.spotlight-invisible span.objectstatusbanner")
            if status_tag:
                status_text = status_tag.text.strip().lower()
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
    url = 'https://www.koltmakelaardij.nl/aanbod/woningaanbod/AMSTERDAM/koop/'
    html = get_html(url)
    listings = extract_kolt_data(html)
    for listing in listings:
        print(listing)
    url_format = 'https://www.koltmakelaardij.nl/aanbod/woningaanbod/AMSTERDAM/koop/pagina-{page}/'