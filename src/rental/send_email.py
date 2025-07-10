# %%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

GOOGLE_KEY = os.getenv("GOOGLE_KEY")

import pandas as pd
import os
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Load preference geojson
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent.parent

def create_vbt_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_properties_amsterdam.csv')  # ✅ enriched version
    df = pd.read_csv(data_path, sep=',')

    df = df[df['is_available'] == True]

    if 'preference' in df.columns:
        df = df[df['preference'] == True]

    df = df.sort_values(by='number_of_responses', ascending=True)

    base_url = 'https://vbtverhuurmakelaars.nl'
    df['link'] = base_url + df['detail_url']
    df['price_per_m2'] = df['price_per_month'] / df['surface_area_m2']
    df = df.dropna(subset=['address', 'price_per_month', 'surface_area_m2', 'price_per_m2', 'number_of_responses', 'link'])

    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "VBT Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'Resp.':>6} {'Neighborhood':>15}\n"
        body += "-" * 50 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            neighborhood = row.get('neighborhood', 'N/A')
            body += f"{address:<35} {int(row['price_per_month']):>8} {int(row['surface_area_m2']):>5} {row['price_per_m2']:>6.2f} {int(row['number_of_responses']):>6} {neighborhood:>15}\n"
            body += f"🔗 {row['link']}\n\n"
        return body

    return create_email_body(df)


def create_bouwinvest_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_bouwinvest_amsterdam.csv')
    df = pd.read_csv(data_path, sep=',')

    # Sort: new listings first, then by price
    df = df.sort_values(by=['is_new', 'price'], ascending=[False, True])

    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price'] / df['surface_m2']
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "🏢 Bouwinvest Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'New':>4} {'Neighborhood':>15}\n"
        body += "-" * 70 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            is_new = 'Yes' if row.get('is_new', False) else 'No'
            neighborhood = row.get('neighborhood', 'N/A')

            body += f"{address:<35} {int(row['price']):>8} {int(row['surface_m2']):>5} {row['price_per_m2']:>6.2f} {is_new:>4} {neighborhood:>15}\n"
            body += f"🔗 {row['url']}\n\n"

        return body

    return create_email_body(df)


def send_gmail(to_email, subject, body, gmail_user, app_password = GOOGLE_KEY):
    msg = MIMEMultipart()
# def send_gmail(to_email, subject, body, gmail_user, app_password = GOOGLE_KEY):
    if not app_password:
        print("❌ Error: GOOGLE_KEY environment variable is not set.")
        return

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, app_password)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def create_vesteda_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_vesteda_amsterdam.csv')
    df = pd.read_csv(data_path, sep=',')

    df = df[df['is_available'] == True]

    # Ensure we're only working with listings in Amsterdam
    df = df[df['address'].str.contains('Amsterdam', case=False, na=False)]

    # Rename columns
    df.rename(columns={'area': 'surface_m2'}, inplace=True)

    # Sort: new listings first, then by price
    df = df.sort_values(by=['is_new', 'price'], ascending=[False, True])

    def create_email_body(df, max_rows=20):
        if df.empty:
            return "Vesteda Rentals (available):\n\nGeen beschikbare woningen gevonden."
        
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price'] / df['surface_m2']
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "🏢 Top Vesteda Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'New':>4} {'Neighborhood':>15}\n"
        body += "-" * 70 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            neighborhood = row.get('neighborhood', 'N/A')
            is_new = 'Yes' if row.get('is_new', False) else 'No'

            body += f"{address:<35} {int(row['price']):>8} {int(row['surface_m2']):>5} {row['price_per_m2']:>6.2f} {is_new:>4} {neighborhood:>15}\n"
            body += f"🔗 {row['url']}\n\n"
        
        return body

    body = create_email_body(df)
    return body

def create_ikwilhuren():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'enriched_ikwilhuren_amsterdam.csv')
    df = pd.read_csv(data_path, sep=',')

    # df = df[df['address'].str.contains('Amsterdam', case=False, na=False)]
    # Parse dates
    df['date_scraped'] = pd.to_datetime(df['date_scraped'], errors='coerce')
    # --- Get first scraped date for each listing (using ALL rows, not just active) ---
    first_seen = df.groupby('link')['date_scraped'].min().reset_index().rename(columns={'date_scraped': 'first_scraped'})
    # --- Get latest version of each listing ---
    df = df.sort_values('date_scraped', ascending=False).drop_duplicates('link')

    # --- Now filter only the ones that are currently active ---
    df = df[(df['is_active'] == True) & (df['is_available'] == True)]

    # Merge in the first_seen date (from full dataset)
    df = df.merge(first_seen, on='link', how='left')

    # Create combined address
    df['address'] = df['address'] + ' ' + df['city']

    # Rename columns
    df.rename(columns={'surface_m2': 'surface_area_m2', 'price_per_month': 'price_per_month'}, inplace=True)

    # Clean and compute derived columns
    df = df.sort_values(by='price_per_month', ascending=True)
    df['price_per_m2'] = df['price_per_month'] / df['surface_area_m2']

    df = df.dropna(subset=['address', 'price_per_month', 'surface_area_m2', 'price_per_m2', 'link'])

    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price_per_m2'].round(2)

        # Clean up notes
        df['available_from_note'] = df['available_from_note'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()

        body = "🏢 Ik wil huren (MVGM - Top Rentals - available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'Neighborhood':>15}\n"
        body += "-" * 70 + "\n"

        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            first_scraped = row['first_scraped'].date() if pd.notnull(row['first_scraped']) else 'N/A'
            available_note = row['available_from_note'] if pd.notnull(row['available_from_note']) else 'N/A'
            is_new = str(row['is_new']) if 'is_new' in row and pd.notnull(row['is_new']) else 'N/A'
            neighborhood = row.get('neighborhood', 'N/A')

            body += f"{address:<35} {int(row['price_per_month']):>8} {int(row['surface_area_m2']):>5} {row['price_per_m2']:>6.2f} {neighborhood:>15}\n"
            body += f"🔗 {row['link']}\n"
            body += f"📅 First scraped: {first_scraped} | 🆕 New: {is_new}\n"
            body += f"📌 Beschikbaar: {available_note}\n\n"

        return body
    body = create_email_body(df)
    return body

def run_pipeline(rental_company='vbt_huren'):
    logging.info(f"[START] Sending email for {rental_company}...")  

    body_dict = {
        'vbt_huren': create_vbt_body,
        'bouwinvest': create_bouwinvest_body,
        'vesteda': create_vesteda_body,
        "ikwilhuren": create_ikwilhuren,  # Assuming ikwilhuren uses the same body as vbt_huren
        # 'funda': create_body
    }

    body = body_dict.get(rental_company, create_vbt_body)()

    # to_email = 'bramgriffioen98@gmail.com, rianne.boon@hotmail.com'
    to_email = 'bramgriffioen98@gmail.com'

    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    subject = f"{rental_company} - Dagelijkse huurwoningen in Amsterdam - {today}"
    # body = 'This is a test email sent from Python using Gmail.'
    gmail_user = 'bramgriffioen98@gmail.com'
    send_gmail(to_email, subject, body, gmail_user) 
    
    logging.info(f"[END] Email sent for {rental_company}.") 
    return body

if __name__ == "__main__":
    body = run_pipeline(rental_company='ikwilhuren')
    print(body)
