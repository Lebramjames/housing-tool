# %% Combiner: 
import pandas as pd

def retreve_most_recent_funda_file():
    import os
    import glob

    # Use glob to find all files matching the pattern
    pattern = os.path.join('data', 'funda', 'funda_data_*.csv')
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError("No Funda makelaars files found.")

    # Sort the files by modification time and get the most recent one
    most_recent_file = max(files, key=os.path.getmtime)
    
    return most_recent_file

def retrieve_most_recent_makelaar_file():
    import os
    import glob

    # Get the current working directory
    current_directory = os.getcwd()

    # Use glob to find all files matching the pattern
    pattern = os.path.join('data', 'makelaars', 'makelaar_results_*.csv')
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError("No Makelaars files found.")

    # Sort the files by modification time and get the most recent one
    most_recent_file = max(files, key=os.path.getmtime)
    
    return most_recent_file

most_recent_funda = retreve_most_recent_funda_file()
most_recent_makelaar = retrieve_most_recent_makelaar_file()

df_funda = pd.read_csv(most_recent_funda)
df_makelaar = pd.read_csv(most_recent_makelaar)
