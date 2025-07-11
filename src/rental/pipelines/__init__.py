# %%
# src/rental/pipelines/__init__.py

from src.rental.pipelines.vbt_huren import run_pipeline as run_vbt
from src.rental.pipelines.vesteda import run_pipeline as run_vesteda
from src.rental.pipelines.bouwinvest import run_pipeline as run_bouwinvest
from src.rental.pipelines.ikwilhuren import run_pipeline as run_ikwilhuren

__all__ = ["run_vbt", "run_vesteda", "run_bouwinvest", "run_ikwilhuren"]
