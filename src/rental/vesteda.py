# %%
import tempfile
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_html_with_cookies_handled(url: str, wait_time=10) -> str:
    edge_driver_path = r"C:\Users\bgriffioen\OneDrive - STX Commodities B.V\Desktop\funda-project\funda-tool\msedgedriver.exe"
    
    options = EdgeOptions()
    options.use_chromium = True
    options.add_argument("--headless=new")  # Comment this line to see the browser window
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    # Use a temporary user data dir to avoid conflicts
    temp_profile_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_profile_dir}")
    
    service = EdgeService(executable_path=edge_driver_path)
    driver = webdriver.Edge(service=service, options=options)
    
    driver.get(url)

    try:
        # Wait for cookie banner and click "Alles weigeren"
        WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        ).click()
        time.sleep(2)  # Allow time for the page to update after dismissing cookies
    except Exception as e:
        print("Cookie banner not found or clickable:", e)

    html = driver.page_source
    driver.quit()
    return html



# def extract_listings(html: str):
#     soup = BeautifulSoup(html, "html.parser")
#     base_url = "https://www.vesteda.com"
#     listings = []

#     for li in soup.select("li.o-layout__cell"):
#         try:
#             a_tag = li.select_one("a[href]")
#             if not a_tag:
#                 continue
#             url = base_url + a_tag["href"]

#             # Title
#             title = li.select_one("h3 span")
#             title = title.get_text(strip=True) if title else None

#             # City
#             city = li.select_one("strong.u-heading")
#             city = city.get_text(strip=True) if city else None

#             # Price
#             price_tag = li.select_one(".o-card--listview-price b")
#             price = None
#             if price_tag:
#                 price_text = price_tag.get_text(strip=True)
#                 match = re.search(r"€\s?([\d\.,]+)", price_text)
#                 if match:
#                     price = float(match.group(1).replace(".", "").replace(",", "."))

#             # Area (woonoppervlakte)
#             area = None
#             area_match = li.find(string=re.compile(r"Woonoppervlakte.*\b\d+ m²"))
#             if area_match:
#                 area_val = re.search(r"(\d+)\s*m²", area_match)
#                 if area_val:
#                     area = int(area_val.group(1))

#             # Number of rooms (slaapkamers)
#             num_rooms = None
#             room_match = li.find(string=re.compile(r"slaapkamer\(s\)\s*\b\d+"))
#             if room_match:
#                 num_rooms_val = re.search(r"(\d+)", room_match)
#                 if num_rooms_val:
#                     num_rooms = int(num_rooms_val.group(1))

#             # Image
#             img = li.select_one("img.c-img")
#             image_url = img["src"] if img and img.has_attr("src") else None

#             listings.append({
#                 "title": title,
#                 "url": url,
#                 "city": city,
#                 "price": price,
#                 "area": area,
#                 "num_rooms": num_rooms,
#                 "image_url": image_url
#             })

#         except Exception as e:
#             print(f"Error parsing a listing: {e}")
#             continue

#     return listings


if __name__ == "__main__":
    search_url = "https://www.vesteda.com/nl/woning-zoeken?placeType=1&sortType=0&radius=5&s=Amsterdam,%20Nederland&sc=woning&latitude=52.367573&longitude=4.904139&filters=0&priceFrom=500&priceTo=9999"
    html = get_html_with_cookies_handled(search_url)
    # listings = extract_listings(html)

    # for listing in listings:
    #     print(listing)
