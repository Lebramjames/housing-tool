# %%

from bs4 import BeautifulSoup
import re

def extract_020makelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.020makelaars.nl"

    for obj in soup.select("div.relative.flex.flex-col.bg-white"):
        try:
            # Address: city and full_adres
            city_tag = obj.select_one("h4.text-secondary")
            street_tag = obj.select_one("h3.h3")
            city = city_tag.get_text(strip=True) if city_tag else None
            full_adres = street_tag.get_text(strip=True) + f" in {city}" if street_tag and city else None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("p.text-bodysmall")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (not clearly visible in this snippet, so set to None)
            area = None

            # Number of rooms (not clearly visible in this snippet, so set to None)
            num_rooms = None

            # Availability — based on label like "Nieuw!"
            available = "Beschikbaar"
            status_tag = obj.select_one("div.bg-secondary")
            if status_tag:
                status_text = status_tag.get_text(strip=True).lower()
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
    url ='https://www.020makelaars.nl/aanbod?where%5Band%5D%5Bweb.salesPrice%5D%5Bless_than_equal%5D=500000&where%5Bor%5D%5BisSales%5D%5Bequals%5D=true'
    html = get_html(url)
    listings = extract_020makelaars_data(html)
    for listing in listings:
        print(listing)
        