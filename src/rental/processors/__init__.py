# %%
# from src.rental.processors.neighborhood_processor import run_pipeline as run_nbh_processor
from src.rental.processors.coordinate_finder import run_pipeline as run_coordinate_finder

__all__ = ["run_coordinate_finder"]