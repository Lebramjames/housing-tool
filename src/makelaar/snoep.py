# %%
from bs4 import BeautifulSoup
import re

def extract_snoep_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.snoepmakelaardij.nl"

    for obj in soup.select("div.elementor.elementor-597.e-loop-item"):
        try:
            # URL
            url_tag = obj.select_one("a.elementor-element[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            street_tag = obj.select_one("h1.elementor-heading-title")
            city_tag = obj.select_one("div.elementor-element-2888ca4 h2.elementor-heading-title")
            street = street_tag.get_text(strip=True) if street_tag else ""
            city = city_tag.get_text(strip=True).replace("-", "").strip() if city_tag else ""
            full_adres = f"{street} in {city}" if street and city else None

            # Price
            price_tag = obj.select_one("div.elementor-element-41478d2 h2.elementor-heading-title")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = None
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Status
            status_tag = obj.select_one("div.elementor-element-395b935 h2.elementor-heading-title")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"

            # Area and rooms not present in the provided HTML
            area = None
            num_rooms = None

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
    url = "https://www.snoepmakelaardij.nl/aanbod/"
    html = get_html(url)
    listings = extract_snoep_data(html)
    for listing in listings:
        print(listing)
        
    