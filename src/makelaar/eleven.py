def extract_eleven_data(html: str):
    from bs4 import BeautifulSoup
    import re

    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.11makelaars.nl"

    for post in soup.select("article.realworks_wonen"):
        try:
            # Address
            address_tag = post.select_one("header.entry-header h2.entry-title")
            full_adres = address_tag.text.strip() if address_tag else None

            # URL
            url_tag = address_tag.find("a") if address_tag else None
            url = url_tag["href"] if url_tag and "href" in url_tag.attrs else None
            if url and not url.startswith("http"):
                url = base_url + url

            # Price
            price_tag = post.select_one("div.prijs")
            price = None
            if price_tag:
                price_match = re.search(r"€\s?([\d\.,]+)", price_tag.text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area
            area = None
            area_tag = post.find(text=re.compile(r"m²"))
            if area_tag:
                area_match = re.search(r"(\d+)\s*m²", area_tag)
                if area_match:
                    area = int(area_match.group(1))

            # Number of rooms
            num_rooms = None
            room_tag = post.find(text=re.compile(r"kamers?", re.IGNORECASE))
            if room_tag:
                room_match = re.search(r"(\d+)\s+kamers?", room_tag)
                if room_match:
                    num_rooms = int(room_match.group(1))

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": "Amsterdam",
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": "Beschikbaar"
            })
        except Exception:
            continue

    return listings
