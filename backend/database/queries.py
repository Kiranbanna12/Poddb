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

def create_user(username: str, email: str, password_hash: str, full_name: str = None) -> dict:
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, now, now))
        
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

def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

def get_user_by_identifier(identifier: str) -> Optional[dict]:
    """Get user by email or username"""
    # Try email first
    user = get_user_by_email(identifier)
    if user:
        return user
    
    # Try username if email didn't work
    return get_user_by_username(identifier)

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
        INSERT INTO contributions (user_id, contribution_type, status, submitted_data, created_at)
        VALUES (?, 'new_podcast', 'pending', ?, ?)
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


# People (Team Members) Queries

def search_people(search_term: str, limit: int = 10) -> List[dict]:
    """Search people by name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_pattern = f"%{search_term}%"
    cursor.execute('''
        SELECT id, slug, full_name, role, profile_photo_path
        FROM people
        WHERE full_name LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (search_pattern, limit))
    
    people = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return people

def get_person_by_id(person_id: int) -> Optional[dict]:
    """Get person by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM people WHERE id = ?", (person_id,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

def create_person(data: dict) -> dict:
    """Create a new person"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    slug = create_slug(data['full_name'])
    
    # Check if slug exists, make it unique
    cursor.execute("SELECT COUNT(*) FROM people WHERE slug = ?", (slug,))
    count = cursor.fetchone()[0]
    if count > 0:
        slug = f"{slug}-{now}"
    
    cursor.execute('''
        INSERT INTO people (
            full_name, slug, bio, profile_photo_path, role, location,
            date_of_birth, instagram_url, youtube_url, twitter_url,
            facebook_url, linkedin_url, website_url, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['full_name'], slug, data.get('bio'), data.get('profile_photo_path'),
        data.get('role', 'Host'), data.get('location'), data.get('date_of_birth'),
        data.get('instagram_url'), data.get('youtube_url'), data.get('twitter_url'),
        data.get('facebook_url'), data.get('linkedin_url'), data.get('website_url'),
        now
    ))
    
    person_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return get_person_by_id(person_id)

def get_all_people(limit: int = None) -> List[dict]:
    """Get all people"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM people ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    people = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return people

# Episode-Guest (Team Member Assignment) Queries

def assign_person_to_episodes(person_id: int, episode_ids: List[int]) -> bool:
    """Assign a person to multiple episodes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for episode_id in episode_ids:
            cursor.execute('''
                INSERT OR IGNORE INTO episode_guests (episode_id, person_id)
                VALUES (?, ?)
            ''', (episode_id, person_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise e

def remove_person_from_episodes(person_id: int, episode_ids: List[int]) -> bool:
    """Remove a person from multiple episodes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        placeholders = ','.join(['?'] * len(episode_ids))
        cursor.execute(f'''
            DELETE FROM episode_guests 
            WHERE person_id = ? AND episode_id IN ({placeholders})
        ''', [person_id] + episode_ids)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise e

def get_episodes_by_person(person_id: int) -> List[int]:
    """Get all episode IDs where a person appears"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT episode_id FROM episode_guests WHERE person_id = ?
    ''', (person_id,))
    
    episode_ids = [row['episode_id'] for row in cursor.fetchall()]
    conn.close()
    return episode_ids

def get_people_by_episode(episode_id: int) -> List[dict]:
    """Get all people in an episode"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.* FROM people p
        JOIN episode_guests eg ON p.id = eg.person_id
        WHERE eg.episode_id = ?
    ''', (episode_id,))
    
    people = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return people

# Episode Management Queries

def create_episode(data: dict) -> dict:
    """Create a new episode"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    
    cursor.execute('''
        INSERT INTO episodes (
            podcast_id, title, description, youtube_video_id, thumbnail,
            episode_number, season_number, season_title, duration,
            published_date, views, likes, comments, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['podcast_id'], data['title'], data.get('description'),
        data.get('youtube_video_id'), data.get('thumbnail'),
        data.get('episode_number', 1), data.get('season_number', 1),
        data.get('season_title'), data.get('duration'),
        data.get('published_date', now), data.get('views', 0),
        data.get('likes', 0), data.get('comments', 0), now
    ))
    
    episode_id = cursor.lastrowid
    
    # Update podcast episode count
    cursor.execute('''
        UPDATE podcasts 
        SET episode_count = (SELECT COUNT(*) FROM episodes WHERE podcast_id = ?)
        WHERE id = ?
    ''', (data['podcast_id'], data['podcast_id']))
    
    conn.commit()
    conn.close()
    
    return get_episode_by_id(episode_id)

def create_episodes_bulk(episodes_data: List[dict]) -> List[dict]:
    """Create multiple episodes at once"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    created_episodes = []
    
    try:
        for data in episodes_data:
            cursor.execute('''
                INSERT INTO episodes (
                    podcast_id, title, description, youtube_video_id, thumbnail,
                    episode_number, season_number, season_title, duration,
                    published_date, views, likes, comments, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['podcast_id'], data['title'], data.get('description'),
                data.get('youtube_video_id'), data.get('thumbnail'),
                data.get('episode_number', 1), data.get('season_number', 1),
                data.get('season_title'), data.get('duration'),
                data.get('published_date', now), data.get('views', 0),
                data.get('likes', 0), data.get('comments', 0), now
            ))
            
            episode_id = cursor.lastrowid
            created_episodes.append(get_episode_by_id_no_close(cursor, episode_id))
        
        # Update podcast episode counts
        if episodes_data:
            podcast_id = episodes_data[0]['podcast_id']
            cursor.execute('''
                UPDATE podcasts 
                SET episode_count = (SELECT COUNT(*) FROM episodes WHERE podcast_id = ?)
                WHERE id = ?
            ''', (podcast_id, podcast_id))
        
        conn.commit()
        conn.close()
        return created_episodes
    except Exception as e:
        conn.close()
        raise e

def get_episode_by_id_no_close(cursor, episode_id: int) -> Optional[dict]:
    """Get episode by ID without closing connection (for bulk operations)"""
    cursor.execute('''
        SELECT e.*, p.title as podcast_title 
        FROM episodes e
        JOIN podcasts p ON e.podcast_id = p.id
        WHERE e.id = ?
    ''', (episode_id,))
    
    row = cursor.fetchone()
    return dict(row) if row else None

def get_episodes_by_podcast(podcast_id: int) -> List[dict]:
    """Get all episodes for a podcast"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM episodes 
        WHERE podcast_id = ?
        ORDER BY season_number ASC, episode_number ASC
    ''', (podcast_id,))
    
    episodes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return episodes

def get_next_episode_number(podcast_id: int, season_number: int = 1) -> int:
    """Get the next episode number for a podcast/season"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT MAX(episode_number) as max_num FROM episodes 
        WHERE podcast_id = ? AND season_number = ?
    ''', (podcast_id, season_number))
    
    result = cursor.fetchone()
    conn.close()
    
    max_num = result['max_num'] if result and result['max_num'] else 0
    return max_num + 1

def delete_episode(episode_id: int) -> bool:
    """Delete an episode"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get podcast_id before deleting
        cursor.execute("SELECT podcast_id FROM episodes WHERE id = ?", (episode_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        podcast_id = result['podcast_id']
        
        cursor.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
        
        # Update podcast episode count
        cursor.execute('''
            UPDATE podcasts 
            SET episode_count = (SELECT COUNT(*) FROM episodes WHERE podcast_id = ?)
            WHERE id = ?
        ''', (podcast_id, podcast_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise e

# Playlist Auto-Sync Queries

def save_playlist_for_sync(podcast_id: int, playlist_url: str, playlist_id: str) -> bool:
    """Save playlist for auto-sync"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    
    try:
        cursor.execute('''
            INSERT INTO podcast_playlists (podcast_id, playlist_url, playlist_id, last_synced_at)
            VALUES (?, ?, ?, ?)
        ''', (podcast_id, playlist_url, playlist_id, now))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise e

def get_playlists_for_sync() -> List[dict]:
    """Get all playlists enabled for auto-sync"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM podcast_playlists 
        WHERE auto_sync_enabled = 1
        ORDER BY last_synced_at ASC
    ''')
    
    playlists = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return playlists

def update_playlist_sync_time(playlist_id: int) -> bool:
    """Update last synced time for a playlist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = int(time.time())
    
    cursor.execute('''
        UPDATE podcast_playlists 
        SET last_synced_at = ?
        WHERE id = ?
    ''', (now, playlist_id))
    
    conn.commit()
    conn.close()
    return True

# Category and Language Management

def create_category(name: str, description: str = None, icon: str = None) -> dict:
    """Create a new category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    slug = create_slug(name)
    
    try:
        cursor.execute('''
            INSERT INTO categories (name, slug, description, icon)
            VALUES (?, ?, ?, ?)
        ''', (name, slug, description, icon))
        
        category_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        category = dict(cursor.fetchone())
        
        conn.close()
        return category
    except Exception as e:
        conn.close()
        raise e

def search_categories(search_term: str, limit: int = 10) -> List[dict]:
    """Search categories by name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_pattern = f"%{search_term}%"
    cursor.execute('''
        SELECT * FROM categories
        WHERE name LIKE ?
        ORDER BY podcast_count DESC
        LIMIT ?
    ''', (search_pattern, limit))
    
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return categories

def create_language(code: str, name: str, native_name: str = None) -> dict:
    """Create a new language"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO languages (code, name, native_name)
            VALUES (?, ?, ?)
        ''', (code, name, native_name))
        
        language_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM languages WHERE id = ?", (language_id,))
        language = dict(cursor.fetchone())
        
        conn.close()
        return language
    except Exception as e:
        conn.close()
        raise e

def search_languages(search_term: str, limit: int = 10) -> List[dict]:
    """Search languages by name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_pattern = f"%{search_term}%"
    cursor.execute('''
        SELECT * FROM languages
        WHERE name LIKE ? OR native_name LIKE ?
        ORDER BY name
        LIMIT ?
    ''', (search_pattern, search_pattern, limit))
    
    languages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return languages

def get_distinct_locations(search_term: str = None, limit: int = 10) -> List[dict]:
    """Get distinct locations from podcasts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search_term:
        search_pattern = f"%{search_term}%"
        cursor.execute('''
            SELECT DISTINCT location, state, country 
            FROM podcasts 
            WHERE location IS NOT NULL 
            AND (location LIKE ? OR state LIKE ? OR country LIKE ?)
            LIMIT ?
        ''', (search_pattern, search_pattern, search_pattern, limit))
    else:
        cursor.execute('''
            SELECT DISTINCT location, state, country 
            FROM podcasts 
            WHERE location IS NOT NULL 
            LIMIT ?
        ''', (limit,))
    
    locations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return locations
