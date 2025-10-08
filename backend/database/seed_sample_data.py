"""Seed sample podcast data"""
from queries import create_podcast, create_episode
import time

# Sample podcasts data
sample_podcasts = [
    {
        'title': 'Tech Talks India',
        'description': 'Deep dive into technology, startups, and innovation in India',
        'cover_image': 'https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=400',
        'youtube_playlist_id': 'PLxxx123tech',
        'location': 'Mumbai',
        'state': 'Maharashtra',
        'country': 'India',
        'categories': ['Technology', 'Business'],
        'languages': ['Hindi', 'English']
    },
    {
        'title': 'Comedy Nights Podcast',
        'description': 'Hilarious conversations with India\'s top comedians',
        'cover_image': 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=400',
        'youtube_playlist_id': 'PLxxx456comedy',
        'location': 'Delhi',
        'state': 'Delhi',
        'country': 'India',
        'categories': ['Comedy', 'Entertainment'],
        'languages': ['Hindi']
    },
    {
        'title': 'Bollywood Insider',
        'description': 'Behind the scenes stories from Bollywood stars',
        'cover_image': 'https://images.unsplash.com/photo-1594908900066-3f47337549d8?w=400',
        'youtube_playlist_id': 'PLxxx789bollywood',
        'location': 'Mumbai',
        'state': 'Maharashtra',
        'country': 'India',
        'categories': ['Entertainment'],
        'languages': ['Hindi', 'English']
    },
    {
        'title': 'Business Masters',
        'description': 'Learn from successful entrepreneurs and business leaders',
        'cover_image': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=400',
        'youtube_playlist_id': 'PLxxx101business',
        'location': 'Bangalore',
        'state': 'Karnataka',
        'country': 'India',
        'categories': ['Business', 'Education'],
        'languages': ['English']
    },
    {
        'title': 'True Crime India',
        'description': 'Investigating India\'s most mysterious criminal cases',
        'cover_image': 'https://images.unsplash.com/photo-1505330622279-bf7d7fc918f4?w=400',
        'youtube_playlist_id': 'PLxxx202crime',
        'location': 'Delhi',
        'state': 'Delhi',
        'country': 'India',
        'categories': ['True Crime'],
        'languages': ['Hindi', 'English']
    },
    {
        'title': 'Health & Wellness Show',
        'description': 'Expert advice on fitness, nutrition, and mental health',
        'cover_image': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400',
        'youtube_playlist_id': 'PLxxx303health',
        'location': 'Pune',
        'state': 'Maharashtra',
        'country': 'India',
        'categories': ['Health'],
        'languages': ['English', 'Hindi']
    },
    {
        'title': 'Sports Central',
        'description': 'In-depth analysis of cricket, football, and other sports',
        'cover_image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400',
        'youtube_playlist_id': 'PLxxx404sports',
        'location': 'Mumbai',
        'state': 'Maharashtra',
        'country': 'India',
        'categories': ['Sports', 'Entertainment'],
        'languages': ['Hindi', 'English']
    },
    {
        'title': 'History Uncovered',
        'description': 'Exploring India\'s rich historical heritage and untold stories',
        'cover_image': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400',
        'youtube_playlist_id': 'PLxxx505history',
        'location': 'Jaipur',
        'state': 'Rajasthan',
        'country': 'India',
        'categories': ['History', 'Education'],
        'languages': ['English']
    }
]

# Sample episodes data
sample_episodes = [
    {
        'podcast_id': 1,
        'title': 'AI Revolution in 2025: What\'s Next?',
        'description': 'Discussing the latest AI breakthroughs and their impact on India',
        'youtube_video_id': 'abc123',
        'thumbnail': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400',
        'episode_number': 156,
        'duration': '45:32',
        'views': 45000,
        'likes': 2100,
        'comments': 134,
        'published_date': int(time.time()) - 86400
    },
    {
        'podcast_id': 2,
        'title': 'Stand-up Struggles ft. Zakir Khan',
        'description': 'Zakir Khan shares his journey in comedy',
        'youtube_video_id': 'def456',
        'thumbnail': 'https://images.unsplash.com/photo-1527224538127-2104bb985c1e?w=400',
        'episode_number': 234,
        'duration': '52:18',
        'views': 67000,
        'likes': 3200,
        'comments': 289,
        'published_date': int(time.time()) - 172800
    },
    {
        'podcast_id': 3,
        'title': 'Shah Rukh Khan\'s Untold Stories',
        'description': 'Exclusive interview with King Khan',
        'youtube_video_id': 'ghi789',
        'thumbnail': 'https://images.unsplash.com/photo-1574267432644-f610a4b70fa4?w=400',
        'episode_number': 189,
        'duration': '1:08:45',
        'views': 123000,
        'likes': 5600,
        'comments': 412,
        'published_date': int(time.time()) - 259200
    },
    {
        'podcast_id': 4,
        'title': 'Scaling Your Startup: Expert Tips',
        'description': 'How to grow from 10 to 100 employees',
        'youtube_video_id': 'jkl012',
        'thumbnail': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400',
        'episode_number': 142,
        'duration': '41:22',
        'views': 34000,
        'likes': 1800,
        'comments': 156,
        'published_date': int(time.time()) - 345600
    },
    {
        'podcast_id': 5,
        'title': 'The Mysterious Case of Sheena Bora',
        'description': 'Deep investigation into one of India\'s most shocking crimes',
        'youtube_video_id': 'mno345',
        'thumbnail': 'https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=400',
        'episode_number': 98,
        'duration': '56:12',
        'views': 89000,
        'likes': 4200,
        'comments': 567,
        'published_date': int(time.time()) - 432000
    },
    {
        'podcast_id': 6,
        'title': 'Mental Health in Modern India',
        'description': 'Breaking the stigma around mental health',
        'youtube_video_id': 'pqr678',
        'thumbnail': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
        'episode_number': 167,
        'duration': '38:45',
        'views': 28000,
        'likes': 1500,
        'comments': 98,
        'published_date': int(time.time()) - 518400
    },
    {
        'podcast_id': 7,
        'title': 'World Cup 2025: Team India\'s Chances',
        'description': 'Expert analysis of India\'s cricket team performance',
        'youtube_video_id': 'stu901',
        'thumbnail': 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=400',
        'episode_number': 203,
        'duration': '47:30',
        'views': 56000,
        'likes': 2800,
        'comments': 234,
        'published_date': int(time.time()) - 604800
    },
    {
        'podcast_id': 8,
        'title': 'The Lost City of Hampi',
        'description': 'Exploring the ruins of the Vijayanagara Empire',
        'youtube_video_id': 'vwx234',
        'thumbnail': 'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=400',
        'episode_number': 121,
        'duration': '43:15',
        'views': 31000,
        'likes': 1600,
        'comments': 87,
        'published_date': int(time.time()) - 691200
    }
]

def seed_all():
    """Seed all sample data"""
    from db import get_db_connection
    
    # Check if data already exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM podcasts")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        print("Sample data already exists. Skipping seed.")
        return
    
    print("Seeding sample podcasts...")
    # Create podcasts and update with ratings
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for podcast_data in sample_podcasts:
        podcast = create_podcast(podcast_data, user_id=1)
        
        # Update with realistic stats
        if podcast['id'] == 1:
            stats = {'views': 2450000, 'likes': 45000, 'comments': 3200, 'rating': 8.7, 'total_ratings': 1240}
        elif podcast['id'] == 2:
            stats = {'views': 5800000, 'likes': 89000, 'comments': 5600, 'rating': 9.2, 'total_ratings': 3450}
        elif podcast['id'] == 3:
            stats = {'views': 3200000, 'likes': 67000, 'comments': 4100, 'rating': 8.5, 'total_ratings': 2100}
        elif podcast['id'] == 4:
            stats = {'views': 1900000, 'likes': 52000, 'comments': 2800, 'rating': 8.9, 'total_ratings': 1890}
        elif podcast['id'] == 5:
            stats = {'views': 4100000, 'likes': 78000, 'comments': 6200, 'rating': 9.0, 'total_ratings': 2780}
        elif podcast['id'] == 6:
            stats = {'views': 1200000, 'likes': 34000, 'comments': 1900, 'rating': 8.3, 'total_ratings': 890}
        elif podcast['id'] == 7:
            stats = {'views': 2800000, 'likes': 61000, 'comments': 3700, 'rating': 8.6, 'total_ratings': 1650}
        else:
            stats = {'views': 1650000, 'likes': 43000, 'comments': 2400, 'rating': 8.8, 'total_ratings': 1320}
        
        cursor.execute('''
            UPDATE podcasts 
            SET views = ?, likes = ?, comments = ?, rating = ?, total_ratings = ?
            WHERE id = ?
        ''', (stats['views'], stats['likes'], stats['comments'], stats['rating'], stats['total_ratings'], podcast['id']))
        
        print(f"✓ Created podcast: {podcast['title']}")
    
    conn.commit()
    conn.close()
    
    print("\nSeeding sample episodes...")
    for episode_data in sample_episodes:
        episode = create_episode(episode_data)
        print(f"✓ Created episode: {episode['title']}")
    
    print("\n✓ Sample data seeding complete!")

if __name__ == '__main__':
    seed_all()
