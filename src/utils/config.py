# %%
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DIR = os.path.join(BASE_DIR, "src")

GEOCODED_STREETS = '1SIeXyyWx1t7Kywip5Micqhl14witEf4cOMHx-mFbFL4'
RENTAL_DB = '1rWa4ExIS3I7S4eb-jTp8CuJk-NXVV7BeEp2k_drWAUc'

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

