# %%

import logging


# from src.rental import vbt_huren
# from src.rental import bouwinvest
# from src.rental import vesteda
# from src.rental import send_email
# from src.rental import ikwilhuren

import send_email
import vbt_huren
import bouwinvest
import vesteda
import ikwilhuren

def process_rental_main():

    vbt_huren.run_pipeline(local=False)
    send_email.run_pipeline(rental_company='vbt_huren')

    bouwinvest.run_pipeline(local=False)
    send_email.run_pipeline(rental_company='bouwinvest')

    vesteda.run_pipeline(local=False)
    send_email.run_pipeline(rental_company='vesteda')

    ikwilhuren.run_pipeline(local=False)
    send_email.run_pipeline(rental_company='ikwilhuren')

if __name__ == "__main__":
    process_rental_main()


