# %%

import logging


# from src.rental import vbt_huren
# from src.rental import bouwinvest
# from src.rental import vesteda
from src.rental import send_email
from src.rental import ikwilhuren

from src.rental import coordinate_finder
from src.rental import neighborhood_processor

# import send_email
# import vbt_huren
# import bouwinvest
# import vesteda
# import ikwilhuren
# import coordinate_finder

def process_rental_main():

    # vbt_huren.run_pipeline(local=False)
    # vesteda.run_pipeline(local=False)
    # ikwilhuren.run_pipeline(local=False)
    # bouwinvest.run_pipeline(local=False)


    # coordinate_finder.run_pipeline()
    # neighborhood_processor.run_pipeline()

    # send_email.run_pipeline(rental_company='vbt_huren')


    # send_email.run_pipeline(rental_company='bouwinvest')
    # send_email.run_pipeline(rental_company='vesteda')

    send_email.run_pipeline(rental_company='ikwilhuren')

if __name__ == "__main__":
    process_rental_main()


