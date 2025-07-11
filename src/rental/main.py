# %%
import logging

from src.rental.pipelines import *
from src.rental.processors import *
from src.rental.notifications import *
from src.utils import *

# Retrieve __all__ from both modules
from src.rental import pipelines, processors

all_pipelines = getattr(pipelines, '__all__', [])
all_processors = getattr(processors, '__all__', [])

TEMP = False

def process_rental_main():
    run_bouwinvest(local=TEMP)
    run_vesteda(local=TEMP)
    run_ikwilhuren(local=TEMP)
    run_vbt(local=TEMP )

    run_coordinate_finder()

    send_slack()

if __name__ == "__main__":
    process_rental_main()


