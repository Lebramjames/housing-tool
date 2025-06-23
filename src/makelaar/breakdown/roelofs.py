# %%
from bs4 import BeautifulSoup
import re

def extract_roelofs_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.roelofsproperties.nl"
    return None

    for item in soup.select("script[type='application/ld+json']"):
        # Use JSON-LD itemListElement for URLs listing
        try:
            data = json.loads(item.string)
            if data.get('@type') == "ItemList":
                for el in data.get("itemListElement", []):
                    url = el.get("url")
                    if url:
                        listings.append({"url": url})
        except:
            pass

    # Fallback: scrape visible elements on page
    for elem in soup.select(".woning, .listing, a[href*='/service-page/']"):
        try:
            url_tag = elem.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Extract address and city from URL or nearby text
            # URL may include street and city slug
            parts = url.split("/")[-1].split("-")
            city = parts[-1] if re.match(r"[a-z]+$", parts[-1]) else None

            raw = elem.get_text(separator=" ").strip()
            address_match = re.search(r"([A-Za-z0-9\s]+\s\d+[A-Za-z]?(?:/\d+)?),?\s*([A-Za-z\s\-]+)", raw)
            if address_match:
                street = address_match.group(1).strip()
                city = city or address_match.group(2).strip()
                full_adres = f"{street} in {city}"
            else:
                full_adres = None

            # Price, area, rooms might appear within elem or require detail page
            price = None
            m = re.search(r"€\s?([\d\.,]+)", raw)
            if m:
                price_str = m.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except:
                    pass

            area = None
            m2 = re.search(r'(\d+)\s*m²|\s*m2', raw)
            if m2:
                area = int(m2.group(1))

            num_rooms = None
            m3 = re.search(r'(\d+)\s*kamer', raw)
            if m3:
                num_rooms = int(m3.group(1))

            # Availability: assume available unless sold/onder bod
            available = "Beschikbaar"
            if re.search(r"verkocht", raw, re.IGNORECASE):
                available = "Verkocht"
            elif re.search(r"onder bod", raw, re.IGNORECASE):
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
            print(listings)
        except Exception:
            continue

    # de-duplicate by URL
    unique = {l['url']: l for l in listings if l.get("url")}
    return list(unique.values())

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://www.roelofsproperties.nl/en/book-online'
    html = get_html(url)
    listings = extract_roelofs_data(html)
    for listing in listings:
        print(listing)
