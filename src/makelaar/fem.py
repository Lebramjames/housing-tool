# %%
from bs4 import BeautifulSoup
import re

def extract_fem_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.femmakelaars.nl"

    for obj in soup.select("div.blok"):
        try:
            # Address extraction (header tags often contain it)
            full_adres = None
            for tag in obj.select("h2, h3, h4"):
                txt = tag.get_text(strip=True)
                if re.search(r"\d{1,4}\s?[A-Z]?[a-z]*", txt):
                    full_adres = txt
                    break

            city = "Amsterdam"
            if full_adres and "," in full_adres:
                parts = full_adres.split(",")
                full_adres = parts[0].strip()
                city = parts[-1].strip()

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_texts = obj.find_all(string=re.compile(r"€"))
            for price_str in price_texts:
                match = re.search(r"€\s?([\d\.,]+)", price_str)
                if match:
                    raw = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(raw)
                        break
                    except ValueError:
                        continue

            # Area
            area = None
            area_texts = obj.find_all(string=re.compile(r"\d+\s*m²"))
            for area_str in area_texts:
                match = re.search(r"(\d+)\s*m²", area_str)
                if match:
                    area = int(match.group(1))
                    break

            # Number of rooms
            num_rooms = None
            room_texts = obj.find_all(string=re.compile(r"\d+\s+kamers?"))
            for room_str in room_texts:
                match = re.search(r"(\d+)\s+kamers?", room_str)
                if match:
                    num_rooms = int(match.group(1))
                    break

            # Availability
            status_tag = obj.select_one("div.status, div.object-status")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder bod" in status_text:
                available = "Onder bod"
            elif "verkocht" in status_text:
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
    url = 'https://www.femmakelaars.nl/aanbod/woningaanbod/AMSTERDAM/-500000/koop/'
    html = get_html(url)
    listings = extract_fem_data(html)
    for listing in listings:
        print(listing)