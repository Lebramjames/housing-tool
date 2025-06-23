#%%
from bs4 import BeautifulSoup
import re

def extract_parkerwilliams_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://parkerwilliams.nl"

    for obj in soup.select("article.objectcontainer"):
        try:
            # URL
            url_tag = obj.select_one("a.img-container")
            url = url_tag["href"] if url_tag and url_tag.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address parts
            street_tag = obj.select_one("h3.obj_address span.street")
            zipcode_tag = obj.select_one("h3.obj_address span.zipcode")
            city_tag = obj.select_one("h3.obj_address span.locality")

            street = street_tag.get_text(strip=True) if street_tag else None
            zipcode = zipcode_tag.get_text(strip=True) if zipcode_tag else None
            city = city_tag.get_text(strip=True) if city_tag else None

            full_adres = f"{street}, {zipcode} {city}" if street and zipcode and city else None

            # Price
            price_tag = obj.select_one("span.obj_price")
            price = None
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                match = re.search(r"€\s?([\d\.,]+)", price_text)
                if match:
                    price_str = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (in m²)
            area_tag = obj.select_one("span.object_label.object_sqfeet span.number")
            area = None
            if area_tag:
                area_text = area_tag.get_text(strip=True)
                area_match = re.search(r"(\d+)", area_text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            rooms_tag = obj.select_one("span.object_label.object_rooms span.number")
            num_rooms = None
            if rooms_tag:
                try:
                    num_rooms = int(rooms_tag.get_text(strip=True))
                except ValueError:
                    pass

            # Availability
            status_tag = obj.select_one("span.object_status")
            status_text = status_tag.get_text(strip=True).lower() if status_tag else ""
            if "under offer" in status_text:
                available = "Onder bod"
            elif "sold" in status_text:
                available = "Verkocht"
            else:
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
    url = "https://parkerwilliams.nl/residential-listings/sale?moveunavailablelistingstothebottom=true&orderby=10&orderdescending=true&pricerange.maxprice=500000"
    
    html = get_html(url)
    listings = extract_parkerwilliams_data(html)
    for listing in listings:
        print(listing)






