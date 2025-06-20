# %%
# TODO
from bs4 import BeautifulSoup
import re

def extract_karenlehman_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.karenlehman.nl"

    for obj in soup.select("li.al4woning"):
        try:
            # Address
            street_tag = obj.select_one("h3.street-address")
            postal_tag = obj.select_one("span.postal-code")
            city_tag = obj.select_one("span.locality")

            street = street_tag.text.strip() if street_tag else ""
            postal = postal_tag.text.strip() if postal_tag else ""
            city = city_tag.text.strip() if city_tag else ""
            full_adres = f"{street} in {city} {postal}".strip() if street and city else None

            # URL
            url_tag = obj.select_one("a.aanbodEntryLink[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("span.kenmerk.koopprijs span.kenmerkValue")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = None

            # Area — not shown in this HTML snippet
            area = None

            # Number of rooms — also not shown in snippet
            num_rooms = None

            # Availability
            status_tag = obj.select_one("div.objectstatus span")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
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
    url ='https://www.karenlehman.nl/aanbod/woningaanbod/'
    html = get_html(url)
    # import pyperclip
    # pyperclip.copy(html)
    listings = extract_karenlehman_data(html)
    for listing in listings:
        print(listing)
    url_format ='https://www.karenlehman.nl/aanbod/woningaanbod/pagina-{page}/'