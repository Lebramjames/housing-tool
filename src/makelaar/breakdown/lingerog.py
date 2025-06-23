# %%
from bs4 import BeautifulSoup
import re

def extract_lingerog_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.lingerog.com"

    for obj in soup.select("div.realworks--item"):
        try:
            # URL
            link_tag = obj.select_one("a.realworks--item-inner")
            url = link_tag["href"] if link_tag and "href" in link_tag.attrs else None

            # Address
            title_tag = obj.select_one("h2.realworks--color-white")
            full_adres = title_tag.text.strip() if title_tag else None

            # City
            city = None
            if full_adres and "," in full_adres:
                parts = full_adres.split(",")
                city = parts[-1].strip()

            # Price
            price = None
            price_tag = obj.select_one("div.h1")
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
            info_tag = obj.select_one("div.realworks--info")
            if info_tag:
                area_match = re.search(r"(\d+)\s*m", info_tag.text)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            if info_tag:
                room_match = re.search(r"(\d+)\s+slaapkamer", info_tag.text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Status
            status_tag = obj.select_one("div.realworks--item-status")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar"
            if "verkocht" in status_text:
                available = "Verkocht"
            elif "onder bod" in status_text:
                available = "Onder bod"
            elif "verhuurd" in status_text:
                available = "Verhuurd"

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
    url ='https://www.lingerog.com/woningen/koop/'
    html = get_html(url)
    listings = extract_lingerog_data(html)
    for listing in listings:
        print(listing)

    # normal

    url_format ='https://www.lingerog.com/woningen/koop/#page/{page};q1bKL0pJLUqqVLKCsKwSi5N1CkqTcjKTE0syU1MSS0pzQWJKOkoZpaVF-WnZ-fkFQMVgqhYA"'