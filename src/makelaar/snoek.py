# %%
from bs4 import BeautifulSoup
import re

def extract_snoek_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.deherenvansnoek.nl"

    for obj in soup.select("div.property-listing, div.result-item, div.property-result"):  # adjust selector if needed
        try:
            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Full address and city
            address_tag = obj.select_one(".property-address, .result-address, h2, h3")
            full_address_text = address_tag.get_text(strip=True) if address_tag else None

            # Try to split into address and city
            address = None
            city = None
            if full_address_text:
                parts = full_address_text.split(",")
                if len(parts) >= 2:
                    address = parts[0].strip()
                    city = parts[-1].strip()
            full_adres = f"{address} in {city}" if address and city else None

            # Price
            price = None
            price_tag = obj.select_one(".price, .property-price")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.find(string=re.compile(r"Woonoppervlakte", re.I))
            if area_tag and area_tag.parent:
                area_match = re.search(r"(\d+)\s*m", area_tag.parent.get_text())
                area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            num_rooms = None
            room_tag = obj.find(string=re.compile(r"kamers", re.I))
            if room_tag and room_tag.parent:
                room_match = re.search(r"(\d+)", room_tag.parent.get_text())
                num_rooms = int(room_match.group(1)) if room_match else None

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one(".status, .label-status")
            if status_tag:
                status_text = status_tag.get_text(strip=True).lower()
                if "verkocht" in status_text:
                    available = "Verkocht"
                elif "onder bod" in status_text:
                    available = "Onder bod"
                elif "verhuurd" in status_text:
                    available = "Verhuurd"

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
    url ='https://www.deherenvansnoek.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&orderdescending=true'
    html = get_html(url)
    import pyperclip
    pyperclip.copy(html)  # Copy HTML to clipboard for debugging
    listings = extract_snoek_data(html)
    for listing in listings:
        print(listing)
    url_format ='https://www.deherenvansnoek.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&orderdescending=true&skip={page}'