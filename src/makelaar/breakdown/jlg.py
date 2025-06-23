 #%%

from bs4 import BeautifulSoup
import re

def extract_jlg_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    
    for card in soup.select("article.card--wonen"):
        try:
            # URL
            url_tag = card.select_one("a.card__overlay")
            url = url_tag["href"] if url_tag and url_tag.has_attr("href") else None

            # Street address
            address_tag = card.select_one("div.card__heading h2")
            street = address_tag.text.strip() if address_tag else None

            # Postal code and city
            pc_city_tag = card.select_one("div.card__prose p")
            if pc_city_tag:
                pc_city_text = pc_city_tag.get_text(strip=True)
                postal_code, city = pc_city_text.split(",", 1)
                city = city.strip()
            else:
                postal_code = city = None

            full_adres = f"{street}, {postal_code.strip()} {city}" if street and postal_code and city else None

            # Price
            price_tag = card.select_one("div.card__price p")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price_match = re.search(r"€\s?([\d\.,]+)", price_text)
            price = float(price_match.group(1).replace(".", "").replace(",", ".")) if price_match else None

            # Area (m²) and Rooms
            footer_items = card.select("div.card__footer li.card__item span.card__text")
            area = None
            num_rooms = None
            for span in footer_items:
                text = span.get_text(strip=True)
                if text.isdigit():
                    num = int(text)
                    if not area:
                        area = num
                    elif not num_rooms:
                        num_rooms = num
                        break  # we found both

            # Availability: default to "Beschikbaar" unless there's a clear reason not to
            available = "Beschikbaar"  # Static unless more logic is added (e.g., "Verkocht", "Onder bod")

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
    url= 'https://jlgrealestate.com/woningen/?#q1bKzU9JzFGyUiooyswqVtJRyi9KSS1KqgSKgFlWicXJOgWlSTmZyYklmakpiSWluVYpqcXJQKXZ-fkFEG1W1Uq5iRVAPaYGIKBUWwsA'
    html = get_html(url)
    listings = extract_jlg_data(html)
    for listing in listings:    
        print(listing)