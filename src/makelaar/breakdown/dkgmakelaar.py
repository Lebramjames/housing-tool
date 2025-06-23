# %%
from bs4 import BeautifulSoup
import re

def extract_dkg_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.dkgmakelaars.nl"

    for obj in soup.select("li.al4woning"):
        try:
            # URL
            url_tag = obj.select_one("a.aanbodEntryLink")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address and City
            street = obj.select_one("h3.street-address")
            city = obj.select_one("span.locality")
            full_adres = f"{street.text.strip()} in {city.text.strip()}" if street and city else None

            # Price
            price = None
            price_tag = obj.select_one("span.kenmerkValue")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Rooms and Area: Extract from JSON-LD if embedded (or if elsewhere available)
            json_ld_tag = obj.find("script", type="application/ld+json")
            area, num_rooms = None, None
            if json_ld_tag:
                import json
                try:
                    data = json.loads(json_ld_tag.string)
                    # Example parsing if data is as shown in your HTML
                    description = data.get("description", "")
                    area_match = re.search(r"(\d+)\s?m", description.lower())
                    if area_match:
                        area = int(area_match.group(1))
                    room_match = re.search(r"(\d+)\s?kamers?", description.lower())
                    if room_match:
                        num_rooms = int(room_match.group(1))
                except Exception:
                    pass

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one("span.objectstatusbanner")
            if status_tag:
                status_text = status_tag.text.strip().lower()
                if "verkocht" in status_text:
                    available = "Verkocht"
                elif "onder bod" in status_text:
                    available = "Onder bod"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city.text.strip() if city else None,
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
    url = 'https://www.dkgmakelaars.nl/aanbod/woningaanbod/AMSTERDAM/koop-huur/'
    html = get_html(url)
    listings = extract_dkg_data(html)
    for listing in listings:
        print(listing)
        