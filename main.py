# %%
# main.py or similar

print(f"Current file path: {os.path.abspath(__file__)}")
print("Files in current directory:")
for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    print(filename)

import argparse
from src.rental.main import process_rental_main
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arg", help="Which process to run (e.g., 'rental')")

    args = parser.parse_args()

    if args.arg == "rental":
        process_rental_main()
    if args.arg == 'buy':
        print("Buy process not implemented yet.")
    else:
        raise ValueError(f"Unknown argument: {args.arg}")

if __name__ == "__main__":
    main()