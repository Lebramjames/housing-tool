# %%
# main.py or similar

import argparse
from rental.main import process_rental_main

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arg", help="Which process to run (e.g., 'rental')")

    args = parser.parse_args()

    if args.arg == "rental":
        process_rental_main()
    else:
        raise ValueError(f"Unknown argument: {args.arg}")

if __name__ == "__main__":
    main()