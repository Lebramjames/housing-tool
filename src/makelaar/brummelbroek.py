# %%
from bs4 import BeautifulSoup
import re

def extract_brummelenbeuk_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://brummelenbeuk.nl"

    for woning in soup.select("a.woning"):
        try:
            # URL
            url = woning.get("href")
            if url and not url.startswith("http"):
                url = base_url + url

            # Full address
            h4 = woning.select_one("h4")
            full_adres = h4.get_text(strip=True) if h4 else None

            # City
            city = None
            if full_adres and "–" in full_adres:
                city = full_adres.split("–")[0].strip()

            # Price
            price = None
            price_tag = woning.select_one("div.price dd")
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                match = re.search(r"€\s?([\d\.,]+)", price_text)
                if match:
                    price_str = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = woning.select_one("div.oppervlakte dd")
            if area_tag:
                area_text = area_tag.get_text(strip=True)
                match = re.search(r"(\d+)\s*m", area_text)
                if match:
                    area = int(match.group(1))

            # Availability
            available = "Onbekend"
            status_tag = woning.select_one("div.status dd")
            if status_tag:
                status_text = status_tag.get_text(strip=True).lower()
                if "beschikbaar" in status_text:
                    available = "Beschikbaar"
                elif "onder bod" in status_text:
                    available = "Onder bod"
                elif "verkocht" in status_text:
                    available = "Verkocht"
                elif "ingetrokken" in status_text:
                    available = "Ingetrokken"

            # Number of rooms not listed, set to None
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
    url = 'https://brummelenbeuk.nl/aanbod/te-koop/'
    html = get_html(url)
    listings = extract_brummelenbeuk_data(html)
    for listing in listings:
        print(listing)