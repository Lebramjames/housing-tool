# %%
# %%
import requests
import os 
import pandas as pd

from src.utils.config import logging, RENTAL_DB, GEOCODED_STREETS
from src.utils.google_sheets import read_sheet_to_df, replace_full_table


SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", None)

def send_slack_message(text: str):
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        logging.info("✅ Slack message sent")
    else:
        logging.error(f"❌ Failed to send message: {response.text}")

def standardized_body(address, price, size, link):
    return (
        f"🏡 *New Rental Listing!*\n\n"
        f"📍 *Address*: {address}\n"
        f"💰 *Price*: €{price} / month\n"
        f"📏 *Size*: {size} m²\n"
        f"🔗 <{link}|View Listing>"
    )


def send_new_listing_update(df: pd.DataFrame):
    if df.empty:
        print("ℹ️ No new listings to send.")
        return

    for _, row in df.iterrows():
        try:
            # address is address_full up to the first comma
            address = row.get("address_full", "Unknown address")
            address = address.split(",")[0] if isinstance(address, str) else "Unknown address"

            # add  'info1', "info2", "info3" to the address with ({ })
            info1 = row.get("info1", "")
            info2 = row.get("info2", "")
            info3 = row.get("info3", "")
            if info1 or info2 or info3:
                address += f" ({info1}, {info2}, {info3})"
            else:
                address += " (No additional info)"
            message = standardized_body(
                address=address,
                price=row["price"],
                size=row["squared_m2"],
                link=row["link"]
            )
            send_slack_message(message)
        except Exception as e:
            print(f"⚠️ Failed to send listing: {row.get('address', 'Unknown address')} - {e}")

def run_pipeline():
    logging.info("Starting Slack notification pipeline...")

    # Read the rental database
    df = read_sheet_to_df(RENTAL_DB, 0)

    df_geocoded = read_sheet_to_df(GEOCODED_STREETS, 0)

    df = df.merge(df_geocoded[['street', 'info1', "info2", "info3"]], on='street', how='left')

    if df.empty:
        logging.info("No new listings found.")
        return

    # Filter for new listings (assuming 'is_new' column exists)
    # convert TRUE and FALSE to boolean
    # convert TRUE to True and FALSE to False
    df['is_new'] = df['is_new'].replace({'TRUE': True, 'FALSE': False})
    df['is_available'] = df['is_available'].replace({'TRUE': True, 'FALSE': False})
    df['is_slack_message_sent'] = df['is_slack_message_sent'].replace({'TRUE': True, 'FALSE': False})
    
    new_listings = df[(df['is_new'] == True) &  
                      (df['is_available'] == True) &
                        (df['price'] < 1800) &
                        (df['date_scraped'] > pd.Timestamp.now() - pd.Timedelta(days=1)) &
                        # is_slack_message_sent is False or np.nan
                        (df['is_slack_message_sent'].isna() | (df['is_slack_message_sent'] == False))]
    
    new_listings = new_listings.drop_duplicates(subset=['link'])

    if new_listings.empty:
        logging.info("No new listings to notify.")
        return
    
    # is_slack_message_sent = True
    df = read_sheet_to_df(RENTAL_DB, 0)
    df.loc[df['link'].isin(new_listings['link']), 'is_slack_message_sent'] = True

    replace_full_table(df, RENTAL_DB, 0)

    send_new_listing_update(new_listings)
    logging.info("Slack notification pipeline completed.")

if __name__ == "__main__":
    run_pipeline()
    logging.info("Slack notification pipeline executed successfully.") 