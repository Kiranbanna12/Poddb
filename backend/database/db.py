import sqlite3
import os
from pathlib import Path

DATABASE_DIR = Path(__file__).parent
DATABASE_PATH = DATABASE_DIR / 'poddb.db'

def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    """Initialize database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create podcasts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT,
            cover_image TEXT,
            youtube_playlist_id TEXT UNIQUE,
            location TEXT,
            state TEXT,
            country TEXT,
            website TEXT,
            rating REAL DEFAULT 0.0,
            total_ratings INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            episode_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    ''')
    
    # Create episodes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            podcast_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            youtube_video_id TEXT UNIQUE,
            thumbnail TEXT,
            episode_number INTEGER,
            season_number INTEGER DEFAULT 1,
            season_title TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            duration TEXT,
            published_date INTEGER,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (podcast_id) REFERENCES podcasts(id) ON DELETE CASCADE
        )
    ''')
    
    # Create people table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            bio TEXT,
            profile_photo_path TEXT,
            role TEXT DEFAULT 'Host',
            location TEXT,
            date_of_birth INTEGER,
            instagram_url TEXT,
            youtube_url TEXT,
            twitter_url TEXT,
            facebook_url TEXT,
            linkedin_url TEXT,
            website_url TEXT,
            created_at INTEGER NOT NULL
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            description TEXT,
            icon TEXT,
            podcast_count INTEGER DEFAULT 0
        )
    ''')
    
    # Create languages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            native_name TEXT
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            contribution_count INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL,
            last_login INTEGER
        )
    ''')
    
    # Create contributions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            podcast_id INTEGER,
            type TEXT DEFAULT 'new',
            status TEXT DEFAULT 'pending',
            rejection_reason TEXT,
            data TEXT,
            created_at INTEGER NOT NULL,
            reviewed_at INTEGER,
            reviewer_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (podcast_id) REFERENCES podcasts(id),
            FOREIGN KEY (reviewer_id) REFERENCES users(id)
        )
    ''')
    
    # Create junction tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_categories (
            podcast_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            PRIMARY KEY (podcast_id, category_id),
            FOREIGN KEY (podcast_id) REFERENCES podcasts(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_languages (
            podcast_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            PRIMARY KEY (podcast_id, language_id),
            FOREIGN KEY (podcast_id) REFERENCES podcasts(id) ON DELETE CASCADE,
            FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_people (
            podcast_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            role TEXT,
            PRIMARY KEY (podcast_id, person_id),
            FOREIGN KEY (podcast_id) REFERENCES podcasts(id) ON DELETE CASCADE,
            FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
        )
    ''')
    
    # Create episode_guests table for team member episode assignments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episode_guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            UNIQUE(episode_id, person_id),
            FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE,
            FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
        )
    ''')
    
    # Create podcast_playlists table for YouTube auto-sync
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            podcast_id INTEGER NOT NULL,
            playlist_url TEXT NOT NULL,
            playlist_id TEXT NOT NULL,
            last_synced_at INTEGER,
            auto_sync_enabled INTEGER DEFAULT 1,
            FOREIGN KEY (podcast_id) REFERENCES podcasts(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_podcasts_status ON podcasts(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_podcasts_rating ON podcasts(rating DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_episodes_podcast ON episodes(podcast_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_episode_guests_episode ON episode_guests(episode_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_episode_guests_person ON episode_guests(person_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contributions_user ON contributions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contributions_status ON contributions(status)')
    
    conn.commit()
    conn.close()
    print("✓ Database tables created successfully")

def seed_data():
    """Seed initial data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if categories already exist
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        # Insert categories
        categories = [
            ('Technology', 'technology', 'Tech and innovation podcasts', 'Laptop'),
            ('Comedy', 'comedy', 'Comedy and humor podcasts', 'Laugh'),
            ('Business', 'business', 'Business and entrepreneurship', 'Briefcase'),
            ('Entertainment', 'entertainment', 'Entertainment and pop culture', 'Film'),
            ('True Crime', 'true-crime', 'True crime investigations', 'Search'),
            ('Health', 'health', 'Health and wellness', 'Heart'),
            ('Sports', 'sports', 'Sports and athletics', 'Trophy'),
            ('History', 'history', 'Historical topics', 'BookOpen'),
            ('Education', 'education', 'Educational content', 'GraduationCap'),
            ('News', 'news', 'News and current affairs', 'Newspaper')
        ]
        cursor.executemany(
            'INSERT INTO categories (name, slug, description, icon) VALUES (?, ?, ?, ?)',
            categories
        )
        print("✓ Categories seeded")
    
    # Check if languages already exist
    cursor.execute("SELECT COUNT(*) FROM languages")
    if cursor.fetchone()[0] == 0:
        # Insert languages
        languages = [
            ('hi', 'Hindi', 'हिन्दी'),
            ('en', 'English', 'English'),
            ('pa', 'Punjabi', 'ਪੰਜਾਬੀ'),
            ('ta', 'Tamil', 'தமிழ்'),
            ('te', 'Telugu', 'తెలుగు'),
            ('bn', 'Bengali', 'বাংলা'),
            ('mr', 'Marathi', 'मराठी'),
            ('gu', 'Gujarati', 'ગુજરાતી')
        ]
        cursor.executemany(
            'INSERT INTO languages (code, name, native_name) VALUES (?, ?, ?)',
            languages
        )
        print("✓ Languages seeded")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    seed_data()
    print("✓ Database initialization complete")