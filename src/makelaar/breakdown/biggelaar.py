# %%
from bs4 import BeautifulSoup
import re

def extract_bnv_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.bnv.nl"

    for obj in soup.select("div.object"):
        try:
            # Address
            street = obj.select_one("span.object-street")
            number = obj.select_one("span.object-housenumber")
            addition = obj.select_one("span.object-housenumber-addition")
            city = obj.select_one("span.object-place")
            street_str = f"{street.text.strip()} {number.text.strip()}" if street and number else None
            if addition:
                street_str += f" {addition.text.strip()}"
            full_adres = f"{street_str} in {city.text.strip()}" if street_str and city else None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("div.object-price-sale span.object-price-value")
            if price_tag:
                price_match = re.search(r"€\s*([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = None

            # Area
            area = None
            area_tag = obj.select_one("div.object-feature-woonoppervlakte .object-feature-info")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms – not found in HTML, so set to None (can adjust if you find relevant class)
            num_rooms = None

            # Availability
            status_tag = obj.select_one("div.object-feature-status .object-feature-info")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
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
    url ='https://www.bnv.nl/woningen-koop/'
    html = get_html(url)
    listings = extract_bnv_data(html)
    for listing in listings:
        print(listing)
        