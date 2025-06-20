# %%
def extract_thuisinvastgoed_data(html):
    return []

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://thuisinvastgoed.nl/aanbod/'
    html = get_html(url)
    listings = extract_thuisinvastgoed_data(html)
    for listing in listings:
        print(listing)
    