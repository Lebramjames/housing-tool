# %%
import pandas as pd
import re
from typing import Optional

def prepare_address_fields(df: pd.DataFrame, full_address_col: str = "full_adres") -> pd.DataFrame:
    """
    Extracts street, number_extension, and city from a 'full_adres' column.
    Constructs a cleaned 'full_address_processed' column for geocoding.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame containing a column with full addresses.
        full_address_col (str): Name of the column that contains the full address string.
        
    Returns:
        pd.DataFrame: The original DataFrame with added columns:
                      'street', 'number_extension', 'city', 'full_address_processed'
    """

    

    def split_address(addr):
        if not isinstance(addr, str):
            return pd.Series([None, None, None])
        
        city = None
        addr_wo_postal = addr
        if ' in ' in addr_wo_postal:
            city = addr_wo_postal.split(' in ')[-1].strip()
            addr_wo_postal = ' in '.join(addr_wo_postal.split(' in ')[:-1]).strip()
        elif ',' in addr_wo_postal:
            city = addr_wo_postal.split(',')[-1].strip()
            addr_wo_postal = ','.join(addr_wo_postal.split(',')[:-1]).strip()

        # Extract street and number
        match = re.search(r'(\D*?)(\d.*)', addr_wo_postal)
        if match:
            street = match.group(1).strip()
            number_extension = match.group(2).strip()
        else:
            street = addr_wo_postal.strip()
            number_extension = None

        return pd.Series([street, number_extension, city])

    # Apply address splitting
    df[['street', 'number_extension', 'city']] = df[full_address_col].apply(split_address)

    # Clean up number_extension and fill missing city
    df['number_extension'] = (
        df['number_extension']
        .replace('Amsterdam', '')
        .str.replace(r'\bAmsterdam\b', '', regex=True)
        .str.strip()
    )

    df['city'] = df['city'].fillna('Amsterdam')

    # Compose full address for geocoding
    df['full_address_processed'] = df.apply(
        lambda row: ' '.join(filter(None, [row['street'], row['number_extension'], row['city']])),
        axis=1
    )
    # df['full_address_streets'] here we add the street and city only
    df['full_address_streets'] = df.apply(
        lambda row: ' '.join(filter(None, [row['street'], row['city']])),
        axis=1
    )

    # drop duplicate rows for full_address_processed
    df = df.drop_duplicates(subset='full_address_processed')

    return df

