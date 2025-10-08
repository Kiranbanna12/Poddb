from pydantic import BaseModel
from typing import Optional, Dict, Any

class ContributionCreate(BaseModel):
    title: str
    description: str
    youtube_playlist_id: str
    categories: list[str]
    languages: list[str]
    location: Optional[str] = None
    website: Optional[str] = None
    spotify_url: Optional[str] = None
    apple_podcasts_url: Optional[str] = None
    jiosaavn_url: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None
    team_members: list[Dict[str, Any]] = []
    cover_image: Optional[str] = None

class Contribution(BaseModel):
    id: int
    user_id: int
    podcast_id: Optional[int] = None
    type: str = 'new'
    status: str = 'pending'
    rejection_reason: Optional[str] = None
    created_at: int
    reviewed_at: Optional[int] = None
    reviewer_id: Optional[int] = None

    class Config:
        from_attributes = True