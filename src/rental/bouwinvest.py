# %%
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

EDGE_DRIVER_PATH = r"C:\Users\bgriffioen\OneDrive - STX Commodities B.V\Desktop\funda-project\funda-tool\msedgedriver.exe"
START_URL = "https://www.wonenbijbouwinvest.nl/huuraanbod?query=Amsterdam&price=1000-1500&type=appartement&range=5"

options = Options()
options.add_argument("--start-maximized")
service = EdgeService(executable_path=EDGE_DRIVER_PATH)
driver = webdriver.Edge(service=service, options=options)
wait = WebDriverWait(driver, 10)

driver.get(START_URL)

# Accept cookies
try:
    wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))).click()
    print("Cookies accepted.")
except:
    print("Cookie banner not shown or already accepted.")

all_listings = []

while True:
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    listings = soup.select("a.projectproperty-tile, a.project-tile")

    for listing in listings:
        try:
            url = listing.get("href")
            if url and not url.startswith("http"):
                url = "https://www.wonenbijbouwinvest.nl" + url

            adres = listing.select_one(".projectproperty-tile__content__body .h2") or \
                    listing.select_one(".project-tile__content--body .h2")
            full_adres = adres.get_text(strip=True) if adres else None

            city = listing.select_one(".projectproperty-tile__content__header .paragraph, .project-tile__content--header .paragraph")
            city = city.get_text(strip=True) if city else None

            price_tag = listing.select_one(".price-tag")
            price = price_tag.get_text(strip=True) if price_tag else None

            area_tag = listing.find("span", class_="facet icon-surface")
            if not area_tag:
                area_tag = listing.find("span", text=re.compile(r"M²"))
            area = area_tag.get_text(strip=True).split()[0] if area_tag else None

            room_tag = listing.find("span", class_="facet icon-total_sleepingrooms")
            num_rooms = re.search(r"(\d+)", room_tag.get_text()) if room_tag else None
            num_rooms = int(num_rooms.group(1)) if num_rooms else None

            available_tag = listing.select_one(".sticker-bar__top")
            available = available_tag.get_text(strip=True) if available_tag else None

            all_listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": city,
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": available
            })
            print(f"Parsed listing: {full_adres}, {price}, {area}, {num_rooms}, {available}")

        except Exception as e:
            print(f"Error parsing a listing: {e}")

    # Try to find and click the "Volgende" (Next) button
    try:
        next_btn = driver.find_element(By.CLASS_NAME, "pagination__next")
        next_btn.click()
    except:
        print("No more pages.")
        break

# Close browser
driver.quit()

# Save or display
from pprint import pprint
pprint(all_listings)

# %%



if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://www.wonenbijbouwinvest.nl/huuraanbod?query=Amsterdam&page=1&price=&range=5&type=appartement&availability=&orientation=&sleepingrooms=&surface=&seniorservice=false'
    html = get_html(url)
    import pyperclip
    pyperclip.copy(html)
    