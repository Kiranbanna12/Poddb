"""
YouTube sync management queries
"""
import time
from typing import Optional, Dict, List, Any
from .db import get_db_connection


def get_all_synced_playlists(
    podcast_id: Optional[int] = None,
    auto_sync_only: bool = False,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get all synced playlists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            pp.*,
            p.title as podcast_title,
            p.cover_image as podcast_cover,
            p.status as podcast_status
        FROM podcast_playlists pp
        LEFT JOIN podcasts p ON pp.podcast_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if podcast_id:
        query += ' AND pp.podcast_id = ?'
        params.append(podcast_id)
    
    if auto_sync_only:
        query += ' AND pp.auto_sync_enabled = 1'
    
    query += ' ORDER BY pp.last_synced_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    playlists = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return playlists


def get_playlist_sync_history(
    podcast_id: Optional[int] = None,
    playlist_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get sync history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            sh.*,
            p.title as podcast_title
        FROM sync_history sh
        LEFT JOIN podcasts p ON sh.podcast_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if podcast_id:
        query += ' AND sh.podcast_id = ?'
        params.append(podcast_id)
    
    if playlist_id:
        query += ' AND sh.playlist_id = ?'
        params.append(playlist_id)
    
    query += ' ORDER BY sh.synced_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history


def create_sync_history_entry(
    podcast_id: int,
    playlist_id: str,
    sync_status: str,
    episodes_added: int = 0,
    episodes_updated: int = 0,
    error_message: Optional[str] = None,
    sync_duration: Optional[int] = None
) -> int:
    """Create sync history entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sync_history 
        (podcast_id, playlist_id, sync_status, episodes_added, episodes_updated, error_message, sync_duration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (podcast_id, playlist_id, sync_status, episodes_added, episodes_updated, error_message, sync_duration))
    
    history_id = cursor.lastrowid
    
    # Update last_synced_at in podcast_playlists
    cursor.execute('''
        UPDATE podcast_playlists
        SET last_synced_at = ?
        WHERE podcast_id = ? AND playlist_id = ?
    ''', (int(time.time()), podcast_id, playlist_id))
    
    conn.commit()
    conn.close()
    return history_id


def update_playlist_sync_settings(
    playlist_table_id: int,
    auto_sync_enabled: Optional[bool] = None,
    sync_frequency: Optional[str] = None
) -> bool:
    """Update playlist sync settings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if auto_sync_enabled is not None:
        updates.append('auto_sync_enabled = ?')
        params.append(1 if auto_sync_enabled else 0)
    
    if sync_frequency:
        updates.append('sync_frequency = ?')
        params.append(sync_frequency)
    
    if not updates:
        conn.close()
        return False
    
    params.append(playlist_table_id)
    query = f'UPDATE podcast_playlists SET {", ".join(updates)} WHERE id = ?'
    
    cursor.execute(query, params)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def get_sync_statistics() -> Dict[str, Any]:
    """Get sync statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total playlists
    cursor.execute('SELECT COUNT(*) FROM podcast_playlists')
    total_playlists = cursor.fetchone()[0]
    
    # Auto-sync enabled
    cursor.execute('SELECT COUNT(*) FROM podcast_playlists WHERE auto_sync_enabled = 1')
    auto_sync_enabled = cursor.fetchone()[0]
    
    # Total syncs today
    today_start = int(time.time()) - 86400
    cursor.execute('SELECT COUNT(*) FROM sync_history WHERE synced_at >= ?', (today_start,))
    syncs_today = cursor.fetchone()[0]
    
    # Successful syncs today
    cursor.execute('''
        SELECT COUNT(*) FROM sync_history 
        WHERE synced_at >= ? AND sync_status = 'success'
    ''', (today_start,))
    successful_syncs_today = cursor.fetchone()[0]
    
    # Failed syncs today
    cursor.execute('''
        SELECT COUNT(*) FROM sync_history 
        WHERE synced_at >= ? AND sync_status = 'failed'
    ''', (today_start,))
    failed_syncs_today = cursor.fetchone()[0]
    
    # Total episodes synced today
    cursor.execute('''
        SELECT SUM(episodes_added) FROM sync_history WHERE synced_at >= ?
    ''', (today_start,))
    result = cursor.fetchone()[0]
    episodes_synced_today = result if result else 0
    
    conn.close()
    
    return {
        'total_playlists': total_playlists,
        'auto_sync_enabled': auto_sync_enabled,
        'syncs_today': syncs_today,
        'successful_syncs_today': successful_syncs_today,
        'failed_syncs_today': failed_syncs_today,
        'episodes_synced_today': episodes_synced_today
    }


def delete_playlist_sync(playlist_table_id: int) -> bool:
    """Delete playlist sync configuration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM podcast_playlists WHERE id = ?', (playlist_table_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
