# PodDB Pro - Backend Implementation Contracts

## 1. API Contracts

### Podcasts API
- **GET /api/podcasts** - Get all podcasts with pagination and filters
  - Query params: `category`, `language`, `location`, `page`, `limit`
  - Response: `{ podcasts: [], total: number, page: number }`

- **GET /api/podcasts/:id** - Get single podcast details
  - Response: Full podcast object with episodes and team members

- **POST /api/podcasts** - Create new podcast (authenticated)
  - Body: Podcast data with YouTube playlist ID
  - Response: Created podcast object

- **GET /api/podcasts/top** - Get top rated podcasts
  - Query params: `limit` (default 8)
  - Response: Array of top podcasts

### Episodes API
- **GET /api/episodes** - Get latest episodes
  - Query params: `limit`, `page`
  - Response: `{ episodes: [], total: number }`

- **GET /api/episodes/:id** - Get single episode
  - Response: Episode object with podcast details

### People API
- **GET /api/people** - Get all people (hosts, guests, producers)
  - Query params: `limit`, `role`
  - Response: Array of people objects

### Categories API
- **GET /api/categories** - Get all categories with podcast counts
  - Response: Array of category objects

### Rankings API
- **GET /api/rankings/:type** - Get rankings (overall/weekly/monthly)
  - Query params: `category`, `language`, `page`, `limit`
  - Response: Ranked podcasts with rank change indicators

### Contributions API
- **POST /api/contributions** - Submit podcast contribution
  - Body: Full contribution data
  - Response: Contribution object with pending status

- **GET /api/contributions** - Get user's contributions (authenticated)
  - Response: Array of contributions with status

### Auth API
- **POST /api/auth/register** - User registration
  - Body: `{ username, email, password }`
  - Response: User object with JWT token

- **POST /api/auth/login** - User login
  - Body: `{ email, password }`
  - Response: JWT token

### Stats API
- **GET /api/stats** - Get platform statistics
  - Response: `{ totalPodcasts, totalEpisodes, totalPeople }`

### YouTube API Integration
- **POST /api/youtube/import-episodes** - Import episodes from YouTube playlist
  - Body: `{ playlistId }`
  - Response: Array of imported episodes

## 2. Mock Data to Replace

### From mock.js:
- **mockPodcasts** → SQLite `podcasts` table
- **mockEpisodes** → SQLite `episodes` table
- **mockPeople** → SQLite `people` table
- **mockCategories** → SQLite `categories` table (seed data)
- **mockStats** → Calculated from database queries
- **mockNews** → SQLite `news` table (optional for now)

### Data Transformation:
- Cover images: Use Unsplash URLs temporarily, later support file uploads
- Categories: Many-to-many relationship via `podcast_categories` table
- Languages: Many-to-many relationship via `podcast_languages` table
- Team members: Link via `podcast_people` table

## 3. Backend Implementation Plan

### Phase 1: Database Setup
1. Create SQLite database file: `/app/backend/database/poddb.db`
2. Create database schema with essential tables:
   - `podcasts` - Main podcast data
   - `episodes` - Episode data
   - `people` - Hosts, guests, producers
   - `categories` - Podcast categories
   - `languages` - Language options
   - `users` - User authentication
   - `contributions` - User submissions
   - `podcast_categories` - Junction table
   - `podcast_languages` - Junction table
   - `podcast_people` - Junction table
   - `rankings_weekly` - Pre-calculated weekly rankings
   - `rankings_monthly` - Pre-calculated monthly rankings

3. Create seed data for categories and languages

### Phase 2: Database Models (Pydantic)
1. Create models in `/app/backend/models/`
   - `podcast.py` - Podcast, PodcastCreate, PodcastUpdate
   - `episode.py` - Episode, EpisodeCreate
   - `person.py` - Person, PersonCreate
   - `category.py` - Category
   - `language.py` - Language
   - `user.py` - User, UserCreate, UserLogin
   - `contribution.py` - Contribution, ContributionCreate
   - `ranking.py` - Ranking models

### Phase 3: Database Functions
1. Create `/app/backend/database/db.py`
   - Initialize SQLite connection
   - Create tables function
   - Seed data function

2. Create `/app/backend/database/queries.py`
   - CRUD operations for all entities
   - Filtering and pagination helpers
   - Statistics calculations
   - Ranking calculations

### Phase 4: YouTube API Integration
1. Create `/app/backend/services/youtube_service.py`
   - Fetch playlist details
   - Fetch video details
   - Parse episode data
   - Download thumbnails (optional)

### Phase 5: Authentication
1. Create `/app/backend/auth/`
   - `auth.py` - JWT token generation/verification
   - `password.py` - Password hashing (bcrypt)
   - `middleware.py` - Protected route decorator

### Phase 6: API Routes
1. Update `/app/backend/server.py`
   - Add all API endpoints
   - Connect to database queries
   - Add authentication middleware
   - Error handling

### Phase 7: File Upload (Optional for MVP)
1. Create `/app/backend/services/upload_service.py`
   - Handle cover image uploads
   - Handle profile photo uploads
   - Image resizing/optimization

## 4. Frontend-Backend Integration

### Files to Update:

#### HomePage.jsx
- Replace `mockPodcasts` with `GET /api/podcasts/top`
- Replace `mockEpisodes` with `GET /api/episodes?limit=8`
- Replace `mockPeople` with `GET /api/people?limit=12`
- Replace `mockCategories` with `GET /api/categories`
- Replace `mockStats` with `GET /api/stats`

#### RankingsPage.jsx
- Replace `mockPodcasts` with `GET /api/rankings/:type`
- Add category/language filters to API calls
- Handle pagination from backend

#### ContributePage.jsx
- Connect form submission to `POST /api/contributions`
- Add YouTube playlist validation
- Add image upload for cover/profile photos
- Show success/error toasts

### API Helper File
Create `/app/frontend/src/services/api.js`:
- Axios instance with base URL from env
- API call functions for all endpoints
- Error handling
- JWT token management (localStorage)

### Authentication Context
Create `/app/frontend/src/context/AuthContext.jsx`:
- User state management
- Login/logout functions
- Protected route wrapper

## 5. Database Schema Details

### podcasts table
```
id, title, slug, description, cover_image, youtube_playlist_id,
location, state, country, website, rating (default 0.0), 
total_ratings (default 0), views, likes, comments, episode_count,
status (pending/approved/rejected), created_at, updated_at
```

### episodes table
```
id, podcast_id (FK), title, description, youtube_video_id, thumbnail,
episode_number, views, likes, comments, duration, published_date, created_at
```

### people table
```
id, name, slug, bio, profile_photo, role (host/guest/producer/editor),
location, created_at
```

### categories table
```
id, name, slug, description, icon, podcast_count (cached)
```

### languages table
```
id, code (hi/en/etc), name, native_name
```

### users table
```
id, username, email, password_hash, role (user/moderator/admin),
contribution_count, created_at, last_login
```

### contributions table
```
id, user_id (FK), podcast_id (FK), type (new/update/episode),
status (pending/approved/rejected), rejection_reason,
created_at, reviewed_at, reviewer_id (FK)
```

### Junction Tables
```
podcast_categories: podcast_id, category_id
podcast_languages: podcast_id, language_id
podcast_people: podcast_id, person_id, role
```

## 6. Environment Variables

Add to `/app/backend/.env`:
```
YOUTUBE_API_KEY=AIzaSyACB23V_uwQSVa2Wiz8rJbhwBO8AihOe3o
JWT_SECRET_KEY=<generate random secret>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## 7. Testing Strategy

After backend implementation:
1. Test all API endpoints with backend testing agent
2. Test YouTube API integration
3. Test authentication flow
4. Test frontend-backend integration
5. Test filtering and pagination

## 8. MVP Scope

**Include in MVP:**
- Basic podcast CRUD operations
- Episode listing (without import initially)
- Category/language filtering
- User authentication (JWT)
- Contribution submission
- Basic rankings (overall only)
- Statistics

**Defer for later:**
- Automated YouTube episode import (can manually add sample episodes)
- Weekly/monthly rankings calculation (show overall only)
- File uploads (use URLs for now)
- Admin panel
- Reviews/ratings functionality
- Search functionality
