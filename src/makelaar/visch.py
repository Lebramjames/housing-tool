# %%
from bs4 import BeautifulSoup
import re

def extract_visch_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.visch-vanzeggelaar.nl"

    for article in soup.select("article.objectcontainer"):
        try:
            # URL and Address
            a_tag = article.select_one("h3.obj_address a[href]")
            url = a_tag["href"] if a_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            street = article.select_one("span.street")
            city_tag = article.select_one("span.locality")
            postcode = article.select_one("span.zipcode")

            full_adres = None
            city = city_tag.text.strip() if city_tag else None
            if street and postcode and city:
                full_adres = f"{street.text.strip()} {postcode.text.strip()} {city}"

            # Price
            price = None
            price_tag = article.select_one("span.obj_price")
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
            area_tag = article.select_one("span.object_label.object_sqfeet span.number")
            if area_tag:
                area_text = area_tag.get_text(strip=True)
                match = re.search(r"(\d+)", area_text)
                if match:
                    area = int(match.group(1))

            # Number of rooms
            num_rooms = None
            rooms_tag = article.select_one("span.object_label.object_rooms span.number")
            if rooms_tag:
                try:
                    num_rooms = int(rooms_tag.text.strip())
                except ValueError:
                    pass

            # Status
            status_tag = article.select_one("span.object_status")
            status_text = status_tag.text.lower().strip() if status_tag else ""
            available = "Beschikbaar"
            if "verkocht" in status_text:
                available = "Verkocht"
            elif "onder bod" in status_text:
                available = "Onder bod"
            elif "nieuw" in status_text:
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
    url = 'https://www.visch-vanzeggelaar.nl/woningaanbod/koop/amsterdam?locationofinterest=Amsterdam&moveunavailablelistingstothebottom=true&pricerange.maxprice=500000'
    html = get_html(url)
    listings = extract_visch_data(html)
    for listing in listings:
        print(listing)
        