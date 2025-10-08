// Mock data for PodDB Pro

export const mockPodcasts = [
  {
    id: 1,
    title: "Tech Talks India",
    description: "Deep dive into technology, startups, and innovation in India",
    coverImage: "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=400",
    categories: ["Technology", "Business"],
    languages: ["Hindi", "English"],
    rating: 8.7,
    totalRatings: 1240,
    views: 2450000,
    likes: 45000,
    comments: 3200,
    episodeCount: 156,
    location: "Mumbai, Maharashtra, India",
    youtubePlaylistId: "PLxxx123",
    status: "approved"
  },
  {
    id: 2,
    title: "Comedy Nights Podcast",
    description: "Hilarious conversations with India's top comedians",
    coverImage: "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=400",
    categories: ["Comedy", "Entertainment"],
    languages: ["Hindi"],
    rating: 9.2,
    totalRatings: 3450,
    views: 5800000,
    likes: 89000,
    comments: 5600,
    episodeCount: 234,
    location: "Delhi, India",
    youtubePlaylistId: "PLxxx456",
    status: "approved"
  },
  {
    id: 3,
    title: "Bollywood Insider",
    description: "Behind the scenes stories from Bollywood stars",
    coverImage: "https://images.unsplash.com/photo-1594908900066-3f47337549d8?w=400",
    categories: ["Entertainment", "Movies"],
    languages: ["Hindi", "English"],
    rating: 8.5,
    totalRatings: 2100,
    views: 3200000,
    likes: 67000,
    comments: 4100,
    episodeCount: 189,
    location: "Mumbai, Maharashtra, India",
    youtubePlaylistId: "PLxxx789",
    status: "approved"
  },
  {
    id: 4,
    title: "Business Masters",
    description: "Learn from successful entrepreneurs and business leaders",
    coverImage: "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=400",
    categories: ["Business", "Education"],
    languages: ["English"],
    rating: 8.9,
    totalRatings: 1890,
    views: 1900000,
    likes: 52000,
    comments: 2800,
    episodeCount: 142,
    location: "Bangalore, Karnataka, India",
    youtubePlaylistId: "PLxxx101",
    status: "approved"
  },
  {
    id: 5,
    title: "True Crime India",
    description: "Investigating India's most mysterious criminal cases",
    coverImage: "https://images.unsplash.com/photo-1505330622279-bf7d7fc918f4?w=400",
    categories: ["True Crime", "Documentary"],
    languages: ["Hindi", "English"],
    rating: 9.0,
    totalRatings: 2780,
    views: 4100000,
    likes: 78000,
    comments: 6200,
    episodeCount: 98,
    location: "Delhi, India",
    youtubePlaylistId: "PLxxx202",
    status: "approved"
  },
  {
    id: 6,
    title: "Health & Wellness Show",
    description: "Expert advice on fitness, nutrition, and mental health",
    coverImage: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400",
    categories: ["Health", "Lifestyle"],
    languages: ["English", "Hindi"],
    rating: 8.3,
    totalRatings: 890,
    views: 1200000,
    likes: 34000,
    comments: 1900,
    episodeCount: 167,
    location: "Pune, Maharashtra, India",
    youtubePlaylistId: "PLxxx303",
    status: "approved"
  },
  {
    id: 7,
    title: "Sports Central",
    description: "In-depth analysis of cricket, football, and other sports",
    coverImage: "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400",
    categories: ["Sports", "Entertainment"],
    languages: ["Hindi", "English"],
    rating: 8.6,
    totalRatings: 1650,
    views: 2800000,
    likes: 61000,
    comments: 3700,
    episodeCount: 203,
    location: "Mumbai, Maharashtra, India",
    youtubePlaylistId: "PLxxx404",
    status: "approved"
  },
  {
    id: 8,
    title: "History Uncovered",
    description: "Exploring India's rich historical heritage and untold stories",
    coverImage: "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400",
    categories: ["History", "Education"],
    languages: ["English"],
    rating: 8.8,
    totalRatings: 1320,
    views: 1650000,
    likes: 43000,
    comments: 2400,
    episodeCount: 121,
    location: "Jaipur, Rajasthan, India",
    youtubePlaylistId: "PLxxx505",
    status: "approved"
  }
];

export const mockEpisodes = [
  {
    id: 1,
    podcastId: 1,
    podcastTitle: "Tech Talks India",
    title: "AI Revolution in 2025: What's Next?",
    description: "Discussing the latest AI breakthroughs and their impact on India",
    thumbnail: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
    videoId: "abc123",
    episodeNumber: 156,
    views: 45000,
    likes: 2100,
    comments: 134,
    publishedDate: "2025-09-15",
    duration: "45:32"
  },
  {
    id: 2,
    podcastId: 2,
    podcastTitle: "Comedy Nights Podcast",
    title: "Stand-up Struggles ft. Zakir Khan",
    description: "Zakir Khan shares his journey in comedy",
    thumbnail: "https://images.unsplash.com/photo-1527224538127-2104bb985c1e?w=400",
    videoId: "def456",
    episodeNumber: 234,
    views: 67000,
    likes: 3200,
    comments: 289,
    publishedDate: "2025-09-14",
    duration: "52:18"
  },
  {
    id: 3,
    podcastId: 3,
    podcastTitle: "Bollywood Insider",
    title: "Shah Rukh Khan's Untold Stories",
    description: "Exclusive interview with King Khan",
    thumbnail: "https://images.unsplash.com/photo-1574267432644-f610a4b70fa4?w=400",
    videoId: "ghi789",
    episodeNumber: 189,
    views: 123000,
    likes: 5600,
    comments: 412,
    publishedDate: "2025-09-13",
    duration: "1:08:45"
  },
  {
    id: 4,
    podcastId: 4,
    podcastTitle: "Business Masters",
    title: "Scaling Your Startup: Expert Tips",
    description: "How to grow from 10 to 100 employees",
    thumbnail: "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400",
    videoId: "jkl012",
    episodeNumber: 142,
    views: 34000,
    likes: 1800,
    comments: 156,
    publishedDate: "2025-09-12",
    duration: "41:22"
  },
  {
    id: 5,
    podcastId: 5,
    podcastTitle: "True Crime India",
    title: "The Mysterious Case of Sheena Bora",
    description: "Deep investigation into one of India's most shocking crimes",
    thumbnail: "https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=400",
    videoId: "mno345",
    episodeNumber: 98,
    views: 89000,
    likes: 4200,
    comments: 567,
    publishedDate: "2025-09-11",
    duration: "56:12"
  },
  {
    id: 6,
    podcastId: 6,
    podcastTitle: "Health & Wellness Show",
    title: "Mental Health in Modern India",
    description: "Breaking the stigma around mental health",
    thumbnail: "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400",
    videoId: "pqr678",
    episodeNumber: 167,
    views: 28000,
    likes: 1500,
    comments: 98,
    publishedDate: "2025-09-10",
    duration: "38:45"
  },
  {
    id: 7,
    podcastId: 7,
    podcastTitle: "Sports Central",
    title: "World Cup 2025: Team India's Chances",
    description: "Expert analysis of India's cricket team performance",
    thumbnail: "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=400",
    videoId: "stu901",
    episodeNumber: 203,
    views: 56000,
    likes: 2800,
    comments: 234,
    publishedDate: "2025-09-09",
    duration: "47:30"
  },
  {
    id: 8,
    podcastId: 8,
    podcastTitle: "History Uncovered",
    title: "The Lost City of Hampi",
    description: "Exploring the ruins of the Vijayanagara Empire",
    thumbnail: "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=400",
    videoId: "vwx234",
    episodeNumber: 121,
    views: 31000,
    likes: 1600,
    comments: 87,
    publishedDate: "2025-09-08",
    duration: "43:15"
  }
];

export const mockPeople = [
  {
    id: 1,
    name: "Ranveer Allahbadia",
    bio: "Content creator and podcast host",
    profilePhoto: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200",
    role: "Host",
    podcasts: ["Tech Talks India"]
  },
  {
    id: 2,
    name: "Zakir Khan",
    bio: "Stand-up comedian and storyteller",
    profilePhoto: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
    role: "Host",
    podcasts: ["Comedy Nights Podcast"]
  },
  {
    id: 3,
    name: "Anupama Chopra",
    bio: "Film critic and journalist",
    profilePhoto: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200",
    role: "Host",
    podcasts: ["Bollywood Insider"]
  },
  {
    id: 4,
    name: "Varun Mayya",
    bio: "Entrepreneur and business coach",
    profilePhoto: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200",
    role: "Host",
    podcasts: ["Business Masters"]
  },
  {
    id: 5,
    name: "Priya Sharma",
    bio: "Investigative journalist",
    profilePhoto: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200",
    role: "Host",
    podcasts: ["True Crime India"]
  },
  {
    id: 6,
    name: "Dr. Anjali Mehta",
    bio: "Nutritionist and wellness expert",
    profilePhoto: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200",
    role: "Host",
    podcasts: ["Health & Wellness Show"]
  },
  {
    id: 7,
    name: "Rohit Kapoor",
    bio: "Sports analyst and commentator",
    profilePhoto: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200",
    role: "Host",
    podcasts: ["Sports Central"]
  },
  {
    id: 8,
    name: "Prof. Vikram Singh",
    bio: "Historian and author",
    profilePhoto: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=200",
    role: "Host",
    podcasts: ["History Uncovered"]
  },
  {
    id: 9,
    name: "Karan Johar",
    bio: "Film director and producer",
    profilePhoto: "https://images.unsplash.com/photo-1506277886164-e25aa3f4ef7f?w=200",
    role: "Guest",
    podcasts: ["Bollywood Insider"]
  },
  {
    id: 10,
    name: "Ritesh Agarwal",
    bio: "OYO Founder and CEO",
    profilePhoto: "https://images.unsplash.com/photo-1531427186611-ecfd6d936c79?w=200",
    role: "Guest",
    podcasts: ["Business Masters"]
  },
  {
    id: 11,
    name: "Luke Coutinho",
    bio: "Holistic lifestyle coach",
    profilePhoto: "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=200",
    role: "Guest",
    podcasts: ["Health & Wellness Show"]
  },
  {
    id: 12,
    name: "Harsha Bhogle",
    bio: "Cricket commentator",
    profilePhoto: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=200",
    role: "Guest",
    podcasts: ["Sports Central"]
  }
];

export const mockCategories = [
  { id: 1, name: "Technology", slug: "technology", icon: "Laptop", count: 45 },
  { id: 2, name: "Comedy", slug: "comedy", icon: "Laugh", count: 67 },
  { id: 3, name: "Business", slug: "business", icon: "Briefcase", count: 52 },
  { id: 4, name: "Entertainment", slug: "entertainment", icon: "Film", count: 89 },
  { id: 5, name: "True Crime", slug: "true-crime", icon: "Search", count: 34 },
  { id: 6, name: "Health", slug: "health", icon: "Heart", count: 41 },
  { id: 7, name: "Sports", slug: "sports", icon: "Trophy", count: 56 },
  { id: 8, name: "History", slug: "history", icon: "BookOpen", count: 38 }
];

export const mockStats = {
  totalPodcasts: 327,
  totalEpisodes: 4563,
  totalPeople: 892
};

export const mockNews = [
  {
    id: 1,
    title: "PodDB Pro Launches with 300+ Podcasts",
    excerpt: "India's comprehensive podcast database goes live",
    featuredImage: "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=400",
    publishedDate: "2025-09-10"
  },
  {
    id: 2,
    title: "Top 10 Podcasts of September 2025",
    excerpt: "Discover the most popular podcasts this month",
    featuredImage: "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=400",
    publishedDate: "2025-09-08"
  },
  {
    id: 3,
    title: "New Feature: Community Rankings",
    excerpt: "Users can now vote and rank their favorite podcasts",
    featuredImage: "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400",
    publishedDate: "2025-09-05"
  }
];