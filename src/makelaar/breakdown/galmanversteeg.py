# %%
from bs4 import BeautifulSoup
import re

def extract_galmanversteeg_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://galmanversteeg.nl"

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

            # Price (either koop or huur)
            price = None
            price_tag = obj.select_one("div.object-price-value")
            if not price_tag:
                price_tag = obj.select_one("div.object-price-rent span.object-price-value")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area — Not available in provided HTML
            area = None

            # Number of rooms — Not available in provided HTML
            num_rooms = None

            # Status
            status_tag = obj.select_one("div.object-status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"
            elif "verhuurd" in status_text:
                available = "Verhuurd"

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
    url ='https://galmanversteeg.nl/woningaanbod/'
    html = get_html(url)
    listings = extract_galmanversteeg_data(html)
    for listing in listings:
        print(listing)

    url_formaat = 'https://galmanversteeg.nl/woningaanbod/?_paged={page}'