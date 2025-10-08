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
        
        # Create JWT token
        token = create_access_token({"user_id": new_user['id'], "email": new_user['email']})
        
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
        # Get user by email
        user = queries.get_user_by_email(credentials.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        # Create JWT token
        token = create_access_token({"user_id": user['id'], "email": user['email']})
        
        return {
            "user": user,
            "token": token
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
