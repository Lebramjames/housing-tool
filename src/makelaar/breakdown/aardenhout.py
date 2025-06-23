# %%
from bs4 import BeautifulSoup
import re

def extract_aardenhout_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://aardenhoutmakelaardij.nl"

    for obj in soup.select("li.portfolio-item"):
        try:
            # URL
            url_tag = obj.select_one("a.link-to-post")
            url = url_tag["href"].strip() if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Full address (taken from title)
            title_tag = obj.select_one("h3.portfolio-item-title a")
            full_adres = title_tag.get_text(strip=True) if title_tag else None

            # City is inferred from address suffix or defaulted if not specified
            city = None
            if full_adres:
                city_match = re.search(r"\b(\w+)$", full_adres.split()[-1])
                city = city_match.group(1) if city_match else None

            # Price
            price = None
            price_tag = obj.select_one("li.price b")
            if price_tag:
                price_text = price_tag.get_text(strip=True).lower()
                match = re.search(r"€\s?([\d\.,]+)", price_text)
                if match:
                    price_str = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (woonoppervlak)
            area = None
            desc_text = obj.select_one("div.portfolio-item-excerpt")
            if desc_text:
                area_match = re.search(r"woonoppervlak\s*(\d+)\s*m", desc_text.get_text().lower())
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms (bedrooms or more general)
            num_rooms = None
            room_match = re.findall(r"(\w+)\s*slaapkamer", desc_text.get_text().lower()) if desc_text else []
            if room_match:
                try:
                    # Try to extract numeric from word
                    num_rooms = sum([int(re.search(r"\d+", r).group()) for r in room_match if re.search(r"\d+", r)])
                except Exception:
                    num_rooms = len(room_match)  # fallback: count number of mentions

            # Availability
            available = "Beschikbaar"
            if price_tag:
                status_text = price_tag.get_text(strip=True).lower()
                if "verkocht onder voorbehoud" in status_text:
                    available = "Verkocht onder voorbehoud"
                elif "onder bod" in status_text:
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
    url = 'https://aardenhoutmakelaardij.nl/aanbod/'
    html = get_html(url)
    listings = extract_aardenhout_data(html)
    for listing in listings:
        print(listing)
        