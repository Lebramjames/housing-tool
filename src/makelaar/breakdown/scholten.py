from bs4 import BeautifulSoup

def extract_scholten_data(html):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    cards = soup.select("div.e-loop-item")

    for card in cards:
        try:
            # Listing URL
            a_tag = card.select_one("a[href]")
            url = a_tag["href"] if a_tag else None

            # Address
            full_adres_elem = card.select_one("div.elementor-element-be45008 p span.notranslate")
            full_adres = full_adres_elem.text.strip() if full_adres_elem else None

            # Price
            price_elem = card.select_one("div.elementor-element-19557bd")
            price = price_elem.text.strip() if price_elem else None

            # Area and number of rooms (robust DOM walker)
            area = None
            num_rooms = None
            info_elem = card.select_one("div.elementor-element-9deac01 p")

            if info_elem:
                parts = info_elem.contents
                area_found = False
                for i, part in enumerate(parts):
                    if hasattr(part, 'name') and part.name == 'img' and 'house' in part.get('src', ''):
                        # Get next text (number) and potentially <sup> after it
                        text_node = parts[i + 1] if i + 1 < len(parts) else ''
                        sup_node = parts[i + 2] if i + 2 < len(parts) and hasattr(parts[i + 2], 'name') and parts[i + 2].name == 'sup' else ''
                        text_str = ''
                        if isinstance(text_node, str):
                            text_str += text_node.strip()
                        if sup_node:
                            text_str += sup_node.get_text()
                        area_digits = ''.join(filter(str.isdigit, text_str))
                        if area_digits:
                            area = area_digits
                            area_found = True

                    if hasattr(part, 'name') and part.name == 'img' and 'bed' in part.get('src', ''):
                        text_node = parts[i + 1] if i + 1 < len(parts) else ''
                        if isinstance(text_node, str):
                            num_rooms = ''.join(filter(str.isdigit, text_node.strip()))

            # Availability
            availability_elem = card.select_one(".house-status")
            available = availability_elem.text.strip() if availability_elem else "Onbekend"

            # City
            city = None
            if full_adres and "Amsterdam" in full_adres:
                city = "Amsterdam"
            elif full_adres:
                city = full_adres.split()[-1]
            # if area ends with '2', remove only the trailing '2' and convert to int
            if area and area.endswith('2'):
                area = int(area[:-1].strip())
            elif area:
                area = int(area.strip())
            # convert : € 425.000,- to float
            if price:
                price = price.replace('€', '').replace('.', '').replace(',', '.').replace('.-', '').strip()
                price = float(price)
            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })

        except Exception as e:
            print(f"Skipping a card due to error: {e}")

    return listings
