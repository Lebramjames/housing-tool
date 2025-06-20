# %%
from bs4 import BeautifulSoup
import re

def extract_nieuwamsterdamshuys_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.nieuwamsterdamshuys.nl"

    for fig in soup.select("figure.sqs-block-image-figure"):
        try:
            # URL
            url_tag = fig.select_one("a.sqs-block-image-link")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Address
            title_tag = fig.select_one("div.image-title")
            full_adres = title_tag.get_text(strip=True) if title_tag else None

            # City - infer from address suffix or leave as None
            city = None
            if full_adres:
                parts = full_adres.strip().split()
                if len(parts) >= 2:
                    city = parts[-1] if parts[-1][0].isupper() else None

            # Description block
            subtitle_tag = fig.select_one("div.image-subtitle")
            subtitle_text = subtitle_tag.get_text(separator="\n", strip=True).lower() if subtitle_tag else ""

            # Price
            price = None
            price_match = re.search(r"€\s?([\d\.,]+)", subtitle_text)
            if price_match:
                price_str = price_match.group(1).replace(".", "").replace(",", ".")
                try:
                    price = float(price_str)
                except ValueError:
                    pass

            # Area
            area = None
            area_match = re.search(r"woonoppervlakte:\s*(\d+)\s*m", subtitle_text)
            if area_match:
                area = int(area_match.group(1))

            # Rooms
            num_rooms = None
            room_match = re.search(r"aantal kamers:\s*(\d+)", subtitle_text)
            if room_match:
                num_rooms = int(room_match.group(1))

            # Status
            available = "Beschikbaar"
            if "verkocht onder voorbehoud" in subtitle_text:
                available = "Verkocht onder voorbehoud"
            elif "onder bod" in subtitle_text:
                available = "Onder bod"
            elif "verkocht" in subtitle_text:
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
    url ='https://www.nieuwamsterdamshuys.nl/woningaanbod?gad_source=1&gad_campaignid=810625601&gbraid=0AAAAADRpcKRrdpK5QYZI3KcRgyD4EZmUk&gclid=Cj0KCQjwjdTCBhCLARIsAEu8bpJjxioNXUpgAorfOR__Jmrnqtn2JnKzpKEI1_frCjZnYAKTPsDGGGsaAiHLEALw_wcB'
    html = get_html(url)
    listings = extract_nieuwamsterdamshuys_data(html)
    for listing in listings:
        print(listing)
        