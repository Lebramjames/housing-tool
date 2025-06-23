# %%
from bs4 import BeautifulSoup
import re

def extract_bbdb_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.bbdb-makelaars.nl"

    for li in soup.select("li.al2woning"):
        try:
            # URL
            a_tag = li.select_one("a.aanbodEntryLink[href]")
            url = a_tag["href"] if a_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Full address
            street_tag = li.select_one("h3.street-address")
            city_tag = li.select_one("span.locality")
            full_adres = f"{street_tag.text.strip()} in {city_tag.text.strip()}" if street_tag and city_tag else None

            # City
            city = city_tag.text.strip() if city_tag else None

            # Price
            price = None
            price_tag = li.select_one("span.kenmerk.koopprijs .kenmerkValue")
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
            area_tag = li.select_one("span.kenmerk.woonoppervlakte .kenmerkValue")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            num_rooms = None
            rooms_tag = li.select_one("span.kenmerk.aantalkamers .kenmerkValue")
            if rooms_tag:
                rooms_match = re.search(r"(\d+)", rooms_tag.text)
                num_rooms = int(rooms_match.group(1)) if rooms_match else None

            # Availability
            status_banner = li.select_one("span.objectstatusbanner")
            status_text = status_banner.text.strip().lower() if status_banner else ""
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
    url = 'https://www.bbdb-makelaars.nl/aanbod/woningaanbod/koop/'
    html = get_html(url)
    import pyperclip
    pyperclip.copy(html)  # Copy HTML to clipboard for debugging
    listings = extract_bbdb_data(html)
    for listing in listings:
        print(listing)