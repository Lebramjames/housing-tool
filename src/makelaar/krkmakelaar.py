# %%

def extract_krkmakelaar_data(html: str):
    return []
if __name__ == "__main__":
    from src.utils.get_url import get_html
    url = 'https://krk.nl/wonen/aanbod'
    html = get_html(url)
    import pyperclip
    pyperclip.copy(html)
# %%
