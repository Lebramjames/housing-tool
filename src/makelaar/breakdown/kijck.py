from bs4 import BeautifulSoup

def extract_kijck_data(html):
    # KIJCK. makelaars (Almere)
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    cards = soup.select("div.shadow-card")

    for card in cards:
        try:
            full_adres = card.select_one("h4").text.strip()
            city = card.select_one("span.block").text.strip()
            url = card.select_one("a[href]")['href']

            price_elem = card.find("span", class_="text-secondary text-right")
            price = price_elem.text.strip() if price_elem else None

            available_label = card.select_one("span.bg-label-green-background, span.bg-label-orange-background")
            available = available_label.text.strip() if available_label else "Onbekend"

            # Default placeholders
            area = None
            num_rooms = None

            # Extract area and number of rooms by label
            detail_rows = card.select("div.text-accent-medium.flex")

            for row in detail_rows:
                key_elem = row.select_one("span.font-bold")
                val_elem = row.select("span.text-right")[-1]  # Use last one in case of nested spans
                if key_elem and val_elem:
                    key = key_elem.text.strip()
                    val = val_elem.text.strip()

                    if "Woonoppervlakte" in key:
                        area = val.replace("m²", "").strip()
                    elif "Kamers" in key:
                        num_rooms = val.strip()

            listings.append({
                "full_adres": full_adres,
                "url": 'https://kijck.nl' + url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })
        except Exception as e:
            print(f"Skipping a card due to error: {e}")

    return listings