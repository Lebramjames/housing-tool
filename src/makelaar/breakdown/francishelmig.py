# %%
# TODO HTML loads wrong data

def extract_francishelmig_data(html):
    return []

if __name__ == "__main__":
    from src.utils.get_url import get_html
    url ='https://www.francishelmig.nl/woningaanbod-amsterdam'
    html = get_html(url)
    import pyperclip
    pyperclip.copy(html)  # Copy HTML to clipboard for debugging