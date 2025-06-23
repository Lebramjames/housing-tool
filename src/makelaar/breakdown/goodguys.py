# %%
# ERROR all java bsed
from bs4 import BeautifulSoup
import re

def extract_goodguys_data(html: str):
    return []

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url ='https://www.goodguys.nl/nl/woningaanbod#{%22view%22:%22grid%22,%22sort%22:%22addedDesc%22,%22searchTerms%22:[%22address%22,%22zipcode%22,%22city%22,%22state%22],%22address%22:%22%22,%22title%22:%22%22,%22salesRentals%22:%22both%22,%22salesPriceMin%22:0,%22salesPriceMax%22:9999999999,%22devSalesPriceMin%22:0,%22devSalesPriceMax%22:9999999999,%22rentalsPriceMin%22:0,%22rentalsPriceMax%22:9999999999,%22devRentalsPriceMin%22:0,%22devRentalsPriceMax%22:9999999999,%22surfaceMin%22:0,%22surfaceMax%22:9999999999,%22unitsMin%22:0,%22unitsMax%22:9999999999,%22devSurfaceMin%22:0,%22devSurfaceMax%22:9999999999,%22plotSurfaceMin%22:0,%22plotSurfaceMax%22:9999999999,%22roomsMin%22:0,%22roomsMax%22:9999999999,%22bedroomsMin%22:0,%22bedroomsMax%22:9999999999,%22bathroomsMin%22:0,%22bathroomsMax%22:9999999999,%22city%22:[],%22district%22:[],%22mainType%22:[],%22buildType%22:[],%22tag%22:[],%22country%22:[],%22state%22:[],%22listingsType%22:[],%22ignoreType%22:[],%22categories%22:[],%22status%22:%22available%22,%22statusStrict%22:false,%22includeIsBought%22:false,%22user%22:%22%22,%22branch%22:%22%22,%22apartmentType%22:%22%22,%22houseType%22:%22%22,%22archiveTime%22:15778463,%22page%22:1,%22grouped%22:true}'
    html = get_html(url)
    import pyperclip
    pyperclip.copy(html)
    listings = extract_goodguys_data(html)
    for listing in listings:
        print(listing)
