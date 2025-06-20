# %%
from bs4 import BeautifulSoup
import re

def extract_addmakelaardij_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://www.addmakelaardij.nl"
    listings = []

    for obj in soup.select("div.object"):
        try:
            # URL and full address
            link_tag = obj.select_one("a.sys-property-link.object_header")
            url = link_tag["href"] if link_tag else None
            if url and not url.startswith("http"):
                url = base_url + url
            h2 = link_tag.select_one("h2") if link_tag else None
            full_adres = h2.text.strip().split(":")[-1].strip() if h2 else None

            # Extract city from the address (last word after last comma)
            city = None
            if full_adres and "," in full_adres:
                parts = full_adres.split(",")
                city = parts[-1].strip().split()[-1] if len(parts) >= 2 else None

            # Price
            price_tag = obj.select_one("span.object_price")
            price = None
            if price_tag:
                match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if match:
                    price_str = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("span[title='Woonoppervlakte']")
            if area_tag:
                area_match = re.search(r"(\d+)", area_tag.text.replace("\xa0", ""))
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("span.object_label.object_rooms span")
            if room_tag and room_tag.text.isdigit():
                num_rooms = int(room_tag.text)

            # Status
            status_tag = obj.select_one("span.object_status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "onder voorbehoud" in status_text:
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
    url ='https://www.addmakelaardij.nl/woningaanbod/koop?pricerange.maxprice=500000'
    html = get_html(url)
    listings = extract_addmakelaardij_data(html)
    for listing in listings:
        print(listing)
        