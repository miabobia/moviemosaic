"""
Dataclass for storing movie data taken from fetch_data.py
"""
from dataclasses import dataclass

@dataclass
class MovieCell:
    title: str
    director: str
    rating: int
    im_path: str