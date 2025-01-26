from typing import List, Optional, Union
from pydantic import BaseModel

class BaseMedia(BaseModel):
    id: Optional[str]  # Change to str to handle MongoDB ObjectId
    name: str
    logo: Optional[str] = None
    path: str
    url: str
        
class Movie(BaseMedia):
    duration: Optional[str] = None  # Duration in seconds
    resolution: Optional[str] = None  # Resolution as a string (e.g., "1920x1080")
    type: Optional[str] = "Movie"
    
class Episode(BaseModel):
    id: Optional[str]  # Add this line if you want to include id
    name: str
    url: Optional[str] = None
    path: str
    season: Optional[str] = None
    episode: Optional[str] = None
    type: Optional[str] = "Episode"
    
class Season(BaseModel):
    season: str
    path: str
    episodes: List[Episode] = []
    type: Optional[str] = "Season"
    
class Series(BaseModel):
    id: Optional[str] = None  # Use str to handle MongoDB ObjectId
    name: str
    image: Optional[str] = None
    path: str  # Add the path attribute
    seasons: List[Season] = []  # Include seasons in the Series model
    type: Optional[str] = "Series"
    duration: Optional[str] = None  # Duration in seconds
    resolution: Optional[str] = None  # Resolution as a string (e.g., "1920x1080")
# Define a type that can be either a Movie, Series, Episode, or Season
MediaItem = Union[Movie, Series, Episode, Season]
