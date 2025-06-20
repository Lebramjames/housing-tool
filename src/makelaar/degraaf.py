# %%
from bs4 import BeautifulSoup
import re

def extract_degraaf_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.degraafengroot.nl"

    for obj in soup.select("li.propertycard"):
        try:
            # Address from heading
            heading = obj.select_one("h2.h4")
            if heading and "|" in heading.text:
                raw_adres, city = map(str.strip, heading.text.split("|"))
            else:
                continue  # skip malformed entries

            full_adres = f"{raw_adres} in {city}"

            # URL
            url_tag = obj.select_one("a[href]")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price = None
            price_tag = obj.select_one("strong.price")
            if price_tag:
                price_text = price_tag.get_text()
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except:
                        pass

            # Area
            area = None
            m2_tag = obj.find("span", string=re.compile(r"\d+\s*m²", re.IGNORECASE))
            if m2_tag:
                area_match = re.search(r"(\d+)\s*m²", m2_tag.text)
                area = int(area_match.group(1)) if area_match else None

            # Rooms
            num_rooms = None
            if obj.has_attr("data-rooms"):
                try:
                    num_rooms = int(obj["data-rooms"])
                except:
                    pass

            # Status (no explicit status found in HTML; assume available)
            available = "Beschikbaar"

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
    url= 'https://www.degraafengroot.nl/koop?gad_source=1&gad_campaignid=21092060303&gbraid=0AAAAACykZ3DstkM9YLvVfcq2fTb3IbttU&gclid=CjwKCAjw6s7CBhACEiwAuHQckvhUomFfer3XiAKFqoPMB3HxgcU16DbpL_CgHf9U-lZ2Qk3Czk72ZxoCmRYQAvD_BwE&location=amsterdam'
    html = get_html(url)
    listings = extract_degraaf_data(html)
    for listing in listings:
        print(listing)
        