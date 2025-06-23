# %%
from bs4 import BeautifulSoup
import re

def extract_deruyter_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://deruytermakelaardij.nl"

    for obj in soup.select("div.wpl_prp_cont"):
        try:
            # URL and full address from title and link
            title_tag = obj.select_one("a.view_detail[title]")
            url_tag = obj.select_one("a.view_detail[href]")
            full_adres = title_tag["title"].strip() if title_tag else None
            city = None
            if full_adres and "," in full_adres:
                parts = full_adres.split(",")
                if len(parts) > 1:
                    city = parts[-1].strip()

            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("div.price_box span")
            if price_tag:
                price_text = price_tag.text.strip()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area
            area = None
            area_tag = obj.select_one("div.built_up_area")
            if area_tag:
                area_match = re.search(r"(\d+)", area_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = obj.select_one("div.room span.value")
            if room_tag and room_tag.text.isdigit():
                num_rooms = int(room_tag.text)

            # Status (Beschikbaar, Onder bod, Verkocht)
            available = "Beschikbaar"
            status_tag = obj.select_one("div.wpl-listing-tags-wp div")
            if status_tag:
                status_text = status_tag.text.strip().lower()
                if "onder bod" in status_text:
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
    url = 'https://deruytermakelaardij.nl/woningaanbod/'
    html = get_html(url)
    listings = extract_deruyter_data(html)
    for listing in listings:
        print(listing)
        