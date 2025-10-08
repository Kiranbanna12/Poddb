import time
import json
from typing import Optional, List, Dict, Any
try:
    from .db import get_db_connection
except ImportError:
    from db import get_db_connection

def create_slug(title: str) -> str:
    """Create URL-friendly slug from title"""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug

# Podcast Queries

def create_podcast(data: dict, user_id: int) -> dict:
    """Create a new podcast"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    slug = create_slug(data['title'])
    
    # Check if slug exists, make it unique
    cursor.execute("SELECT COUNT(*) FROM podcasts WHERE slug = ?", (slug,))
    count = cursor.fetchone()[0]
    if count > 0:
        slug = f"{slug}-{now}"
    
    cursor.execute('''
        INSERT INTO podcasts (
            title, slug, description, cover_image, youtube_playlist_id,
            location, state, country, website, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?, ?)
    ''', (
        data['title'], slug, data.get('description'), data.get('cover_image'),
        data.get('youtube_playlist_id'), data.get('location'), data.get('state'),
        data.get('country'), data.get('website'), now, now
    ))
    
    podcast_id = cursor.lastrowid
    
    # Insert categories
    if 'categories' in data and data['categories']:
        for cat_name in data['categories']:
            cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
            cat = cursor.fetchone()
            if cat:
                cursor.execute(
                    "INSERT OR IGNORE INTO podcast_categories (podcast_id, category_id) VALUES (?, ?)",
                    (podcast_id, cat['id'])
                )
    
    # Insert languages
    if 'languages' in data and data['languages']:
        for lang_name in data['languages']:
            cursor.execute("SELECT id FROM languages WHERE name = ?", (lang_name,))
            lang = cursor.fetchone()
            if lang:
                cursor.execute(
                    "INSERT OR IGNORE INTO podcast_languages (podcast_id, language_id) VALUES (?, ?)",
                    (podcast_id, lang['id'])
                )
    
    conn.commit()
    conn.close()
    
    return get_podcast_by_id(podcast_id)

def get_podcasts(filters: dict = None) -> List[dict]:
    """Get podcasts with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM podcasts WHERE status = 'approved'"
    params = []
    
    if filters:
        if 'category' in filters and filters['category']:
            query += ''' AND id IN (
                SELECT podcast_id FROM podcast_categories pc
                JOIN categories c ON pc.category_id = c.id
                WHERE c.name = ?
            )'''
            params.append(filters['category'])
        
        if 'language' in filters and filters['language']:
            query += ''' AND id IN (
                SELECT podcast_id FROM podcast_languages pl
                JOIN languages l ON pl.language_id = l.id
                WHERE l.name = ?
            )'''
            params.append(filters['language'])
    
    query += " ORDER BY rating DESC, views DESC"
    
    if 'limit' in filters:
        query += " LIMIT ?"
        params.append(filters['limit'])
    
    cursor.execute(query, params)
    podcasts = [dict(row) for row in cursor.fetchall()]
    
    # Enrich with categories and languages
    for podcast in podcasts:
        podcast['categories'] = get_podcast_categories(podcast['id'])
        podcast['languages'] = get_podcast_languages(podcast['id'])
    
    conn.close()
    return podcasts

def get_podcast_by_id(podcast_id: int) -> Optional[dict]:
    """Get single podcast by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM podcasts WHERE id = ?", (podcast_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    podcast = dict(row)
    podcast['categories'] = get_podcast_categories(podcast_id)
    podcast['languages'] = get_podcast_languages(podcast_id)
    
    conn.close()
    return podcast

def get_podcast_categories(podcast_id: int) -> List[str]:
    """Get categories for a podcast"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.name FROM categories c
        JOIN podcast_categories pc ON c.id = pc.category_id
        WHERE pc.podcast_id = ?
    ''', (podcast_id,))
    
    categories = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_podcast_languages(podcast_id: int) -> List[str]:
    """Get languages for a podcast"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.name FROM languages l
        JOIN podcast_languages pl ON l.id = pl.language_id
        WHERE pl.podcast_id = ?
    ''', (podcast_id,))
    
    languages = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return languages

# Episode Queries

def create_episode(data: dict) -> dict:
    """Create a new episode"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    
    cursor.execute('''
        INSERT INTO episodes (
            podcast_id, title, description, youtube_video_id, thumbnail,
            episode_number, duration, published_date, views, likes, comments, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['podcast_id'], data['title'], data.get('description'),
        data.get('youtube_video_id'), data.get('thumbnail'),
        data.get('episode_number'), data.get('duration'),
        data.get('published_date'), data.get('views', 0),
        data.get('likes', 0), data.get('comments', 0), now
    ))
    
    episode_id = cursor.lastrowid
    
    # Update podcast episode count
    cursor.execute('''
        UPDATE podcasts SET episode_count = episode_count + 1
        WHERE id = ?
    ''', (data['podcast_id'],))
    
    conn.commit()
    conn.close()
    
    return get_episode_by_id(episode_id)

def get_episodes(filters: dict = None) -> List[dict]:
    """Get episodes with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT e.*, p.title as podcast_title 
        FROM episodes e
        JOIN podcasts p ON e.podcast_id = p.id
        WHERE p.status = 'approved'
        ORDER BY e.created_at DESC
    '''
    params = []
    
    if filters and 'limit' in filters:
        query += " LIMIT ?"
        params.append(filters['limit'])
    
    cursor.execute(query, params)
    episodes = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return episodes

def get_episode_by_id(episode_id: int) -> Optional[dict]:
    """Get single episode by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT e.*, p.title as podcast_title 
        FROM episodes e
        JOIN podcasts p ON e.podcast_id = p.id
        WHERE e.id = ?
    ''', (episode_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

# Category & Language Queries

def get_all_categories() -> List[dict]:
    """Get all categories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(row) for row in cursor.fetchall()]
    
    # Update podcast counts
    for cat in categories:
        cursor.execute('''
            SELECT COUNT(*) as count FROM podcast_categories pc
            JOIN podcasts p ON pc.podcast_id = p.id
            WHERE pc.category_id = ? AND p.status = 'approved'
        ''', (cat['id'],))
        cat['podcast_count'] = cursor.fetchone()['count']
    
    conn.close()
    return categories

def get_all_languages() -> List[dict]:
    """Get all languages"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM languages ORDER BY name")
    languages = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return languages

# Stats Queries

def get_stats() -> dict:
    """Get platform statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM podcasts WHERE status = 'approved'")
    total_podcasts = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM episodes")
    total_episodes = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM people")
    total_people = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'totalPodcasts': total_podcasts,
        'totalEpisodes': total_episodes,
        'totalPeople': total_people
    }

# User Queries

def create_user(username: str, email: str, password_hash: str) -> dict:
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, now))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = dict(cursor.fetchone())
        
        conn.close()
        return user
    except Exception as e:
        conn.close()
        raise e

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

# Contribution Queries

def create_contribution(user_id: int, data: dict) -> dict:
    """Create a new contribution"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    data_json = json.dumps(data)
    
    cursor.execute('''
        INSERT INTO contributions (user_id, type, status, data, created_at)
        VALUES (?, 'new', 'pending', ?, ?)
    ''', (user_id, data_json, now))
    
    contribution_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return get_contribution_by_id(contribution_id)

def get_contribution_by_id(contribution_id: int) -> Optional[dict]:
    """Get contribution by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM contributions WHERE id = ?", (contribution_id,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

def get_user_contributions(user_id: int) -> List[dict]:
    """Get all contributions by a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM contributions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    
    contributions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contributions