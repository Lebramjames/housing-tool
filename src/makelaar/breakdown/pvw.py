# %%
from bs4 import BeautifulSoup
import re

def extract_pvw_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.makelaardijpvw.nl"

    for li in soup.select("li.aanbodEntry"):
        try:
            # URL and full_adres
            url_tag = li.select_one("a.aanbodEntryLink[href]")
            url = url_tag["href"].strip() if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            alt = li.select_one("img.foto_")["alt"] if li.select_one("img.foto_") else None
            address_match = re.match(r"(.*?)\s+in\s+(.*)\s+\d{4}\s\w{2}", alt) if alt else None
            address = address_match.group(1).strip() if address_match else None
            city = address_match.group(2).strip() if address_match else None
            full_adres = f"{address} in {city}" if address and city else None

            # Price
            price = None
            price_tag = li.select_one("span.kenmerk.koopprijs span.kenmerkValue")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

            # Area (woonoppervlakte)
            area = None
            area_tags = li.select("span.kenmerk")
            for tag in area_tags:
                if "woonoppervlakte" in tag.text.lower():
                    area_match = re.search(r"(\d+)\s*m", tag.text)
                    if area_match:
                        area = int(area_match.group(1))
                        break

            # Number of rooms (aantal kamers)
            num_rooms = None
            for tag in area_tags:
                if "kamers" in tag.text.lower():
                    room_match = re.search(r"(\d+)", tag.text)
                    if room_match:
                        num_rooms = int(room_match.group(1))
                        break

            # Available (check status label)
            available = "Beschikbaar"
            banner = li.select_one("span.objectstatusbanner")
            if banner:
                banner_text = banner.get_text(strip=True).lower()
                if "verkocht" in banner_text:
                    available = "Verkocht"
                elif "onder bod" in banner_text:
                    available = "Onder bod"
                elif "verhuurd" in banner_text:
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
    url ='https://www.makelaardijpvw.nl/aanbod/woningaanbod/-500000/koop/'
    html = get_html(url)

    listings = extract_pvw_data(html)
    for listing in listings:
        print(listing)
    url_format ='https://www.makelaardijpvw.nl/aanbod/woningaanbod/-500000/koop/pagina-{page}/'