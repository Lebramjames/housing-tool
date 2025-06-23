from bs4 import BeautifulSoup

import re

def extract_vanhuisuit_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.vanhuisuit-makelaars.nl"

    for article in soup.select("article.result"):
        try:
            # Extract full address
            address_tag = article.select_one("h2.result__address")
            if not address_tag:
                continue
            address_parts = address_tag.stripped_strings
            address_parts = list(address_parts)
            street = address_parts[0] if len(address_parts) > 0 else None
            city = address_parts[1] if len(address_parts) > 1 else None
            full_adres = f"{street} in {city}" if street and city else None

            # Extract price
            price_tag = article.select_one("strong.result__price")
            price = int(re.sub(r"[^\d]", "", price_tag.text)) if price_tag else None

            # Extract area
            area_tag = article.find("li", string=re.compile(r"\d+\s*m²"))
            area = int(re.search(r"(\d+)", area_tag.text).group(1)) if area_tag else None

            # Extract number of rooms
            room_tag = article.find("li", string=re.compile(r"\d+\s+slaapkamer"))
            num_rooms = int(re.search(r"(\d+)", room_tag.text).group(1)) if room_tag else None

            # Extract listing URL
            url_tag = article.select_one("a.button--secondary[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Extract availability
            status_tag = article.select_one(".status-label")
            status_text = status_tag.text.strip().lower() if status_tag else ""
            available = "Beschikbaar" if "verkocht" not in status_text else "Verkocht (onder voorbehoud)"

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


