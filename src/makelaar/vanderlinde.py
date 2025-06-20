# %%
from bs4 import BeautifulSoup
import re

def extract_vanderlinden_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.vanderlinden.nl"

    for obj in soup.select("div.woninginfo"):
        try:
            # Address (street + number)
            address_tag = obj.select_one("div > strong")
            street = address_tag.get_text(strip=True) if address_tag else None

            # City
            city_tag = obj.select_one("div.text-80 i.fa-location-dot + text")
            if not city_tag:  # fallback: get the second div.text-80
                city_container = obj.select("div.text-80")
                city = city_container[0].get_text(strip=True).replace("📍", "") if city_container else None
            else:
                city = city_tag.strip()

            full_adres = f"{street} in {city}" if street and city else None

            # URL
            url_tag = obj.select_one("a.blocklink")
            url = url_tag["href"] if url_tag and url_tag.has_attr("href") else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("div.mt-2")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price = float(price_match.group(1).replace(".", "").replace(",", "."))

            # Area (woonoppervlakte)
            area = None
            area_tags = obj.select("div.text-80.mt-3 span")
            for tag in area_tags:
                if "m²" in tag.text:
                    woonoppervlakte_match = re.search(r"(\d+)\s*m²", tag.text)
                    if woonoppervlakte_match:
                        area = int(woonoppervlakte_match.group(1))
                        break

            # Number of rooms
            num_rooms = None
            for tag in area_tags:
                room_match = re.search(r"(\d+)\s*$", tag.text.strip())
                if "kiko-bedroom" in str(tag) and room_match:
                    num_rooms = int(room_match.group(1))
                    break

            # Availability (not explicitly shown — assume available unless price is "verkocht")
            available = "Beschikbaar"
            if price_tag and "verkocht" in price_tag.text.lower():
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
    url = "https://www.vanderlinden.nl/woning-kopen/?gad_source=1&gad_campaignid=21209884534&gbraid=0AAAAADnNA5UDFxFaJEeagbJoUxsMDvsfl&gclid=CjwKCAjw6s7CBhACEiwAuHQckt7ARKffUcWYJft033EABGJkB7abTTih9E-wCICgCuTOqDou3EMDjxoCRQIQAvD_BwE"
    html = get_html(url)
    listings = extract_vanderlinden_data(html)
    for listing in listings:
        print(listing)
        