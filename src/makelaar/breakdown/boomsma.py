# %%
from bs4 import BeautifulSoup
import re

def extract_bbmakelaars_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    
    for card in soup.select("a.pxp-results-card-1"):
        try:
            # URL
            url = card.get("href")
            
            # Address and City
            title_div = card.select_one("div.pxp-results-card-1-details-title")
            full_adres, city = None, None
            if title_div:
                text_parts = title_div.decode_contents().split("<br")
                if len(text_parts) >= 2:
                    address = BeautifulSoup(text_parts[0], "html.parser").text.strip()
                    city_match = re.search(r'in\s+([A-Z\s\-]+)', BeautifulSoup(text_parts[1], "html.parser").text)
                    city = city_match.group(1).strip().title() if city_match else None
                    full_adres = f"{address} in {city}" if city else address

            # Price
            price = None
            price_div = card.select_one("div.pxp-results-card-1-details-price")
            if price_div:
                price_text = price_div.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area and Rooms
            area, num_rooms = None, None
            features_div = card.select_one("div.pxp-results-card-1-features")
            if features_div:
                features_text = features_div.get_text(" ", strip=True)
                area_match = re.search(r"(\d+)\s*M", features_text)
                if area_match:
                    area = int(area_match.group(1))
                room_match = re.search(r"(\d+)\s+Kamers", features_text)
                if room_match:
                    num_rooms = int(room_match.group(1))

            # Availability
            available = "Beschikbaar"
            label_div = card.select_one("div.property-label span")
            if label_div:
                label = label_div.text.strip().lower()
                if "verkocht" in label:
                    available = "Verkocht"
                elif "onder bod" in label:
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
    url ='https://www.bbmakelaars.nl/ons-aanbod'
    html = get_html(url)
    listings = extract_bbmakelaars_data(html)
    for listing in listings:
        print(listing)
        