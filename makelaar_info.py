# %%
import argparse
import pyperclip
from src.utils.get_url import get_html

def extract_html_snippet(html: str, keyword: str, window: int = 10000):
    index = html.lower().find(keyword.lower())
    if index == -1:
        raise ValueError(f"'{keyword}' not found in page.")
    start = max(0, index - window)
    end = min(len(html), index + window)
    return html[start:end]

def load_function_code(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Generate ChatGPT prompt to extract listing data.")
    parser.add_argument("--url", required=True, help="URL of the real estate listing page")
    parser.add_argument("--street", required=True, help="Street name to locate relevant HTML section")
    args = parser.parse_args()

    try:
        html = get_html(args.url)
        snippet = extract_html_snippet(html, args.street)
        function_code = load_function_code("src/makelaar/wester.py")

        prompt = f""" this is for company {args.url.split('/')[2]}
I want to extract the following fields for all listings visible in this HTML:
 - full_adres
 - url
 - city
 - price
 - area
 - num_rooms
 - available

Use this extraction function as a reference:

{function_code}

Here is the relevant trimmed HTML around the street I specified:

{snippet}
"""

        pyperclip.copy(prompt)
        print("✅ Prompt successfully copied to clipboard! Paste it into ChatGPT.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
