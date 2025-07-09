# %%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

GOOGLE_KEY = os.getenv("GOOGLE_KEY")

import pandas as pd
import os
import json
from pathlib import Path
from shapely.geometry import Point, Polygon

# Load preference geojson
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent.parent

def create_vbt_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'properties_amsterdam.csv')
  
    df = pd.read_csv(data_path, sep=',')
    # filter: is_available:
    df = df[df['is_available'] == True]
    df = df[df['preference'] == True]

    # sort number_of_responses
    df = df.sort_values(by='number_of_responses', ascending=True)

    base_url = 'https://vbtverhuurmakelaars.nl'

    df['link'] = base_url +  df['detail_url'] 
    df['price_per_m2'] = df['price_per_month'] / df['surface_area_m2']

    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "🏠 Top Amsterdam Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'Resp.':>6}\n"
        body += "-" * 30 + "\n"
        
        for _, row in df.iterrows():
            address = row['address'][:32] + "..." if len(row['address']) > 35 else row['address']
            body += f"{address:<35} {int(row['price_per_month']):>8} {int(row['surface_area_m2']):>5} {row['price_per_m2']:>6.2f} {int(row['number_of_responses']):>6}\n"
            body += f"🔗 {row['link']}\n\n"
        return body

    body = create_email_body(df)
    return body

def create_bouwinvest_body():
    data_path = os.path.join(parent_dir, 'data', 'huren', 'bouwinvest_amsterdam.csv')
    df = pd.read_csv(data_path, sep=',')

    # sort based on is_new True first, then sort by price_per_month
    df = df.sort_values(by=['is_new', 'price'], ascending=[False, True])
    # create same body as vbt_huren but than with address, is_new,  price_per_month, surface_area_m2, availability, url
    def create_email_body(df, max_rows=10):
        df = df.head(max_rows).copy()
        df['price_per_m2'] = df['price'] / df['surface_m2']
        df['price_per_m2'] = df['price_per_m2'].round(2)

        body = "🏢 Top Bouwinvest Rentals (available):\n\n"
        body += f"{'Address':<35} {'€ Rent':>8} {'m²':>5} {'€/m²':>6} {'New':>4}\n"
        body += "-" * 30 + "\n"
        
        for _, row in df.iterrows():
            address = row['adress'][:32] + "..." if len(row['adress']) > 35 else row['adress']            
            body += f"{address:<35} {int(row['price']):>8} {int(row['surface_m2']):>5} {row['price_per_m2']:>6.2f} {'Yes' if row['is_new'] else 'No':>4}\n"
            body += f"🔗 {row['url']}\n\n"
        return body
    
    body = create_email_body(df)

    return body

def send_gmail(to_email, subject, body, gmail_user, app_password = GOOGLE_KEY):
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


def run_pipeline(rental_company='bouwinvest'):

    body_dict = {
        'vbt_huren': create_vbt_body,
        'bouwinvest': create_bouwinvest_body,
        # 'funda': create_body
    }

    body = body_dict.get(rental_company, create_vbt_body)()

    to_email = 'bramgriffioen98@gmail.com, rianne.boon@hotmail.com'

    subject_dict = {
        'vbt_huren': 'Dagelijkse VBT Verhuur Makelaars Huren Update',
        'bouwinvest': 'Dagelijkse Bouwinvest Huren Update',
        'funda': 'Dagelijkse Funda Huren Update'
        }
    
    subject = subject_dict.get(rental_company, 'Dagelijkse Huren Update')
    
    # body = 'This is a test email sent from Python using Gmail.'
    gmail_user = 'bramgriffioen98@gmail.com'

    send_gmail(to_email, subject, body, gmail_user) 

if __name__ == "__main__":
    run_pipeline()