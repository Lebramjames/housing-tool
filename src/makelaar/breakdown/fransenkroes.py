# %%
from bs4 import BeautifulSoup
import re

def extract_fransenkroes_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://fransenkroes.nl"

    for card in soup.select("div.card"):
        try:
            # Address
            street_tag = card.select_one("h3.card-title")
            city_tag = card.select_one("h6.card-subtitle")
            street = street_tag.get_text(strip=True) if street_tag else ""
            city_text = city_tag.get_text(strip=True) if city_tag else ""
            city_match = re.search(r"\d{4}\s*[A-Z]{2},\s*(.+)", city_text)
            city = city_match.group(1).strip() if city_match else ""
            full_adres = f"{street} in {city}" if street and city else None

            # URL
            url_tag = card.select_one("a.stretched-link")
            url = url_tag["href"] if url_tag and url_tag.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price_tag = card.select_one("h4.card-price-tag")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s*([\d\.,]+)", price_text)
            price = None
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Area
            area = None
            for li in card.select("ul li"):
                if "icon-surface" in li.get("class", []) or "icon-surface" in str(li):
                    area_match = re.search(r"(\d+)\s*m", li.get_text())
                    if area_match:
                        area = int(area_match.group(1))
                        break

            # Number of rooms
            num_rooms = None
            for li in card.select("ul li"):
                if "icon-rooms" in li.get("class", []) or "icon-rooms" in str(li):
                    room_match = re.search(r"(\d+)", li.get_text())
                    if room_match:
                        num_rooms = int(room_match.group(1))
                        break

            # Status
            available = "Beschikbaar"  # All are shown as "Nieuw" by default; override if needed

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
    url = 'https://fransenkroes.nl/aanbod/?keyword=fransen%20kroes%20makelaars&gad_source=1&gad_campaignid=1466314782&gbraid=0AAAAADG4lereb4JqTi7TnCkSa2d5Pj_Gk&gclid=CjwKCAjw6s7CBhACEiwAuHQcknjfeHUqDe7NMM_nV-zDYRTBpDYuAO43bxw8uHDN1KO8Nwc64BEb5RoC5gYQAvD_BwE'
    html = get_html(url)
    listings = extract_fransenkroes_data(html)
    for listing in listings:
        print(listing)