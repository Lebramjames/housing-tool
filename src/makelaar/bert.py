# %%%
from bs4 import BeautifulSoup
import re

def extract_makelaarbert_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://makelaarbert.nu"

    for obj in soup.select("article.woning"):
        try:
            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            address_tag = obj.select_one("div.woning-address h4")
            city_tag = obj.select_one("div.woning-address p")
            street = address_tag.text.strip() if address_tag else None
            city_line = city_tag.text.strip() if city_tag else ""
            city_match = re.search(r"\d{4}\s?[A-Z]{2}\s+(.*)", city_line)
            city = city_match.group(1).strip() if city_match else None
            full_adres = f"{street} in {city}" if street and city else None

            # Price
            price_tag = obj.select_one("div.woning-price")
            price = None
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area (not available in this view)
            area = None

            # Number of rooms
            room_tag = obj.select_one("li.kamers strong")
            num_rooms = int(room_tag.text.strip()) if room_tag and room_tag.text.strip().isdigit() else None

            # Availability: infer from price (if "p/m" then it's for rent)
            available = "Beschikbaar"
            if price_tag and "verhuurd" in price_tag.text.lower():
                available = "Verhuurd"
            elif price_tag and "verkocht" in price_tag.text.lower():
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
    url = 'https://makelaarbert.nu/aanbod/'
    html = get_html(url)
    listings = extract_makelaarbert_data(html)
    for listing in listings:
        print(listing)