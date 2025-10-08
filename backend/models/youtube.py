"""YouTube Integration Models"""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class YouTubePlaylistRequest(BaseModel):
    playlist_url: str
    max_results: Optional[int] = None  # None = fetch all
    start_index: Optional[int] = 0  # For pagination


class YouTubeVideoRequest(BaseModel):
    video_url: str


class YouTubePlaylistResponse(BaseModel):
    id: str
    title: str
    description: str
    channel_name: str
    thumbnail: str
    item_count: int


class YouTubeVideoResponse(BaseModel):
    video_id: str
    title: str
    description: str
    thumbnail: str
    duration: str
    duration_seconds: int
    published_date: int
    views: int
    likes: int
    comments: int


class EpisodeImportRequest(BaseModel):
    """Request to import episodes"""
    podcast_id: Optional[int] = None
    source_type: str  # 'playlist' or 'video'
    source_url: str
    season_number: Optional[int] = 1
    season_title: Optional[str] = None


class SeasonCreateRequest(BaseModel):
    """Request to create a season"""
    podcast_id: int
    season_number: int
    season_title: Optional[str] = None
    source_type: str  # 'playlist' or 'video'
    source_url: Optional[str] = None


class TeamMemberAssignment(BaseModel):
    """Assign team member to episodes"""
    person_id: int
    episode_ids: List[int]
