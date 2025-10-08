"""YouTube API Integration Service"""
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
from typing import Dict, List, Optional
from datetime import datetime


class YouTubeService:
    def __init__(self):
        self.api_key = os.environ.get('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment variables")
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL"""
        if 'list=' in url:
            return url.split('list=')[1].split('&')[0]
        return url if len(url) == 34 and url.startswith('PL') else None
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        if 'watch?v=' in url:
            return url.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        return url if len(url) == 11 else None
    
    def get_playlist_details(self, playlist_id: str) -> Dict:
        """Get playlist metadata"""
        try:
            request = self.youtube.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError("Playlist not found")
            
            playlist = response['items'][0]
            snippet = playlist['snippet']
            
            return {
                'id': playlist_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_name': snippet['channelTitle'],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'item_count': playlist['contentDetails']['itemCount']
            }
        except HttpError as e:
            raise Exception(f"YouTube API Error: {e}")
    
    def get_playlist_videos(self, playlist_id: str, max_results: Optional[int] = None, start_index: int = 0) -> List[Dict]:
        """
        Get videos from a playlist with pagination support.
        
        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos to fetch. If None, fetches ALL videos (unlimited).
            start_index: Starting index for pagination (0-based)
        
        Returns:
            List of video details
        """
        videos = []
        next_page_token = None
        page_count = 0
        videos_skipped = 0
        
        try:
            while True:
                page_count += 1
                print(f"Fetching page {page_count}... (Total videos so far: {len(videos)})")
                
                request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,  # YouTube API max per request
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Extract video IDs
                video_ids = [item['contentDetails']['videoId'] for item in response['items']]
                
                # Get detailed video information
                video_details = self.get_video_details(video_ids)
                
                # Apply start_index filtering
                for video in video_details:
                    if videos_skipped < start_index:
                        videos_skipped += 1
                        continue
                    videos.append(video)
                    
                    # Stop if we've reached the requested limit
                    if max_results is not None and len(videos) >= max_results:
                        print(f"✅ Reached requested limit of {max_results} videos (starting from index {start_index}).")
                        return videos
                
                # Check if we should continue
                next_page_token = response.get('nextPageToken')
                
                # Stop if no more pages
                if not next_page_token:
                    print(f"✅ Completed! Fetched {len(videos)} videos from playlist (starting from index {start_index}).")
                    break
            
            return videos
            
        except HttpError as e:
            raise Exception(f"YouTube API Error: {e}")
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get detailed information for multiple videos"""
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                snippet = item['snippet']
                content_details = item['contentDetails']
                statistics = item.get('statistics', {})
                
                # Parse duration
                duration_iso = content_details.get('duration', 'PT0S')
                duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())
                duration_str = self._format_duration(duration_seconds)
                
                # Parse published date
                published_at = snippet['publishedAt']
                published_timestamp = int(datetime.fromisoformat(published_at.replace('Z', '+00:00')).timestamp())
                
                videos.append({
                    'video_id': item['id'],
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'thumbnail': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else snippet['thumbnails']['default']['url'],
                    'duration': duration_str,
                    'duration_seconds': duration_seconds,
                    'published_date': published_timestamp,
                    'views': int(statistics.get('viewCount', 0)),
                    'likes': int(statistics.get('likeCount', 0)),
                    'comments': int(statistics.get('commentCount', 0))
                })
            
            return videos
        except HttpError as e:
            raise Exception(f"YouTube API Error: {e}")
    
    def get_single_video(self, video_id: str) -> Dict:
        """Get details for a single video"""
        videos = self.get_video_details([video_id])
        if not videos:
            raise ValueError("Video not found")
        return videos[0]
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


# Singleton instance
youtube_service = YouTubeService()
