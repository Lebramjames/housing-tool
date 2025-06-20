# %%
from bs4 import BeautifulSoup
import re

def extract_denuyl_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.denuylrealestate.com"

    for obj in soup.select("div.e-loop-item"):
        try:
            # URL and address (street + number)
            title_tag = obj.select_one("div.straat h2 a")
            full_address = title_tag.text.strip() if title_tag else None
            url = title_tag["href"] if title_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # City
            city_tag = obj.select_one("div.elementor-element-70fea56 h3 a")
            city = city_tag.text.strip() if city_tag else None

            # Price
            price_tag = obj.select_one("div.vraagprijs")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = float(price_match.group(1).replace(".", "").replace(",", ".")) if price_match else None

            # Area
            area_tag = obj.select("li.elementor-icon-list-item span.elementor-icon-list-text")
            area = None
            for tag in area_tag:
                if "m2" in tag.text.lower():
                    area_match = re.search(r"(\d+)\s*m2", tag.text)
                    area = int(area_match.group(1)) if area_match else None
                    break

            # Rooms
            num_rooms = None
            for tag in area_tag:
                if re.search(r"\d+\s*$", tag.text.strip()):
                    try:
                        num_rooms = int(tag.text.strip())
                        break
                    except ValueError:
                        continue

            # Availability
            container_class = obj.select_one("div.onder-bod-js")
            available = "Onder bod" if container_class else "Beschikbaar"

            listings.append({
                "full_adres": full_address,
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
    url = 'https://www.denuylrealestate.com/aanbod/'
    html = get_html(url)
    listings = extract_denuyl_data(html)
    for listing in listings:
        print(listing)