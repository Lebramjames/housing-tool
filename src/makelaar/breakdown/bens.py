# %%
from bs4 import BeautifulSoup
import re

def extract_bensmakelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.bensmakelaars.nl"

    for li in soup.select("li.aanbodEntry"):
        try:
            # Address elements
            street_tag = li.select_one("h3.street-address")
            zip_tag = li.select_one("span.postal-code")
            city_tag = li.select_one("span.locality")
            
            street = street_tag.get_text(strip=True) if street_tag else ""
            zip_code = zip_tag.get_text(strip=True) if zip_tag else ""
            city = city_tag.get_text(strip=True) if city_tag else ""
            full_adres = f"{street} in {city} {zip_code}".strip()

            # URL
            url_tag = li.select_one("a.aanbodEntryLink[href]")
            relative_url = url_tag["href"] if url_tag else None
            url = f"{base_url}{relative_url}" if relative_url else None

            # Price
            price_text = li.select_one("span.kenmerkValue")
            price = None
            if price_text:
                price_match = re.search(r"€\s*([\d\.,]+)", price_text.get_text())
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = None

            # Availability (Nieuw, Verkocht, Onder bod, etc.)
            status_banner = li.select_one("span.objectstatusbanner")
            available = status_banner.get_text(strip=True) if status_banner else "Beschikbaar"

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": None,         # Not found in provided snippet
                "num_rooms": None,    # Not found in provided snippet
                "available": available
            })
        except Exception as e:
            continue

    return listings

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = "https://www.bensmakelaars.nl/aanbod/woningaanbod/beschikbaar/50+woonopp/appartement/"
    html = get_html(url)
    listings = extract_bensmakelaars_data(html)
    for listing in listings:
        print(listing)

    url_format = f'https://www.bensmakelaars.nl/aanbod/woningaanbod/pagina-{page}/'