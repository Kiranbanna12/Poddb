from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from typing import Optional, List

# Import database queries
from database import queries
from database.db import init_database, seed_data

# Import models
from models.podcast import Podcast, PodcastCreate
from models.episode import Episode
from models.user import User, UserCreate, UserLogin
from models.contribution import Contribution, ContributionCreate
from models.person import PersonCreate, PersonSearch, PersonWithEpisodes
from models.youtube import (
    YouTubePlaylistRequest, YouTubeVideoRequest, YouTubePlaylistResponse,
    YouTubeVideoResponse, EpisodeImportRequest, SeasonCreateRequest,
    TeamMemberAssignment
)

# Import auth
from auth.password import hash_password, verify_password
from auth.auth import create_access_token, get_current_user_id

# Import services
from services.youtube_service import youtube_service
from services.cloudinary_service import cloudinary_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize database on startup
try:
    init_database()
    seed_data()
except:
    pass  # Already initialized

# Create the main app
app = FastAPI(title="PodDB Pro API")

# Create API router
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Authentication dependency
async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[int]:
    """Get current user from JWT token"""
    if not authorization:
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        user_id = get_current_user_id(token)
        return user_id
    except:
        return None

# Routes

@api_router.get("/")
async def root():
    return {"message": "PodDB Pro API - v1.0"}

# Stats API
@api_router.get("/stats")
async def get_stats():
    """Get platform statistics"""
    try:
        stats = queries.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Podcasts API
@api_router.get("/podcasts")
async def get_podcasts(
    category: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 20
):
    """Get all podcasts with optional filters"""
    try:
        filters = {'limit': limit}
        if category:
            filters['category'] = category
        if language:
            filters['language'] = language
        
        podcasts = queries.get_podcasts(filters)
        return {"podcasts": podcasts, "total": len(podcasts)}
    except Exception as e:
        logger.error(f"Error getting podcasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/podcasts/top")
async def get_top_podcasts(limit: int = 8):
    """Get top rated podcasts"""
    try:
        podcasts = queries.get_podcasts({'limit': limit})
        return podcasts
    except Exception as e:
        logger.error(f"Error getting top podcasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/podcasts/{podcast_id}")
async def get_podcast(podcast_id: int):
    """Get single podcast by ID"""
    try:
        podcast = queries.get_podcast_by_id(podcast_id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")
        return podcast
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/podcasts")
async def create_podcast(podcast: PodcastCreate, user_id: Optional[int] = Depends(get_current_user)):
    """Create a new podcast (requires authentication)"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        podcast_dict = podcast.model_dump()
        new_podcast = queries.create_podcast(podcast_dict, user_id)
        return new_podcast
    except Exception as e:
        logger.error(f"Error creating podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Episodes API
@api_router.get("/episodes")
async def get_episodes(limit: int = 8):
    """Get latest episodes"""
    try:
        episodes = queries.get_episodes({'limit': limit})
        return episodes
    except Exception as e:
        logger.error(f"Error getting episodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/episodes/{episode_id}")
async def get_episode(episode_id: int):
    """Get single episode by ID"""
    try:
        episode = queries.get_episode_by_id(episode_id)
        if not episode:
            raise HTTPException(status_code=404, detail="Episode not found")
        return episode
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting episode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Categories API
@api_router.get("/categories")
async def get_categories():
    """Get all categories"""
    try:
        categories = queries.get_all_categories()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Languages API
@api_router.get("/languages")
async def get_languages():
    """Get all languages"""
    try:
        languages = queries.get_all_languages()
        return languages
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Rankings API
@api_router.get("/rankings/{ranking_type}")
async def get_rankings(
    ranking_type: str,
    category: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 20
):
    """Get rankings (overall/weekly/monthly)"""
    try:
        # For MVP, we'll use overall rankings from podcasts table
        filters = {'limit': limit}
        if category:
            filters['category'] = category
        if language:
            filters['language'] = language
        
        podcasts = queries.get_podcasts(filters)
        
        # Add mock rank changes for frontend
        import random
        for i, podcast in enumerate(podcasts):
            podcast['rank'] = i + 1
            if i == 0:
                podcast['rankChange'] = 2
            elif i == 1:
                podcast['rankChange'] = -1
            elif i == 2:
                podcast['rankChange'] = 0
            else:
                podcast['rankChange'] = random.randint(-5, 5)
        
        return podcasts
    except Exception as e:
        logger.error(f"Error getting rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Authentication API
@api_router.post("/auth/register")
async def register(user: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = queries.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        password_hash = hash_password(user.password)
        new_user = queries.create_user(user.username, user.email, password_hash)
        
        # Remove password_hash from response
        new_user.pop('password_hash', None)
        
        # Create JWT token with role
        token = create_access_token({
            "user_id": new_user['id'], 
            "email": new_user['email'],
            "role": new_user.get('role', 'user')
        })
        
        return {
            "user": new_user,
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """User login"""
    try:
        # Get user by email or username
        user = queries.get_user_by_identifier(credentials.identifier)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email/username or password")
        
        # Verify password
        if not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email/username or password")
        
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        # Create JWT token with role
        token = create_access_token({
            "user_id": user['id'], 
            "email": user['email'],
            "role": user.get('role', 'user')
        })
        
        return {
            "success": True,
            "user": user,
            "token": token,
            "message": "Login successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/me")
async def get_current_user_info(user_id: Optional[int] = Depends(get_current_user)):
    """Get current user info"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        user = queries.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.pop('password_hash', None)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Contributions API
@api_router.post("/contributions")
async def create_contribution(
    contribution: ContributionCreate,
    user_id: Optional[int] = Depends(get_current_user)
):
    """Submit a podcast contribution"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        contribution_dict = contribution.model_dump()
        new_contribution = queries.create_contribution(user_id, contribution_dict)
        return new_contribution
    except Exception as e:
        logger.error(f"Error creating contribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/contributions")
async def get_user_contributions(user_id: Optional[int] = Depends(get_current_user)):
    """Get user's contributions"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        contributions = queries.get_user_contributions(user_id)
        return contributions
    except Exception as e:
        logger.error(f"Error getting contributions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# YouTube API Integration Endpoints

@api_router.post("/youtube/fetch-playlist")
async def fetch_youtube_playlist(request: YouTubePlaylistRequest):
    """Fetch YouTube playlist details and videos"""
    try:
        playlist_id = youtube_service.extract_playlist_id(request.playlist_url)
        if not playlist_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube playlist URL")
        
        # Get playlist details
        playlist_details = youtube_service.get_playlist_details(playlist_id)
        
        # Get all videos
        videos = youtube_service.get_playlist_videos(playlist_id, max_results=100)
        
        # Upload thumbnail to Cloudinary
        try:
            cover_image_result = cloudinary_service.upload_from_url(
                playlist_details['thumbnail'],
                folder="podcasts",
                public_id=f"playlist_{playlist_id}"
            )
            playlist_details['cover_image_cloudinary'] = cover_image_result['secure_url']
        except Exception as e:
            logger.warning(f"Failed to upload playlist thumbnail: {e}")
            playlist_details['cover_image_cloudinary'] = playlist_details['thumbnail']
        
        # Upload episode thumbnails to Cloudinary
        for video in videos:
            try:
                thumbnail_result = cloudinary_service.download_and_upload_youtube_thumbnail(
                    video['thumbnail'],
                    video['video_id'],
                    folder="episodes"
                )
                video['thumbnail_cloudinary'] = thumbnail_result['secure_url']
            except Exception as e:
                logger.warning(f"Failed to upload video thumbnail for {video['video_id']}: {e}")
                video['thumbnail_cloudinary'] = video['thumbnail']
        
        return {
            "playlist": playlist_details,
            "episodes": videos
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching YouTube playlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/youtube/fetch-video")
async def fetch_youtube_video(request: YouTubeVideoRequest):
    """Fetch single YouTube video details"""
    try:
        video_id = youtube_service.extract_video_id(request.video_url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube video URL")
        
        video = youtube_service.get_single_video(video_id)
        
        # Upload thumbnail to Cloudinary
        try:
            thumbnail_result = cloudinary_service.download_and_upload_youtube_thumbnail(
                video['thumbnail'],
                video['video_id'],
                folder="episodes"
            )
            video['thumbnail_cloudinary'] = thumbnail_result['secure_url']
        except Exception as e:
            logger.warning(f"Failed to upload video thumbnail: {e}")
            video['thumbnail_cloudinary'] = video['thumbnail']
        
        return video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching YouTube video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Smart Search Endpoints

@api_router.get("/search/categories")
async def search_categories_endpoint(q: str = "", limit: int = 10):
    """Search categories by name"""
    try:
        if not q:
            categories = queries.get_all_categories()[:limit]
        else:
            categories = queries.search_categories(q, limit)
        return categories
    except Exception as e:
        logger.error(f"Error searching categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/search/categories/add")
async def add_new_category(name: str, description: str = None, icon: str = None):
    """Add a new category"""
    try:
        category = queries.create_category(name, description, icon)
        return category
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/search/languages")
async def search_languages_endpoint(q: str = "", limit: int = 10):
    """Search languages by name"""
    try:
        if not q:
            languages = queries.get_all_languages()[:limit]
        else:
            languages = queries.search_languages(q, limit)
        return languages
    except Exception as e:
        logger.error(f"Error searching languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/search/languages/add")
async def add_new_language(code: str, name: str, native_name: str = None):
    """Add a new language"""
    try:
        language = queries.create_language(code, name, native_name)
        return language
    except Exception as e:
        logger.error(f"Error creating language: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/search/locations")
async def search_locations_endpoint(q: str = "", limit: int = 10):
    """Search locations from existing podcasts"""
    try:
        locations = queries.get_distinct_locations(q, limit)
        return locations
    except Exception as e:
        logger.error(f"Error searching locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/search/locations/add")
async def add_new_location(location: str, state: str = "", country: str = ""):
    """Add a new location (returns the location data for form)"""
    try:
        # For locations, we don't store them separately
        # Just return the formatted location data for the form
        return {
            "location": location,
            "state": state,
            "country": country,
            "name": f"{location}{', ' + state if state else ''}{', ' + country if country else ''}"
        }
    except Exception as e:
        logger.error(f"Error creating location: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/search/people")
async def search_people_endpoint(q: str = "", limit: int = 10):
    """Search people (team members) by name"""
    try:
        if not q:
            people = queries.get_all_people(limit)
        else:
            people = queries.search_people(q, limit)
        return people
    except Exception as e:
        logger.error(f"Error searching people: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# People (Team Members) Endpoints

@api_router.post("/people")
async def create_person_endpoint(person_data: PersonCreate):
    """Create a new person (team member)"""
    try:
        person_dict = person_data.model_dump()
        
        # Handle profile photo upload to Cloudinary
        if person_dict.get('profile_photo_url'):
            try:
                photo_result = cloudinary_service.upload_from_url(
                    person_dict['profile_photo_url'],
                    folder="people",
                    public_id=f"person_{person_dict['full_name'].replace(' ', '_').lower()}"
                )
                person_dict['profile_photo_path'] = photo_result['secure_url']
            except Exception as e:
                logger.warning(f"Failed to upload profile photo: {e}")
                person_dict['profile_photo_path'] = person_dict.get('profile_photo_url')
        
        person = queries.create_person(person_dict)
        return person
    except Exception as e:
        logger.error(f"Error creating person: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/people/{person_id}")
async def get_person_endpoint(person_id: int):
    """Get person by ID"""
    try:
        person = queries.get_person_by_id(person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting person: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/people/{person_id}/episodes")
async def get_person_episodes(person_id: int):
    """Get all episodes where a person appears"""
    try:
        episode_ids = queries.get_episodes_by_person(person_id)
        return {"person_id": person_id, "episode_ids": episode_ids}
    except Exception as e:
        logger.error(f"Error getting person episodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/people/assign-episodes")
async def assign_person_to_episodes_endpoint(assignment: TeamMemberAssignment):
    """Assign a person to multiple episodes"""
    try:
        success = queries.assign_person_to_episodes(assignment.person_id, assignment.episode_ids)
        return {"success": success, "message": f"Person assigned to {len(assignment.episode_ids)} episodes"}
    except Exception as e:
        logger.error(f"Error assigning person to episodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/people/{person_id}/remove-episodes")
async def remove_person_from_episodes_endpoint(person_id: int, episode_ids: List[int]):
    """Remove a person from multiple episodes"""
    try:
        success = queries.remove_person_from_episodes(person_id, episode_ids)
        return {"success": success, "message": f"Person removed from {len(episode_ids)} episodes"}
    except Exception as e:
        logger.error(f"Error removing person from episodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Episode Management Endpoints

@api_router.get("/podcasts/{podcast_id}/episodes")
async def get_podcast_episodes(podcast_id: int):
    """Get all episodes for a podcast"""
    try:
        episodes = queries.get_episodes_by_podcast(podcast_id)
        return episodes
    except Exception as e:
        logger.error(f"Error getting podcast episodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/episodes/import")
async def import_episodes_endpoint(import_request: EpisodeImportRequest):
    """Import episodes from YouTube playlist or single video"""
    try:
        if import_request.source_type == 'playlist':
            playlist_id = youtube_service.extract_playlist_id(import_request.source_url)
            if not playlist_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube playlist URL")
            
            videos = youtube_service.get_playlist_videos(playlist_id, max_results=100)
        elif import_request.source_type == 'video':
            video_id = youtube_service.extract_video_id(import_request.source_url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube video URL")
            
            video = youtube_service.get_single_video(video_id)
            videos = [video]
        else:
            raise HTTPException(status_code=400, detail="Invalid source type")
        
        # Get next episode number if podcast_id provided
        next_episode_num = 1
        if import_request.podcast_id:
            next_episode_num = queries.get_next_episode_number(
                import_request.podcast_id,
                import_request.season_number or 1
            )
        
        # Prepare episodes data
        episodes_data = []
        for i, video in enumerate(videos):
            # Upload thumbnail to Cloudinary
            try:
                thumbnail_result = cloudinary_service.download_and_upload_youtube_thumbnail(
                    video['thumbnail'],
                    video['video_id'],
                    folder="episodes"
                )
                thumbnail_url = thumbnail_result['secure_url']
            except Exception as e:
                logger.warning(f"Failed to upload thumbnail: {e}")
                thumbnail_url = video['thumbnail']
            
            episode_data = {
                'podcast_id': import_request.podcast_id,
                'title': video['title'],
                'description': video['description'],
                'youtube_video_id': video['video_id'],
                'thumbnail': thumbnail_url,
                'episode_number': next_episode_num + i,
                'season_number': import_request.season_number or 1,
                'season_title': import_request.season_title,
                'duration': video['duration'],
                'published_date': video['published_date'],
                'views': video.get('views', 0),
                'likes': video.get('likes', 0),
                'comments': video.get('comments', 0)
            }
            episodes_data.append(episode_data)
        
        # Create episodes in bulk if podcast_id provided
        if import_request.podcast_id:
            created_episodes = queries.create_episodes_bulk(episodes_data)
            
            # Save playlist for auto-sync if it's a playlist import
            if import_request.source_type == 'playlist':
                queries.save_playlist_for_sync(
                    import_request.podcast_id,
                    import_request.source_url,
                    playlist_id
                )
            
            return {
                "success": True,
                "episodes": created_episodes,
                "count": len(created_episodes)
            }
        else:
            # Return episodes data for preview (during contribution)
            return {
                "success": True,
                "episodes": episodes_data,
                "count": len(episodes_data)
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing episodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/episodes")
async def create_episode_endpoint(episode_data: dict):
    """Create a single episode"""
    try:
        # Upload thumbnail to Cloudinary if provided
        if episode_data.get('thumbnail_url'):
            try:
                thumbnail_result = cloudinary_service.upload_from_url(
                    episode_data['thumbnail_url'],
                    folder="episodes"
                )
                episode_data['thumbnail'] = thumbnail_result['secure_url']
            except Exception as e:
                logger.warning(f"Failed to upload thumbnail: {e}")
                episode_data['thumbnail'] = episode_data.get('thumbnail_url')
        
        episode = queries.create_episode(episode_data)
        return episode
    except Exception as e:
        logger.error(f"Error creating episode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/episodes/{episode_id}")
async def delete_episode_endpoint(episode_id: int):
    """Delete an episode"""
    try:
        success = queries.delete_episode(episode_id)
        if not success:
            raise HTTPException(status_code=404, detail="Episode not found")
        return {"success": True, "message": "Episode deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting episode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/episodes/{episode_id}/people")
async def get_episode_people(episode_id: int):
    """Get all people in an episode"""
    try:
        people = queries.get_people_by_episode(episode_id)
        return people
    except Exception as e:
        logger.error(f"Error getting episode people: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Import auth routes
try:
    from routes import auth, profile, admin, admin_content
    api_router.include_router(auth.router)
    api_router.include_router(profile.router)
    api_router.include_router(admin.router)
    api_router.include_router(admin_content.router)
except ImportError as e:
    logger.warning(f"Could not import auth routes: {e}")

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutting down")
