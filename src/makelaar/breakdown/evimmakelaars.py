# %%
def extract_evimmakelaars_data(html: str):
    return []

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://evimmakelaars.nl/woningen/'
    html = get_html(url)
    listings = extract_evimmakelaars_data(html)
    for listing in listings:
        print(listing)
        