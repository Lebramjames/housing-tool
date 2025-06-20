# %%
from bs4 import BeautifulSoup
import re

def extract_smitenheinen_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.smitenheinen.nl"

    for obj in soup.select("article"):
        try:
            # Street + number
            street_tag = obj.select_one("h4.custom-address-text a")
            street = street_tag.get_text(strip=True) if street_tag else None

            # City
            city_tag = obj.select_one("span.custom-postcode-text")
            city_text = city_tag.get_text(strip=True) if city_tag else None
            city = None
            if city_text and re.search(r"\d{4}\s?[A-Z]{2}\s+(.+)", city_text):
                city = re.search(r"\d{4}\s?[A-Z]{2}\s+(.+)", city_text).group(1).strip()

            full_adres = f"{street} in {city}" if street and city else None

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("div.price")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except:
                        pass

            # Area (e.g. 55 m²)
            area = None
            area_tag = obj.find("img", alt=re.compile(r"\d+\s?m²", re.IGNORECASE))
            if area_tag and area_tag.has_attr("alt"):
                area_match = re.search(r"(\d+)\s?m²", area_tag["alt"])
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms (usually number right after "slaapkamers")
            num_rooms = None
            room_tag = obj.find("img", alt=re.compile(r"\d+\s+slaapkamers", re.IGNORECASE))
            if room_tag and room_tag.has_attr("alt"):
                room_match = re.search(r"(\d+)\s+slaapkamers", room_tag["alt"])
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Status (default: Beschikbaar)
            available = "Beschikbaar"
            status_tag = obj.select_one("span.status")
            if status_tag:
                status_text = status_tag.text.lower()
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
    url = 'https://www.smitenheinen.nl/woningaanbod/koop?street_postcode_city=AMSTERDAM&status=&purchase_price_from=&purchase_price_till=500000&construction_year_from=&construction_year_till=&living_area_from=&living_area_till=#objects'
    html = get_html(url)
    listings = extract_smitenheinen_data(html)
    for listing in listings:
        print(listing)
        