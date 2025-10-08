"""Person (Team Member) Models"""
from pydantic import BaseModel, Field
from typing import Optional, List


class PersonBase(BaseModel):
    full_name: str
    bio: Optional[str] = None
    role: str = "Host"  # Host, Guest, Producer, Editor, Other
    location: Optional[str] = None
    date_of_birth: Optional[int] = None  # Unix timestamp
    instagram_url: Optional[str] = None
    youtube_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None


class PersonCreate(PersonBase):
    profile_photo_url: Optional[str] = None  # URL or base64
    profile_photo_path: Optional[str] = None  # Cloudinary URL after upload


class PersonUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    date_of_birth: Optional[int] = None
    profile_photo_path: Optional[str] = None
    instagram_url: Optional[str] = None
    youtube_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None


class Person(PersonBase):
    id: int
    slug: str
    profile_photo_path: Optional[str] = None
    created_at: int


class PersonWithEpisodes(Person):
    """Person with episode assignment"""
    episode_ids: List[int] = []


class PersonSearch(BaseModel):
    """Search result for person"""
    id: int
    slug: str
    full_name: str
    role: str
    profile_photo_path: Optional[str] = None
