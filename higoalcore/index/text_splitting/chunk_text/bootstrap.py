# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Bootstrap definition."""

import os
import nltk
import warnings
from pathlib import Path
from nltk.corpus import wordnet as wn

from higoalutils.config.load_model_info import get_model_info


# Ignore warnings from numba
warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")
warnings.filterwarnings("ignore", message=".*Use no seed for parallelism.*")

_initialized_nltk = False

def bootstrap():
    """Bootstrap definition."""
    global _initialized_nltk
    if _initialized_nltk:
        return
    
    nltk_path = get_model_info().get_by_model_name("nltk").local_path
    if nltk_path:
        nltk_path = Path(nltk_path).resolve()
        nltk_path.mkdir(parents=True, exist_ok=True)
        os.environ["NLTK_DATA"] = str(nltk_path)

    if str(nltk_path) not in nltk.data.path:
        nltk.data.path.insert(0, str(nltk_path))

    pkg = [
        "punkt",
        "punkt_tab",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "maxent_ne_chunker",
        "maxent_ne_chunker_tab",
        "words",
        "wordnet",
    ]
    for p in pkg:
        nltk.download(p, download_dir=str(nltk_path), quiet=True)
    
    wn.ensure_loaded()
    _initialized_nltk = True
