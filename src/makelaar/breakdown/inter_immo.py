# %%
from bs4 import BeautifulSoup
import re

def extract_interimmo_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.interimmo.nl"

    for obj in soup.select("div.frt_list_item"):
        try:
            a_tag = obj.select_one("a[href]")
            url = a_tag["href"] if a_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Full text line like: "Amsterdam | Jan Smitstraat 14"
            info_tag = obj.select_one("div.frt_list_item_info")
            address_line = info_tag.get_text(strip=True) if info_tag else ""
            city = None
            street = None
            if "|" in address_line:
                city_part, street_part = map(str.strip, address_line.split("|", 1))
                city = city_part
                street = street_part
            full_adres = f"{street} in {city}" if street and city else None

            # Price
            price = None
            price_tag = obj.select_one("div.frt_list_item_info b")
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price = float(price_match.group(1).replace(".", "").replace(",", "."))

            # Area
            area = None
            tags = obj.select("div.frt_list_item_tags div")
            for tag in tags:
                if "m²" in tag.text or "m&sup2;" in tag.decode_contents():
                    match = re.search(r"(\d+)", tag.text)
                    if match:
                        area = int(match.group(1))
                        break

            # Number of rooms (based on "x slaapkamers")
            num_rooms = None
            for tag in tags:
                if "slaapkamer" in tag.text.lower():
                    match = re.search(r"(\d+)", tag.text)
                    if match:
                        num_rooms = int(match.group(1))
                        break

            # Availability
            available = "Beschikbaar"
            status_tag = obj.select_one("span.frt_list_item_status")
            if status_tag:
                status_text = status_tag.get_text(strip=True).lower()
                if "onder bod" in status_text:
                    available = "Onder bod"
                elif "verkocht" in status_text or "verhuurd" in status_text:
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
    url = 'https://www.interimmo.nl/aanbod/koop/?input_huur_of_koop=koop&input_stad=AMSTERDAM&input_prijs_huur=&input_prijs_koop=400000-500000&input_oppervlakte=&input_status_huur=&input_status_koop=BESCHIKBAAR&input_slaapkamers=&input_huurconditie=&input_buitenruimte=&input_type=&_gl=1*2e3b4w*_up*MQ..*_gs*MQ..&gclid=CjwKCAjw6s7CBhACEiwAuHQcktEDhPPHTZZHQGFI8k-yYIyA8A57ELE2ZDa5K9Xpy7AVhtOSguvvARoCJucQAvD_BwE&gbraid=0AAAAADiRkdHQIgfw95LcVv5wWHD8A9o9I'
    html = get_html(url)
    listings = extract_interimmo_data(html)
    for listing in listings:
        print(listing)
    