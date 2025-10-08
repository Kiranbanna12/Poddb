from pydantic import BaseModel
from typing import Optional

class EpisodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    youtube_video_id: Optional[str] = None
    thumbnail: Optional[str] = None
    episode_number: Optional[int] = None
    duration: Optional[str] = None
    published_date: Optional[int] = None

class EpisodeCreate(EpisodeBase):
    podcast_id: int

class Episode(EpisodeBase):
    id: int
    podcast_id: int
    views: int = 0
    likes: int = 0
    comments: int = 0
    created_at: int
    podcast_title: Optional[str] = None

    class Config:
        from_attributes = True