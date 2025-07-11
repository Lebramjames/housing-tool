# %%
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import os
import math

GOOGLE_SREVICE_JSON_KEY = os.getenv("GOOGLE_SERVICE_JSON_KEY",None)

from src.utils import base64_decoder
from src.utils.config import logging
from src.utils.config import GEOCODED_STREETS, RENTAL_DB

def clean_value(v):
    if isinstance(v, pd.Timestamp):
        return v.isoformat()
    if pd.isna(v) or (isinstance(v, float) and (math.isinf(v) or math.isnan(v))):
        return None
    if isinstance(v, (str, int, float, bool, type(None))):
        return v
    return str(v)

def read_sheet_to_df(sheet_id: str, sheet_index: int = 0) -> pd.DataFrame:
    import pandas as pd
    import gspread
    from google.oauth2.service_account import Credentials

    if GOOGLE_SREVICE_JSON_KEY:
        creds_dict = base64_decoder.decode_base64_to_json(GOOGLE_SREVICE_JSON_KEY)
    else:
        raise ValueError("Missing GOOGLE_SERVICE_JSON_KEY environment variable.")
    
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.get_worksheet(sheet_index)

    all_data = worksheet.get_all_values()
    if not all_data:
        return pd.DataFrame()

    header, *rows = all_data
    df = pd.DataFrame(rows, columns=header)

    # Optionally clean whitespace
    df.columns = [col.strip() for col in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Smart type conversion only on likely columns
    for col in df.columns:
        col_lower = col.lower()

        if "date" in col_lower or "time" in col_lower:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif any(keyword in col_lower for keyword in ["price", "size", "amount", "value"]):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def replace_full_table(
    data: pd.DataFrame,
    sheet_id: str,
    sheet_index: int = 0,
) -> None:
    """
    Replaces all data in a Google Sheet worksheet with the provided DataFrame.
    
    Parameters:
    - data: pandas DataFrame to upload
    - sheet_id: The unique Google Sheet ID
    - sheet_index: Index of the worksheet/tab (default is 0)
    """

    if data.empty:
        raise ValueError("DataFrame is empty. Aborting write operation.")

    if GOOGLE_SREVICE_JSON_KEY:
        creds_dict = base64_decoder.decode_base64_to_json(GOOGLE_SREVICE_JSON_KEY)
    else:
        raise ValueError("Missing GOOGLE_SERVICE_JSON_KEY environment variable.")
    
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.get_worksheet(sheet_index)

    # Clear existing content
    worksheet.clear()

    # Prepare data for upload
    rows = [list(data.columns)] + data.astype(str).values.tolist()

    # Update with new data
    worksheet.update(rows)
    print("✅ Google Sheet updated successfully.")


def append_row_to_sheet(
    data: pd.DataFrame,
    sheet_id: str,
    sheet_index: int = 0,
) -> None:
    """
    Appends rows from a DataFrame to a specified Google Sheet.

    Parameters:
    - data: pd.DataFrame
    - sheet_id: The unique Google Sheet ID (from URL)
    - sheet_index: Index of the worksheet (default = 0 for first sheet)
    - credentials_path: Path to the service account JSON file
    """
    if GOOGLE_SREVICE_JSON_KEY:
        credentials_path = base64_decoder.decode_base64_to_json(GOOGLE_SREVICE_JSON_KEY)
    print(f"Using credentials from: {credentials_path}")
    
    if not isinstance(data, pd.DataFrame):
        raise ValueError("`data` must be a pandas DataFrame")

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = base64_decoder.decode_base64_to_json(GOOGLE_SREVICE_JSON_KEY)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.get_worksheet(sheet_index)

    header = worksheet.row_values(1)
    num_columns = len(header)

    # Clean all data rows at once
    cleaned_rows = []
    for _, row in data.iterrows():
        row_values = [clean_value(v) for v in row.tolist()]
        if len(row_values) < num_columns:
            row_values += [None] * (num_columns - len(row_values))
        elif len(row_values) > num_columns:
            row_values = row_values[:num_columns]
        cleaned_rows.append(row_values)

    # Batch append
    worksheet.append_rows(cleaned_rows, value_input_option="USER_ENTERED")

    logging.info(f"Appended {len(data)} rows to sheet {sheet_id} at index {sheet_index}.")

if __name__ == "__main__":
    # Example usage
    # columsn
    # address_full	street	price	squared_m2	price_per_squared_m2	is_available	note	date_scraped	link	available_from	rental_company	is_new
    df = pd.DataFrame({
        "address_full": ["Damstraat 1", "Singel 2"],
        "street": ["Damstraat", "Singel"],
        "price": [1200, 1500],
        "squared_m2": [50, 60],
        "price_per_squared_m2": [24, '"'],
        "is_available": [True, False],
        "note": ["Nice place", "Available soon"],
        "date_scraped": [pd.Timestamp.now(), pd.Timestamp.now()],
        "link": ["http://example.com/1", "http://example.com/2"],
        "available_from": [None, None],
        "rental_company": ["Test Company", "Test Company"],
    })
    
    # append_row_to_sheet(
    #     data=df,
    #     sheet_id="1rWa4ExIS3I7S4eb-jTp8CuJk-NXVV7BeEp2k_drWAUc"
    # )

    df = read_sheet_to_df(GEOCODED_STREETS, 0)
    df = read_sheet_to_df(RENTAL_DB, 0)