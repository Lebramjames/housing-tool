# %%
import re
import json

from bs4 import BeautifulSoup



def extract_indeling_info(html):
    soup = BeautifulSoup(html, "html.parser")
    indeling_data = {
        "kamers": None,
        "badkamers": None,
        "voorzieningen": None,
        "woonlagen": None,
        "verdieping": None,
        "energielabel": None,
        "isolatie": None,
        "verwarming": None,
        "warm_water": None,
    }

    rows = soup.select('div[data-testid="category-indeling"] dt')
    for dt in rows:
        label = dt.get_text(strip=True).lower()
        dd = dt.find_next_sibling("dd")
        value = dd.get_text(strip=True) if dd else None

        if "kamers" in label:
            indeling_data["kamers"] = value
        elif "badkamers" in label:
            indeling_data["badkamers"] = value
        elif "voorzieningen" in label:
            indeling_data["voorzieningen"] = value
        elif "woonlagen" in label:
            indeling_data["woonlagen"] = value
        elif "gelegen op" in label:
            indeling_data["verdieping"] = value

    energie_rows = soup.select('div[data-testid="category-energie"] dt')
    for dt in energie_rows:
        label = dt.get_text(strip=True).lower()
        dd = dt.find_next_sibling("dd")
        value = dd.get_text(strip=True) if dd else None

        if "energielabel" in label:
            indeling_data["energielabel"] = value
        elif "isolatie" in label:
            indeling_data["isolatie"] = value
        elif "verwarming" in label:
            indeling_data["verwarming"] = value
        elif "warm water" in label:
            indeling_data["warm_water"] = value

    return indeling_data

def extract_listing_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Step 1: Find the script tag with __NUXT__ or JSON-like data
    script = soup.find('script', string=re.compile(r'window\.__NUXT__'))
    if not script:
        return {}

    # Step 2: Extract JSON from script contents
    match = re.search(r'window\.__NUXT__\s*=\s*({.*});', script.string, re.DOTALL)
    if not match:
        return {}

    nuxt_json_str = match.group(1)

    try:
        # Evaluate or parse the JS object
        data = json.loads(nuxt_json_str)
    except json.JSONDecodeError:
        return {}

    # Step 3: Traverse through the nested JSON to pull relevant fields
    # This step depends on actual JSON structure; example below is flexible

    listing_data = {}

    # Example regex-based fallback if JSON structure varies:
    pattern_pairs = {
        'soort_appartement': r'"Soort appartement"\s*,\s*"([^"]+)"',
        'soort_bouw': r'"Soort bouw"\s*,\s*"([^"]+)"',
        'bouwjaar': r'"Bouwjaar"\s*,\s*"([^"]+)"',
        'soort_dak': r'"Soort dak"\s*,\s*"([^"]+)"',
        'woonoppervlakte_m2': r'"Wonen"\s*,\s*"(\d+)\s*m²"',
        'gebouwgebonden_buitenruimte_m2': r'"Gebouwgebonden buitenruimte"\s*,\s*"(\d+)\s*m²"',
        'externe_bergruimte_m2': r'"Externe bergruimte"\s*,\s*"(\d+)\s*m²"',
        'inhoud_m3': r'"Inhoud"\s*,\s*"(\d+)\s*m³"'
    }

    for key, regex in pattern_pairs.items():
        match = re.search(regex, html)
        if match:
            value = match.group(1).strip()
            # Only convert to int if value is numeric
            if ('m2' in key or 'm3' in key or key == 'bouwjaar') and value.isdigit():
                listing_data[key] = int(value)
            else:
                listing_data[key] = value

    return listing_data

def extract_surface_areas(text):
    """
    Extracts surface area values in m² from structured Funda HTML/JS blocks.
    Returns a dictionary with values as integers (in m²), if present.
    """
    fields = {
        "woonoppervlakte_m2": r'"Wonen"\s*,\s*"(\d+)\s*m²"',
        "gebouwgebonden_buitenruimte_m2": r'"Gebouwgebonden buitenruimte"\s*,\s*"(\d+)\s*m²"',
        "externe_bergruimte_m2": r'"Externe bergruimte"\s*,\s*"(\d+)\s*m²"',
        "inhoud_m3": r'"Inhoud"\s*,\s*"(\d+)\s*m³"'
    }

    data = {}
    for key, pattern in fields.items():
        match = re.search(pattern, text)
        if match:
            data[key] = int(match.group(1).strip())

    return data

def extract_energy_label(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the dt with "Energielabel"
    label_dt = soup.find('dt', string="Energielabel")
    if label_dt:
        # The <dd> element is typically the next sibling of the <dt>
        dd = label_dt.find_next_sibling('dd')
        if dd:
            span = dd.find('span')
            if span:
                return span.get_text(strip=True)
    return None

def extract_popularity_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Locate the popularity section
    popularity_section = soup.find('section', {'data-testid': 'object-insights'})
    if popularity_section:
        # Look for all blur-sm value containers
        blur_values = popularity_section.find_all('p', class_='blur-sm m-0 font-bold')

        if len(blur_values) >= 2:
            # The first is views, second is saved count
            data['bekeken'] = blur_values[0].get_text(strip=True)
            data['bekeken'] = re.sub(r'\D', '', blur_values[0].get_text(strip=True))  # Remove non-digit characters
            data['bewaard'] = blur_values[1].get_text(strip=True) 
            data['bewaard'] = re.sub(r'\D', '', blur_values[1].get_text(strip=True))  # Remove non-digit characters

    return data or None

def extract_overdracht_from_json_block(raw_text):
    data = {}

    fields = {
        "vraagprijs": r'"Vraagprijs"\s*,\s*"([^"]+)"',
        "prijs_per_m2": r'"Vraagprijs per m²"\s*,\s*"([^"]+)"',
        "aangeboden_sinds": r'"Aangeboden sinds"\s*,\s*"([^"]+)"',
        "status": r'"Status"\s*,\s*"([^"]+)"',
        "aanvaarding": r'"Aanvaarding"\s*,\s*"([^"]+)"',
        "servicekosten": r'"Bijdrage VvE"\s*,\s*"([^"]+)"',
    }

    for key, pattern in fields.items():
        match = re.search(pattern, raw_text)
        data[key] = match.group(1) if match else None

    return data

def extract_kadastrale_info_from_flat_html(raw_text):
    def extract_value(label_key):
        # Match the pattern: "label_key","Label","Actual value"
        pattern = rf'"{re.escape(label_key)}"\s*,\s*"[^"]+"\s*,\s*"([^"]+)"'
        match = re.search(pattern, raw_text)
        return match.group(1).strip() if match else None

    return {
        "eigendomssituatie": extract_value("cadastral-ownershipsituation"),
        "lasten": extract_value("cadastral-fees")
        # 
    }

def extract_omschrijving(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Find the heading or section that contains "Omschrijving"
    omschrijving_heading = soup.find(lambda tag: tag.name in ['h2', 'h3', 'h4'] and 'omschrijving' in tag.get_text(strip=True).lower())

    if omschrijving_heading:
        # Find the next sibling that contains the text
        content = []
        next_node = omschrijving_heading.find_next_sibling()

        # Collect all paragraphs or text blocks until a new section starts
        while next_node and next_node.name not in ['h2', 'h3', 'section']:
            if next_node.name in ['p', 'div']:
                content.append(next_node.get_text(strip=True))
            next_node = next_node.find_next_sibling()
        
        if content:
            data['omschrijving'] = '\n'.join(content)
            return data

    return None

def extract_neighborhood_block(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = {}

    # --- Fallback: extract from top header if primary not found ---
    if 'neighborhood_name' not in result:
        fallback_link = soup.find('a', attrs={'aria-label': True}, href=re.compile(r'/informatie/'))
        if fallback_link:
            result['neighborhood_fallback_name'] = fallback_link.get('aria-label')
            result['neighborhood_fallback_url'] = fallback_link.get('href')

    return result if result else None
