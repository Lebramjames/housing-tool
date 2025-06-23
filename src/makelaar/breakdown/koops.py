from bs4 import BeautifulSoup

def extract_koops_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    cards = soup.select("div.c-gallery-item")

    for card in cards:
        try:
            # URL and inferred full address
            a_tag = card.select_one("a.o-media__link")
            url = a_tag["href"] if a_tag else None
            full_adres = url.strip("/").split("/")[-2].replace("-", " ").title() if url else None

            # Price
            price_elem = card.select_one("div.price")
            price = price_elem.text.strip().replace("€", "").replace("\xa0", "").strip() if price_elem else None

            # Woning type, buitenruimte, energielabel
            features_div = card.select_one("div.more-properties")
            woning_type, outside, energielabel = None, None, None

            if features_div:
                features = [d.text.strip() for d in features_div.find_all("div") if d.text.strip()]
                for item in features:
                    if item.lower() in ["tuin", "balkon"]:
                        outside = item
                    elif item.lower().startswith("energielabel"):
                        energielabel = item.split()[-1]  # e.g., "C"
                    else:
                        woning_type = item

            # Area and number of rooms
            area, num_rooms = None, None
            feature_list = card.select("ul.c-features-list li")
            for li in feature_list:
                label = li.get_text(strip=True).lower()
                bold_span = li.select_one("span.u-weight-bold")
                value = bold_span.text.strip() if bold_span else ""

                if "woonoppervlakte" in label:
                    area = value.replace("m²", "").strip()
                elif "kamers" in label:
                    num_rooms = value

            # convert price to float (e.g., "2.850,-" -> 2850.0)
            price_float = None
            if price:
                price_clean = price.replace(".", "").replace(",", ".").replace("-", "").strip()
                try:
                    price_float = float(price_clean)
                except ValueError:
                    price_float = None
            # skip if price is lower than 100000 or could not be converted
            if price_float is None or price_float < 100000:
                continue
            listings.append({
                "full_adres": full_adres,
                "url": f"https://koopsmakelaardij.nl{url}" if url else None,
                "price": price_float,
                "woning_type": woning_type,
                "outside": outside,
                "energielabel": energielabel,
                "area": area,
                "num_rooms": num_rooms
            })

        except Exception as e:
            print(f"Skipping listing due to error: {e}")

    return listings
