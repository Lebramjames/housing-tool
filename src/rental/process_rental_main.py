# %%
# https://krk.nl/wonen/aanbod?buy_rent=rent&order_by=created_at-desc&_gl=1*sz0n87*_up*MQ..*_ga*MTY0NzIxOTUuMTczMDg4NTk5NA..*_ga_HV3ETX4N4F*MTczMDg4NTk5My4xLjEuMTczMDg4NTk5My4wLjAuODY4NTA1Njk3
# https://www.pararius.nl/huurwoningen/amsterdam/0-2000
# https://vbtverhuurmakelaars.nl/woningen
# https://www.vesteda.com/nl/woning-zoeken?placeType=1&sortType=0&radius=5&s=Amsterdam,%20Nederland&sc=woning&latitude=52.367573&longitude=4.904139&filters=&priceFrom=500&priceTo=9999
# https://www.wonenbijbouwinvest.nl/huuraanbod?query=Amsterdam&page=1&price=&range=5&type=appartement&availability=&orientation=&sleepingrooms=&surface=&seniorservice=false
# https://directwonen.nl/huurwoningen-huren/amsterdam

from src.rental import vbt_huren

def process_rental_main():

    vbt_huren.run_pipeline()

if __name__ == "__main__":
    process_rental_main()
    

