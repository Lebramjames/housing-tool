# %%
from bs4 import BeautifulSoup
import re

def extract_puurmakelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for listing in soup.select("li.listing-card__wrapper"):
        try:
            # Address and City
            title_tag = listing.select_one("h3.listing-card__heading a")
            if not title_tag:
                continue
            address_line = title_tag.text.strip()  # e.g., "Linnaeusstraat 31D, Amsterdam"
            if "," in address_line:
                street, city = map(str.strip, address_line.split(",", 1))
            else:
                street = address_line
                city = None
            full_adres = f"{street} in {city}" if city else street

            # URL
            url = title_tag["href"]

            # Price
            price_tag = listing.select_one(".listing-card__price")
            price = None
            if price_tag:
                price_match = re.search(r"€\s*([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (m²)
            area = None
            area_tag = listing.select_one("span.text:contains('m')")
            if not area_tag:
                area_tag = listing.select_one(".listing-card__icon-item span.text")
            if area_tag:
                area_match = re.search(r"(\d+)\s*m", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            room_tag = listing.select_one("span.text:contains('kamer')")
            num_rooms = None
            if room_tag:
                room_match = re.search(r"(\d+)", room_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            status_tag = listing.select_one("span.listing-card__status")
            available = status_tag.text.strip() if status_tag else "Beschikbaar"

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

# Example usage:
if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://puurmakelaars.nl/woningen/?gad_source=1&gad_campaignid=20153194718&gbraid=0AAAAAD1e9wss0KqOWohlliZEnZGNer5SE&gclid=CjwKCAjw6s7CBhACEiwAuHQckq_xAMoSieEmhRKnHXZT1-Xd-LczE7bWPs_mJikxj7Kh58l9IWZBcRoCMXIQAvD_BwE&_plaatsen=amsterdam'
    html = get_html(url)
    listings = extract_puurmakelaars_data(html)
    for listing in listings:
        print(listing)

        