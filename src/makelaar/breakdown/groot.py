import requests
from bs4 import BeautifulSoup

def extract_groot_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    cards = soup.select("div.object")

    for card in cards:
        try:
            broker_name = "Groot Amsterdam Makelaardij B.V."
            broker_url = "https://www.grootamsterdam.nl"

            # Address
            street = card.select_one("span.object-street")
            house_number = card.select_one("span.object-housenumber")
            city = card.select_one("span.object-place")

            street_text = street.text.strip() if street else ""
            house_number_text = house_number.text.strip() if house_number else ""
            city_text = city.text.strip() if city else ""

            full_adres = f"{street_text} {house_number_text}".strip()

            # URL
            a_tag = card.select_one("a[href]")
            url = a_tag["href"] if a_tag and "http" in a_tag["href"] else f"https://www.grootamsterdam.nl{a_tag['href']}" if a_tag else None

            # Price
            price_elem = card.select_one("span.object-price-value")
            price = price_elem.text.strip().replace("€", "").strip() if price_elem else None

            # Availability
            status_elem = card.select_one("div.object-status")
            available = status_elem.text.strip() if status_elem else "Onbekend"

            # Area and rooms (if present under div.object-info)
            area, num_rooms = None, None
            info_div = card.select_one("div.object-info")
            if info_div:
                info_text = info_div.get_text(" ", strip=True).lower()
                import re
                area_match = re.search(r'(\d+)\s?m²', info_text)
                rooms_match = re.search(r'(\d+)\s?(kamers|kamer)', info_text)

                if area_match:
                    area = area_match.group(1)
                if rooms_match:
                    num_rooms = rooms_match.group(1)
            # Convert price to float (e.g., "400.000" -> 400000.0)
            if price:
                price = price.replace(".", "").replace(",", ".")
                try:
                    price = float(price)
                except ValueError:
                    price = None
            listings.append({
                "broker_name": broker_name,
                "broker_url": broker_url,
                "full_adres": full_adres,
                "url": url,
                "city": city_text,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })

        except Exception as e:
            print(f"Error parsing card: {e}")
            continue

    return listings


