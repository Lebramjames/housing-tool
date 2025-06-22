# %%
from bs4 import BeautifulSoup
import re

def extract_jamakelaardij_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://jamakelaardij.nl"

    for obj in soup.select("div.card-overview"):
        try:
            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Full address (from title + city)
            title_tag = obj.select_one("h5 a")
            address = title_tag.text.strip() if title_tag else None

            meta = obj.select_one("div.overview-meta")
            city = None
            if meta:
                meta_text = meta.get_text(separator="|").strip().split("|")
                if len(meta_text) > 1:
                    city = meta_text[-1].strip()
            full_adres = f"{address} in {city}" if address and city else None

            # Price
            price = None
            price_tag = obj.select_one("div.price span")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area and num_rooms are not in the HTML snippet provided
            area = None
            num_rooms = None

            # Available (assumed all listed as available unless otherwise specified)
            available = "Beschikbaar"

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
    url = 'https://jamakelaardij.nl/woningen/'
    html = get_html(url)
    listings = extract_jamakelaardij_data(html)
    for listing in listings:
        print(listing)
            