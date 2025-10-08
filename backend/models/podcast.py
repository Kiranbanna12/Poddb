from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PodcastBase(BaseModel):
    title: str
    description: Optional[str] = None
    youtube_playlist_id: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    cover_image: Optional[str] = None

class PodcastCreate(PodcastBase):
    categories: List[str] = []
    languages: List[str] = []

class PodcastUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    cover_image: Optional[str] = None

class Podcast(PodcastBase):
    id: int
    slug: str
    rating: float = 0.0
    total_ratings: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0
    episode_count: int = 0
    status: str = 'pending'
    created_at: int
    updated_at: int
    categories: List[str] = []
    languages: List[str] = []

    class Config:
        from_attributes = True

class PodcastWithDetails(Podcast):
    episodes: List = []
    team_members: List = []