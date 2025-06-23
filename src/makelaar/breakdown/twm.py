# %%
from bs4 import BeautifulSoup
import re

def extract_twm_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.twm-makelaardij.nl"

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
            price_tag = obj.select_one("div.object-price-sale span.object-price-value")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = None
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Area
            area_tag = obj.select_one("div.object-feature-woonoppervlakte .object-feature-info")
            area_text = area_tag.get_text(strip=True) if area_tag else ""
            area_match = re.search(r"(\d+)\s*m", area_text)
            area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            room_tag = obj.select_one("div.object-feature-aantalkamers .object-feature-info")
            room_text = room_tag.get_text(strip=True) if room_tag else ""
            room_match = re.search(r"(\d+)", room_text)
            num_rooms = int(room_match.group(1)) if room_match else None

            # Status
            status_tag = obj.select_one("div.object")
            status_classes = status_tag.get("class", []) if status_tag else []
            status_text = " ".join(status_classes).lower()
            available = "Beschikbaar"
            if "verkocht" in status_text:
                available = "Verkocht"
            elif "onder-bod" in status_text:
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

    url ='https://www.twm-makelaardij.nl/koopwoningen/?_plaatsen=amsterdam&_prijs_tot=1-500000'
    html = get_html(url)
    listings = extract_twm_data(html)
    for listing in listings:
        print(listing)


    # url_format = 'https://www.twm-makelaardij.nl/koopwoningen/?_plaatsen=amsterdam&_prijs_tot=1-500000&_paged={page}'
