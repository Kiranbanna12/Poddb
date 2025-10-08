"""
Admin routes for contribution review and content management
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import time

from ..middleware.admin_middleware import verify_admin, verify_super_admin, get_user_from_token
from ..database import admin_queries, sync_queries
from ..database.queries import (
    create_podcast, create_episode, create_person,
    get_podcast_by_id, get_episode_by_id, get_person_by_id
)
from ..services.email_service import (
    send_contribution_approved_email,
    send_contribution_rejected_email,
    send_content_updated_email
)

router = APIRouter(prefix="/admin", tags=["Admin Content Management"])

# ============================================
# PYDANTIC MODELS
# ============================================

class ContributionStatusUpdate(BaseModel):
    status: str
    rejection_reason: Optional[str] = None
    admin_notes: Optional[str] = None

class PartialApprovalField(BaseModel):
    field_name: str
    action: str  # 'approve', 'reject', 'modify'
    admin_value: Optional[str] = None
    rejection_reason: Optional[str] = None

class PartialApproval(BaseModel):
    fields: List[PartialApprovalField]

class PodcastUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None

class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    season_title: Optional[str] = None

class PersonUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    instagram_url: Optional[str] = None
    youtube_url: Optional[str] = None
    twitter_url: Optional[str] = None

class SyncSettingsUpdate(BaseModel):
    auto_sync_enabled: Optional[bool] = None
    sync_frequency: Optional[str] = None

# ============================================
# CONTRIBUTION REVIEW ENDPOINTS
# ============================================

@router.get("/contributions/stats")
async def get_contribution_statistics(admin = Depends(verify_admin)):
    """Get contribution statistics for dashboard"""
    stats = admin_queries.get_contribution_stats()
    return {"success": True, "stats": stats}

@router.get("/contributions")
async def get_contributions(
    status: Optional[str] = None,
    contribution_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = 'created_at',
    sort_order: str = 'DESC',
    admin = Depends(verify_admin)
):
    """Get contributions with filters"""
    offset = (page - 1) * limit
    contributions = admin_queries.get_contributions(
        status=status,
        contribution_type=contribution_type,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {"success": True, "contributions": contributions, "page": page, "limit": limit}

@router.get("/contributions/{contribution_id}")
async def get_contribution_details(contribution_id: int, admin = Depends(verify_admin)):
    """Get detailed contribution data"""
    contribution = admin_queries.get_contribution_by_id(contribution_id)
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    
    # Detect similar podcasts if it's a new podcast contribution
    similar_podcasts = []
    if contribution['contribution_type'] == 'new_podcast':
        submitted_data = contribution.get('submitted_data', {})
        title = submitted_data.get('title', '')
        youtube_channel = submitted_data.get('youtube_playlist_id', '')
        similar_podcasts = admin_queries.detect_similar_podcasts(title, youtube_channel)
    
    return {
        "success": True,
        "contribution": contribution,
        "similar_podcasts": similar_podcasts
    }

@router.post("/contributions/{contribution_id}/approve")
async def approve_contribution(
    contribution_id: int,
    request: Request,
    admin = Depends(verify_admin)
):
    """Approve contribution and create entities"""
    admin_user_id = admin.get('user_id')
    
    # Get contribution
    contribution = admin_queries.get_contribution_by_id(contribution_id)
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    
    if contribution['status'] != 'pending' and contribution['status'] != 'in_review':
        raise HTTPException(status_code=400, detail="Contribution already processed")
    
    try:
        submitted_data = contribution['submitted_data']
        created_entities = {}
        
        # Create entities based on contribution type
        if contribution['contribution_type'] == 'new_podcast':
            # Create podcast
            podcast_id = create_podcast(submitted_data, contribution['user_id'])
            created_entities['podcast_id'] = podcast_id
            
            # Update contribution with podcast_id
            admin_queries.update_contribution_status(
                contribution_id,
                'approved',
                admin_user_id,
                admin_notes="Approved - Podcast created successfully"
            )
            
            # Send approval email
            send_contribution_approved_email(
                contribution['submitter_email'],
                contribution['submitter_name'] or contribution['submitter_username'],
                submitted_data.get('title', 'Your Podcast'),
                podcast_id
            )
            
            # Create in-app notification
            admin_queries.create_notification(
                contribution['user_id'],
                'contribution_approved',
                'Podcast Approved!',
                f"Your podcast '{submitted_data.get('title')}' has been approved and is now live!",
                f"/podcast/{podcast_id}"
            )
        
        # Log admin activity
        admin_queries.log_admin_activity(
            admin_user_id,
            'approve_contribution',
            'contribution',
            contribution_id,
            {'created_entities': created_entities},
            request.client.host if request.client else None,
            request.headers.get('user-agent')
        )
        
        return {
            "success": True,
            "message": "Contribution approved successfully",
            "created_entities": created_entities
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve contribution: {str(e)}")

@router.post("/contributions/{contribution_id}/reject")
async def reject_contribution(
    contribution_id: int,
    status_update: ContributionStatusUpdate,
    request: Request,
    admin = Depends(verify_admin)
):
    """Reject contribution with reason"""
    admin_user_id = admin.get('user_id')
    
    # Get contribution
    contribution = admin_queries.get_contribution_by_id(contribution_id)
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    
    if not status_update.rejection_reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    
    # Update status
    success = admin_queries.update_contribution_status(
        contribution_id,
        'rejected',
        admin_user_id,
        status_update.rejection_reason,
        status_update.admin_notes
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update contribution status")
    
    # Send rejection email
    submitted_data = contribution['submitted_data']
    send_contribution_rejected_email(
        contribution['submitter_email'],
        contribution['submitter_name'] or contribution['submitter_username'],
        submitted_data.get('title', 'Your Submission'),
        status_update.rejection_reason,
        status_update.admin_notes or ''
    )
    
    # Create in-app notification
    admin_queries.create_notification(
        contribution['user_id'],
        'contribution_rejected',
        'Submission Needs Changes',
        f"Your submission requires some changes. Reason: {status_update.rejection_reason[:100]}",
        f"/contributions/{contribution_id}"
    )
    
    # Log admin activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'reject_contribution',
        'contribution',
        contribution_id,
        {'rejection_reason': status_update.rejection_reason},
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Contribution rejected successfully"}

@router.put("/contributions/{contribution_id}/status")
async def update_contribution_status_endpoint(
    contribution_id: int,
    status_update: ContributionStatusUpdate,
    request: Request,
    admin = Depends(verify_admin)
):
    """Update contribution status (in_review, etc.)"""
    admin_user_id = admin.get('user_id')
    
    success = admin_queries.update_contribution_status(
        contribution_id,
        status_update.status,
        admin_user_id,
        status_update.rejection_reason,
        status_update.admin_notes
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update contribution status")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'update_contribution_status',
        'contribution',
        contribution_id,
        {'new_status': status_update.status},
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Status updated successfully"}

# ============================================
# CONTENT MANAGEMENT - PODCASTS
# ============================================

@router.get("/podcasts")
async def get_all_podcasts(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = 'created_at',
    sort_order: str = 'DESC',
    admin = Depends(verify_admin)
):
    """Get all podcasts with filters"""
    offset = (page - 1) * limit
    podcasts = admin_queries.get_all_podcasts_admin(
        search=search,
        category_id=category_id,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {"success": True, "podcasts": podcasts, "page": page, "limit": limit}

@router.get("/podcasts/{podcast_id}")
async def get_podcast_details(podcast_id: int, admin = Depends(verify_admin)):
    """Get complete podcast details"""
    podcast = admin_queries.get_podcast_full_details(podcast_id)
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return {"success": True, "podcast": podcast}

@router.put("/podcasts/{podcast_id}")
async def update_podcast(
    podcast_id: int,
    update_data: PodcastUpdate,
    request: Request,
    admin = Depends(verify_admin)
):
    """Update podcast data"""
    admin_user_id = admin.get('user_id')
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    success = admin_queries.update_podcast_admin(podcast_id, update_dict)
    
    if not success:
        raise HTTPException(status_code=404, detail="Podcast not found or update failed")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'update_podcast',
        'podcast',
        podcast_id,
        update_dict,
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Podcast updated successfully"}

@router.delete("/podcasts/{podcast_id}")
async def delete_podcast(
    podcast_id: int,
    permanent: bool = False,
    request: Request,
    admin = Depends(verify_super_admin if permanent else verify_admin)
):
    """Delete or archive podcast"""
    admin_user_id = admin.get('user_id')
    
    success = admin_queries.delete_podcast_admin(podcast_id, permanent)
    
    if not success:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'delete_podcast' if permanent else 'archive_podcast',
        'podcast',
        podcast_id,
        {'permanent': permanent},
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": f"Podcast {'deleted permanently' if permanent else 'archived'} successfully"}

# ============================================
# CONTENT MANAGEMENT - EPISODES
# ============================================

@router.get("/episodes")
async def get_all_episodes(
    podcast_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    admin = Depends(verify_admin)
):
    """Get all episodes with filters"""
    offset = (page - 1) * limit
    episodes = admin_queries.get_all_episodes_admin(
        podcast_id=podcast_id,
        search=search,
        limit=limit,
        offset=offset
    )
    return {"success": True, "episodes": episodes, "page": page, "limit": limit}

@router.put("/episodes/{episode_id}")
async def update_episode(
    episode_id: int,
    update_data: EpisodeUpdate,
    request: Request,
    admin = Depends(verify_admin)
):
    """Update episode data"""
    admin_user_id = admin.get('user_id')
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    success = admin_queries.update_episode_admin(episode_id, update_dict)
    
    if not success:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'update_episode',
        'episode',
        episode_id,
        update_dict,
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Episode updated successfully"}

@router.delete("/episodes/{episode_id}")
async def delete_episode(
    episode_id: int,
    request: Request,
    admin = Depends(verify_admin)
):
    """Delete episode"""
    admin_user_id = admin.get('user_id')
    
    success = admin_queries.delete_episode_admin(episode_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'delete_episode',
        'episode',
        episode_id,
        {},
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Episode deleted successfully"}

# ============================================
# CONTENT MANAGEMENT - PEOPLE
# ============================================

@router.get("/people")
async def get_all_people(
    role: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    admin = Depends(verify_admin)
):
    """Get all people with filters"""
    offset = (page - 1) * limit
    people = admin_queries.get_all_people_admin(
        role=role,
        search=search,
        limit=limit,
        offset=offset
    )
    return {"success": True, "people": people, "page": page, "limit": limit}

@router.put("/people/{person_id}")
async def update_person(
    person_id: int,
    update_data: PersonUpdate,
    request: Request,
    admin = Depends(verify_admin)
):
    """Update person data"""
    admin_user_id = admin.get('user_id')
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    success = admin_queries.update_person_admin(person_id, update_dict)
    
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'update_person',
        'person',
        person_id,
        update_dict,
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Person updated successfully"}

@router.delete("/people/{person_id}")
async def delete_person(
    person_id: int,
    request: Request,
    admin = Depends(verify_admin)
):
    """Delete person"""
    admin_user_id = admin.get('user_id')
    
    success = admin_queries.delete_person_admin(person_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'delete_person',
        'person',
        person_id,
        {},
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Person deleted successfully"}

@router.post("/people/merge")
async def merge_people(
    person_id1: int,
    person_id2: int,
    request: Request,
    admin = Depends(verify_super_admin)
):
    """Merge two person records"""
    admin_user_id = admin.get('user_id')
    
    success = admin_queries.merge_people(person_id1, person_id2)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to merge people")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'merge_people',
        'person',
        person_id1,
        {'merged_from': person_id2},
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "People merged successfully"}

# ============================================
# SYNC MANAGEMENT
# ============================================

@router.get("/sync/stats")
async def get_sync_statistics(admin = Depends(verify_admin)):
    """Get sync statistics"""
    stats = sync_queries.get_sync_statistics()
    return {"success": True, "stats": stats}

@router.get("/sync/playlists")
async def get_synced_playlists(
    podcast_id: Optional[int] = None,
    auto_sync_only: bool = False,
    page: int = 1,
    limit: int = 50,
    admin = Depends(verify_admin)
):
    """Get all synced playlists"""
    offset = (page - 1) * limit
    playlists = sync_queries.get_all_synced_playlists(
        podcast_id=podcast_id,
        auto_sync_only=auto_sync_only,
        limit=limit,
        offset=offset
    )
    return {"success": True, "playlists": playlists, "page": page, "limit": limit}

@router.get("/sync/history")
async def get_sync_history(
    podcast_id: Optional[int] = None,
    playlist_id: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    admin = Depends(verify_admin)
):
    """Get sync history"""
    offset = (page - 1) * limit
    history = sync_queries.get_playlist_sync_history(
        podcast_id=podcast_id,
        playlist_id=playlist_id,
        limit=limit,
        offset=offset
    )
    return {"success": True, "history": history, "page": page, "limit": limit}

@router.put("/sync/playlists/{playlist_id}/settings")
async def update_sync_settings(
    playlist_id: int,
    settings: SyncSettingsUpdate,
    request: Request,
    admin = Depends(verify_admin)
):
    """Update playlist sync settings"""
    admin_user_id = admin.get('user_id')
    
    success = sync_queries.update_playlist_sync_settings(
        playlist_id,
        settings.auto_sync_enabled,
        settings.sync_frequency
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'update_sync_settings',
        'playlist',
        playlist_id,
        settings.dict(),
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Sync settings updated successfully"}

@router.delete("/sync/playlists/{playlist_id}")
async def delete_playlist_sync(
    playlist_id: int,
    request: Request,
    admin = Depends(verify_admin)
):
    """Delete playlist sync configuration"""
    admin_user_id = admin.get('user_id')
    
    success = sync_queries.delete_playlist_sync(playlist_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Playlist sync not found")
    
    # Log activity
    admin_queries.log_admin_activity(
        admin_user_id,
        'delete_playlist_sync',
        'playlist',
        playlist_id,
        {},
        request.client.host if request.client else None,
        request.headers.get('user-agent')
    )
    
    return {"success": True, "message": "Playlist sync deleted successfully"}

# ============================================
# ADMIN ACTIVITY LOGS
# ============================================

@router.get("/activity-logs")
async def get_activity_logs(
    admin_user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
    admin = Depends(verify_admin)
):
    """Get admin activity logs"""
    offset = (page - 1) * limit
    logs = admin_queries.get_admin_activity_logs(
        admin_user_id=admin_user_id,
        action_type=action_type,
        limit=limit,
        offset=offset
    )
    return {"success": True, "logs": logs, "page": page, "limit": limit}

# ============================================
# NOTIFICATIONS
# ============================================

@router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    current_user = Depends(get_user_from_token)
):
    """Get user notifications"""
    user_id = current_user.get('user_id')
    notifications = admin_queries.get_user_notifications(user_id, unread_only)
    return {"success": True, "notifications": notifications}

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_user_from_token)
):
    """Mark notification as read"""
    success = admin_queries.mark_notification_read(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True, "message": "Notification marked as read"}

@router.put("/notifications/read-all")
async def mark_all_notifications_read(current_user = Depends(get_user_from_token)):
    """Mark all notifications as read"""
    user_id = current_user.get('user_id')
    success = admin_queries.mark_all_notifications_read(user_id)
    return {"success": True, "message": "All notifications marked as read"}
