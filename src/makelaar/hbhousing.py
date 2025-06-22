# %%
from bs4 import BeautifulSoup
import re

def extract_hbhousing_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.hbhousing.nl"

    for obj in soup.select("article.woning"):
        try:
            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address (from URL or last part of href)
            full_adres = url.strip("/").split("/")[-1].replace("-", " ").title() if url else None

            # City (part of the URL)
            parts = url.strip("/").split("/") if url else []
            city = parts[4] if len(parts) > 4 else None
            if city:
                city = city.replace("-", " ").title()

            # Price – from within the listing content if visible (not shown in HTML snippet)
            price = None
            price_tag = obj.select_one(".price")  # adjust selector if needed
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area – from label or description (not shown in HTML snippet)
            area = None
            area_tag = obj.select_one(".area")  # adjust selector if needed
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Rooms – from label or description (not shown in HTML snippet)
            num_rooms = None
            room_tag = obj.select_one(".rooms")  # adjust selector if needed
            if room_tag:
                room_match = re.search(r"(\d+)\s+kamer", room_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability – from class
            status_classes = obj.get("class", [])
            available = "Beschikbaar"
            if any("sold" in c.lower() for c in status_classes):
                available = "Verkocht"
            elif any("vov" in c.lower() or "onder-bod" in c.lower() for c in status_classes):
                available = "Verkocht onder voorbehoud"

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
    url ='https://www.hbhousing.nl/aanbod/koop/'
    html = get_html(url)
    listings = extract_hbhousing_data(html)
    for listing in listings:
        print(listing)
        