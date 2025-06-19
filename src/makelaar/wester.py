from bs4 import BeautifulSoup
import re

def extract_wester_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://westermakelaars.nl"

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

            # Price (improve robustness)
            price = None
            price_tags = obj.select("div.object-price")
            for tag in price_tags:
                price_text = tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                        break
                    except ValueError:
                        logging.warning(f"Could not convert price '{price_str}' to float.")

            # Area
            area_tag = obj.select_one("div.object-feature-woonoppervlakte")
            area_text = area_tag.get_text() if area_tag else ""
            area_match = re.search(r"(\d+)\s*m", area_text)
            area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            room_tag = obj.select_one("div.object-feature-aantalkamers")
            room_text = room_tag.get_text() if room_tag else ""
            room_match = re.search(r"(\d+)\s+kamer", room_text)
            num_rooms = int(room_match.group(1)) if room_match else None

            # Status
            status_tag = obj.select_one("div.object-status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
                available = "Verkocht"

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

    return listing