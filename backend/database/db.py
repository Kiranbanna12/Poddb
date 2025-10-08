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
            email_verified INTEGER DEFAULT 0,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            avatar_path TEXT,
            bio TEXT,
            role TEXT DEFAULT 'user',
            contribution_count INTEGER DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_banned INTEGER DEFAULT 0,
            ban_reason TEXT,
            last_login INTEGER,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    ''')
    
    # Create sessions table for session management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            expires INTEGER NOT NULL,
            device_info TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create verification_tokens table for email verification and password reset
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires INTEGER NOT NULL,
            type TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL
        )
    ''')
    
    # Create login_attempts table for security tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL,
            ip_address TEXT,
            success INTEGER NOT NULL,
            attempted_at INTEGER NOT NULL
        )
    ''')
    
    # Create user_activity_logs table for audit trail
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create email_queue table for email management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL,
            sent_at INTEGER
        )
    ''')

    
    # Create contributions table (enhanced for admin review)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            podcast_id INTEGER,
            contribution_type TEXT NOT NULL CHECK(contribution_type IN ('new_podcast', 'update_podcast', 'new_episode', 'new_person')),
            submitted_data TEXT NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_review', 'approved', 'rejected')),
            rejection_reason TEXT,
            admin_notes TEXT,
            reviewed_by INTEGER,
            reviewed_at INTEGER,
            created_at INTEGER NOT NULL,
            updated_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (podcast_id) REFERENCES podcasts(id) ON DELETE CASCADE,
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        )
    ''')
    
    # Create contribution_changes table for partial approvals
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contribution_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contribution_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            original_value TEXT,
            submitted_value TEXT,
            admin_edited_value TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'modified')),
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (contribution_id) REFERENCES contributions(id) ON DELETE CASCADE
        )
    ''')
    
    # Create admin_activity_logs table for audit trail
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            action_details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (admin_user_id) REFERENCES users(id)
        )
    ''')
    
    # Create notifications table for in-app notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            link TEXT,
            is_read INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
    
    # Create indexes for authentication tables
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verification_tokens_token ON verification_tokens(token)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verification_tokens_identifier ON verification_tokens(identifier)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_login_attempts_identifier ON login_attempts(identifier)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activity_logs_user ON user_activity_logs(user_id)')
    
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