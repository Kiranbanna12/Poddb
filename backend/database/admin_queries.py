"""
Admin-specific database queries for contribution review and content management
"""
import time
import json
from .db import get_db_connection
from typing import Optional, Dict, List, Any


# ============================================
# CONTRIBUTION REVIEW QUERIES
# ============================================

def get_contributions(
    status: Optional[str] = None,
    contribution_type: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = 'created_at',
    sort_order: str = 'DESC'
) -> List[Dict[str, Any]]:
    """Get contributions with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            c.*,
            u.username as submitter_username,
            u.full_name as submitter_name,
            u.avatar_path as submitter_avatar,
            r.username as reviewer_username
        FROM contributions c
        LEFT JOIN users u ON c.user_id = u.id
        LEFT JOIN users r ON c.reviewed_by = r.id
        WHERE 1=1
    '''
    params = []
    
    if status:
        query += ' AND c.status = ?'
        params.append(status)
    
    if contribution_type:
        query += ' AND c.contribution_type = ?'
        params.append(contribution_type)
    
    if user_id:
        query += ' AND c.user_id = ?'
        params.append(user_id)
    
    query += f' ORDER BY c.{sort_by} {sort_order} LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    contributions = [dict(row) for row in cursor.fetchall()]
    
    # Parse submitted_data JSON
    for contrib in contributions:
        if contrib.get('submitted_data'):
            try:
                contrib['submitted_data'] = json.loads(contrib['submitted_data'])
            except:
                pass
    
    conn.close()
    return contributions


def get_contribution_by_id(contribution_id: int) -> Optional[Dict[str, Any]]:
    """Get detailed contribution data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.*,
            u.username as submitter_username,
            u.full_name as submitter_name,
            u.email as submitter_email,
            u.avatar_path as submitter_avatar,
            u.contribution_count,
            r.username as reviewer_username
        FROM contributions c
        LEFT JOIN users u ON c.user_id = u.id
        LEFT JOIN users r ON c.reviewed_by = r.id
        WHERE c.id = ?
    ''', (contribution_id,))
    
    contribution = cursor.fetchone()
    if not contribution:
        conn.close()
        return None
    
    contrib_dict = dict(contribution)
    
    # Parse submitted_data JSON
    if contrib_dict.get('submitted_data'):
        try:
            contrib_dict['submitted_data'] = json.loads(contrib_dict['submitted_data'])
        except:
            pass
    
    conn.close()
    return contrib_dict


def get_contribution_stats() -> Dict[str, int]:
    """Get contribution statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count by status
    cursor.execute('''
        SELECT 
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
            COUNT(CASE WHEN status = 'in_review' THEN 1 END) as in_review,
            COUNT(CASE WHEN status = 'approved' AND reviewed_at >= ? THEN 1 END) as approved_today,
            COUNT(CASE WHEN status = 'rejected' AND reviewed_at >= ? THEN 1 END) as rejected_today,
            AVG(CASE WHEN reviewed_at IS NOT NULL THEN reviewed_at - created_at END) as avg_review_time
        FROM contributions
    ''', (int(time.time()) - 86400, int(time.time()) - 86400))
    
    stats = dict(cursor.fetchone())
    conn.close()
    return stats


def update_contribution_status(
    contribution_id: int,
    status: str,
    admin_user_id: int,
    rejection_reason: Optional[str] = None,
    admin_notes: Optional[str] = None
) -> bool:
    """Update contribution status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_time = int(time.time())
    
    cursor.execute('''
        UPDATE contributions
        SET status = ?, reviewed_by = ?, reviewed_at = ?, 
            rejection_reason = ?, admin_notes = ?, updated_at = ?
        WHERE id = ?
    ''', (status, admin_user_id, current_time, rejection_reason, admin_notes, current_time, contribution_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def detect_similar_podcasts(title: str, youtube_channel: Optional[str] = None) -> List[Dict[str, Any]]:
    """Detect similar podcasts by title or YouTube channel"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    similar = []
    
    # Search by title similarity
    cursor.execute('''
        SELECT id, title, youtube_playlist_id, cover_image, status
        FROM podcasts
        WHERE title LIKE ?
        LIMIT 5
    ''', (f'%{title}%',))
    similar.extend([dict(row) for row in cursor.fetchall()])
    
    # Search by YouTube channel if provided
    if youtube_channel:
        cursor.execute('''
            SELECT id, title, youtube_playlist_id, cover_image, status
            FROM podcasts
            WHERE youtube_playlist_id LIKE ?
            LIMIT 5
        ''', (f'%{youtube_channel}%',))
        similar.extend([dict(row) for row in cursor.fetchall()])
    
    conn.close()
    # Remove duplicates
    seen = set()
    unique_similar = []
    for item in similar:
        if item['id'] not in seen:
            seen.add(item['id'])
            unique_similar.append(item)
    
    return unique_similar


# ============================================
# CONTENT MANAGEMENT QUERIES
# ============================================

def get_all_podcasts_admin(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    language_id: Optional[int] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = 'created_at',
    sort_order: str = 'DESC'
) -> List[Dict[str, Any]]:
    """Get all podcasts with admin filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT DISTINCT p.*
        FROM podcasts p
        WHERE 1=1
    '''
    params = []
    
    if search:
        query += ' AND (p.title LIKE ? OR p.description LIKE ? OR p.slug LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])
    
    if category_id:
        query += ''' AND p.id IN (
            SELECT podcast_id FROM podcast_categories WHERE category_id = ?
        )'''
        params.append(category_id)
    
    if language_id:
        query += ''' AND p.id IN (
            SELECT podcast_id FROM podcast_languages WHERE language_id = ?
        )'''
        params.append(language_id)
    
    if status:
        query += ' AND p.status = ?'
        params.append(status)
    
    if location:
        query += ' AND (p.location LIKE ? OR p.state LIKE ? OR p.country LIKE ?)'
        loc_term = f'%{location}%'
        params.extend([loc_term, loc_term, loc_term])
    
    query += f' ORDER BY p.{sort_by} {sort_order} LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    podcasts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return podcasts


def get_podcast_full_details(podcast_id: int) -> Optional[Dict[str, Any]]:
    """Get complete podcast details with all relationships"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get podcast
    cursor.execute('SELECT * FROM podcasts WHERE id = ?', (podcast_id,))
    podcast = cursor.fetchone()
    if not podcast:
        conn.close()
        return None
    
    podcast_dict = dict(podcast)
    
    # Get categories
    cursor.execute('''
        SELECT c.* FROM categories c
        JOIN podcast_categories pc ON c.id = pc.category_id
        WHERE pc.podcast_id = ?
    ''', (podcast_id,))
    podcast_dict['categories'] = [dict(row) for row in cursor.fetchall()]
    
    # Get languages
    cursor.execute('''
        SELECT l.* FROM languages l
        JOIN podcast_languages pl ON l.id = pl.language_id
        WHERE pl.podcast_id = ?
    ''', (podcast_id,))
    podcast_dict['languages'] = [dict(row) for row in cursor.fetchall()]
    
    # Get people/team
    cursor.execute('''
        SELECT p.*, pp.role FROM people p
        JOIN podcast_people pp ON p.id = pp.person_id
        WHERE pp.podcast_id = ?
    ''', (podcast_id,))
    podcast_dict['team'] = [dict(row) for row in cursor.fetchall()]
    
    # Get platform links
    cursor.execute('''
        SELECT * FROM podcast_platforms WHERE podcast_id = ?
    ''', (podcast_id,))
    podcast_dict['platforms'] = [dict(row) for row in cursor.fetchall()]
    
    # Get episodes count
    cursor.execute('SELECT COUNT(*) as count FROM episodes WHERE podcast_id = ?', (podcast_id,))
    podcast_dict['episode_count'] = cursor.fetchone()[0]
    
    conn.close()
    return podcast_dict


def update_podcast_admin(podcast_id: int, update_data: Dict[str, Any]) -> bool:
    """Update podcast data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    update_data['updated_at'] = int(time.time())
    
    # Build dynamic update query
    fields = []
    values = []
    for key, value in update_data.items():
        if key not in ['id', 'created_at']:
            fields.append(f'{key} = ?')
            values.append(value)
    
    if not fields:
        conn.close()
        return False
    
    values.append(podcast_id)
    query = f'UPDATE podcasts SET {", ".join(fields)} WHERE id = ?'
    
    cursor.execute(query, values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_podcast_admin(podcast_id: int, permanent: bool = False) -> bool:
    """Delete or archive podcast"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if permanent:
        cursor.execute('DELETE FROM podcasts WHERE id = ?', (podcast_id,))
    else:
        cursor.execute('UPDATE podcasts SET status = ? WHERE id = ?', ('archived', podcast_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def get_all_episodes_admin(
    podcast_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get episodes with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT e.*, p.title as podcast_title
        FROM episodes e
        LEFT JOIN podcasts p ON e.podcast_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if podcast_id:
        query += ' AND e.podcast_id = ?'
        params.append(podcast_id)
    
    if search:
        query += ' AND (e.title LIKE ? OR e.description LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term])
    
    query += ' ORDER BY e.created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    episodes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return episodes


def update_episode_admin(episode_id: int, update_data: Dict[str, Any]) -> bool:
    """Update episode data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    fields = []
    values = []
    for key, value in update_data.items():
        if key not in ['id', 'created_at']:
            fields.append(f'{key} = ?')
            values.append(value)
    
    if not fields:
        conn.close()
        return False
    
    values.append(episode_id)
    query = f'UPDATE episodes SET {", ".join(fields)} WHERE id = ?'
    
    cursor.execute(query, values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_episode_admin(episode_id: int) -> bool:
    """Delete episode permanently"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM episodes WHERE id = ?', (episode_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def get_all_people_admin(
    role: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get people with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM people WHERE 1=1'
    params = []
    
    if role:
        query += ' AND role = ?'
        params.append(role)
    
    if search:
        query += ' AND (full_name LIKE ? OR bio LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term])
    
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    people = [dict(row) for row in cursor.fetchall()]
    
    # Get podcast and episode counts for each person
    for person in people:
        cursor.execute('''
            SELECT COUNT(DISTINCT podcast_id) as podcast_count
            FROM podcast_people WHERE person_id = ?
        ''', (person['id'],))
        person['podcast_count'] = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) as episode_count
            FROM episode_guests WHERE person_id = ?
        ''', (person['id'],))
        person['episode_count'] = cursor.fetchone()[0]
    
    conn.close()
    return people


def update_person_admin(person_id: int, update_data: Dict[str, Any]) -> bool:
    """Update person data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    fields = []
    values = []
    for key, value in update_data.items():
        if key not in ['id', 'created_at']:
            fields.append(f'{key} = ?')
            values.append(value)
    
    if not fields:
        conn.close()
        return False
    
    values.append(person_id)
    query = f'UPDATE people SET {", ".join(fields)} WHERE id = ?'
    
    cursor.execute(query, values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_person_admin(person_id: int) -> bool:
    """Delete person permanently"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM people WHERE id = ?', (person_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def merge_people(person_id1: int, person_id2: int) -> bool:
    """Merge two person records"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Transfer all associations to person_id1
        cursor.execute('''
            UPDATE OR IGNORE podcast_people SET person_id = ? WHERE person_id = ?
        ''', (person_id1, person_id2))
        
        cursor.execute('''
            UPDATE OR IGNORE episode_guests SET person_id = ? WHERE person_id = ?
        ''', (person_id1, person_id2))
        
        # Delete person_id2
        cursor.execute('DELETE FROM people WHERE id = ?', (person_id2,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        return False


# ============================================
# ADMIN ACTIVITY LOGGING
# ============================================

def log_admin_activity(
    admin_user_id: int,
    action_type: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    action_details: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> int:
    """Log admin action"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    details_json = json.dumps(action_details) if action_details else None
    
    cursor.execute('''
        INSERT INTO admin_activity_logs 
        (admin_user_id, action_type, entity_type, entity_id, action_details, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (admin_user_id, action_type, entity_type, entity_id, details_json, ip_address, user_agent))
    
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_admin_activity_logs(
    admin_user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get admin activity logs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT l.*, u.username as admin_username
        FROM admin_activity_logs l
        LEFT JOIN users u ON l.admin_user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if admin_user_id:
        query += ' AND l.admin_user_id = ?'
        params.append(admin_user_id)
    
    if action_type:
        query += ' AND l.action_type = ?'
        params.append(action_type)
    
    query += ' ORDER BY l.created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    logs = [dict(row) for row in cursor.fetchall()]
    
    # Parse action_details JSON
    for log in logs:
        if log.get('action_details'):
            try:
                log['action_details'] = json.loads(log['action_details'])
            except:
                pass
    
    conn.close()
    return logs


# ============================================
# NOTIFICATION QUERIES
# ============================================

def create_notification(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    link: Optional[str] = None
) -> int:
    """Create in-app notification"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO notifications (user_id, type, title, message, link)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, notification_type, title, message, link))
    
    notification_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return notification_id


def get_user_notifications(user_id: int, unread_only: bool = False) -> List[Dict[str, Any]]:
    """Get user notifications"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM notifications WHERE user_id = ?'
    params = [user_id]
    
    if unread_only:
        query += ' AND is_read = 0'
    
    query += ' ORDER BY created_at DESC LIMIT 50'
    
    cursor.execute(query, params)
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notifications


def mark_notification_read(notification_id: int) -> bool:
    """Mark notification as read"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def mark_all_notifications_read(user_id: int) -> bool:
    """Mark all user notifications as read"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0', (user_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
