import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Star, TrendingUp, Users, PlayCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { getStats, getTopPodcasts, getEpisodes, getCategories } from '../services/api';
import { mockPeople } from '../mock';

const HomePage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [topPodcastsIndex, setTopPodcastsIndex] = useState(0);
  const [stats, setStats] = useState({ totalPodcasts: 0, totalEpisodes: 0, totalPeople: 0 });
  const [topPodcasts, setTopPodcasts] = useState([]);
  const [episodes, setEpisodes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, podcastsData, episodesData, categoriesData] = await Promise.all([
        getStats(),
        getTopPodcasts(8),
        getEpisodes(8),
        getCategories()
      ]);
      
      setStats(statsData);
      setTopPodcasts(podcastsData);
      setEpisodes(episodesData);
      setCategories(categoriesData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      console.log('Searching for:', searchQuery);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const scrollTopPodcasts = (direction) => {
    if (direction === 'left' && topPodcastsIndex > 0) {
      setTopPodcastsIndex(topPodcastsIndex - 1);
    } else if (direction === 'right' && topPodcastsIndex < topPodcasts.length - 4) {
      setTopPodcastsIndex(topPodcastsIndex + 1);
    }
  };

  const visibleTopPodcasts = topPodcasts.slice(topPodcastsIndex, topPodcastsIndex + 4);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#141414] flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#141414]">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-black to-[#1F1F1F] py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Discover India's Best <span className="text-[#F5C518]">Podcasts</span>
          </h1>
          <p className="text-[#AAAAAA] text-lg md:text-xl mb-8 max-w-2xl mx-auto">
            Your comprehensive database for podcasts, episodes, and creators
          </p>

          {/* Search Box */}
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto mb-12">
            <div className="relative">
              <input
                type="text"
                placeholder="Search for podcasts, episodes, or people..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#2A2A2A] text-white text-lg px-6 py-4 pl-14 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#5799EF] transition-all"
              />
              <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-400" size={24} />
              <Button 
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-[#5799EF] hover:bg-[#4A7BC8] text-white"
              >
                Search
              </Button>
            </div>
          </form>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <Card className="bg-[#1F1F1F] border-[#2A2A2A] p-6">
              <div className="flex items-center justify-center mb-2">
                <PlayCircle className="text-[#F5C518]" size={32} />
              </div>
              <div className="text-3xl font-bold text-[#F5C518] mb-1">{stats.totalPodcasts}</div>
              <div className="text-[#AAAAAA] text-sm">Total Podcasts</div>
            </Card>
            <Card className="bg-[#1F1F1F] border-[#2A2A2A] p-6">
              <div className="flex items-center justify-center mb-2">
                <TrendingUp className="text-[#F5C518]" size={32} />
              </div>
              <div className="text-3xl font-bold text-[#F5C518] mb-1">{stats.totalEpisodes}</div>
              <div className="text-[#AAAAAA] text-sm">Total Episodes</div>
            </Card>
            <Card className="bg-[#1F1F1F] border-[#2A2A2A] p-6">
              <div className="flex items-center justify-center mb-2">
                <Users className="text-[#F5C518]" size={32} />
              </div>
              <div className="text-3xl font-bold text-[#F5C518] mb-1">{stats.totalPeople}</div>
              <div className="text-[#AAAAAA] text-sm">Creators & Hosts</div>
            </Card>
          </div>
        </div>
      </section>

      {/* Top Podcasts Carousel */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-white">Top Rated Podcasts</h2>
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => scrollTopPodcasts('left')}
                disabled={topPodcastsIndex === 0}
                className="bg-[#1F1F1F] border-[#2A2A2A] text-white hover:bg-[#2A2A2A] disabled:opacity-50"
              >
                <ChevronLeft size={20} />
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => scrollTopPodcasts('right')}
                disabled={topPodcastsIndex >= topPodcasts.length - 4}
                className="bg-[#1F1F1F] border-[#2A2A2A] text-white hover:bg-[#2A2A2A] disabled:opacity-50"
              >
                <ChevronRight size={20} />
              </Button>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {visibleTopPodcasts.map((podcast) => (
              <Card 
                key={podcast.id} 
                className="bg-[#1F1F1F] border-[#2A2A2A] hover:border-[#5799EF] transition-all duration-300 hover:shadow-lg hover:shadow-black/50 cursor-pointer group overflow-hidden"
              >
                <div className="relative overflow-hidden">
                  <img 
                    src={podcast.cover_image} 
                    alt={podcast.title}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-2 right-2 bg-black/80 px-2 py-1 rounded flex items-center space-x-1">
                    <Star className="text-[#F5C518] fill-[#F5C518]" size={14} />
                    <span className="text-[#F5C518] font-bold text-sm">{podcast.rating.toFixed(1)}</span>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="text-white font-semibold text-lg mb-2 line-clamp-1">{podcast.title}</h3>
                  <p className="text-[#AAAAAA] text-sm mb-3 line-clamp-2">{podcast.description}</p>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {podcast.categories.slice(0, 2).map((cat, idx) => (
                      <Badge key={idx} className="bg-[#2A2A2A] text-[#AAAAAA] hover:bg-[#3A3A3A] text-xs">
                        {cat}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center justify-between text-xs text-[#AAAAAA]">
                    <span>{formatNumber(podcast.views)} views</span>
                    <span>{podcast.episode_count} episodes</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Latest Episodes */}
      <section className="py-16 px-4 bg-[#0F0F0F]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8">Latest Episodes</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {episodes.map((episode) => (
              <Card 
                key={episode.id} 
                className="bg-[#1F1F1F] border-[#2A2A2A] hover:border-[#5799EF] transition-all duration-300 hover:shadow-lg hover:shadow-black/50 cursor-pointer group"
              >
                <div className="relative overflow-hidden">
                  <img 
                    src={episode.thumbnail} 
                    alt={episode.title}
                    className="w-full h-40 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs text-white">
                    {episode.duration}
                  </div>
                </div>
                <div className="p-4">
                  <div className="text-[#5799EF] text-xs mb-1">{episode.podcast_title}</div>
                  <h3 className="text-white font-semibold text-sm mb-2 line-clamp-2">{episode.title}</h3>
                  <div className="flex items-center justify-between text-xs text-[#AAAAAA]">
                    <span>{formatNumber(episode.views)} views</span>
                    <span>Ep {episode.episode_number}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Featured People - Using mock data for now */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8">Featured Creators</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {mockPeople.map((person) => (
              <div key={person.id} className="text-center group cursor-pointer">
                <div className="relative mb-3 overflow-hidden rounded-full">
                  <img 
                    src={person.profilePhoto} 
                    alt={person.name}
                    className="w-32 h-32 mx-auto rounded-full object-cover border-2 border-[#2A2A2A] group-hover:border-[#5799EF] transition-all duration-300 group-hover:scale-105"
                  />
                </div>
                <h3 className="text-white font-medium text-sm mb-1">{person.name}</h3>
                <p className="text-[#AAAAAA] text-xs">{person.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories Carousel */}
      <section className="py-16 px-4 bg-[#0F0F0F]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8">Browse by Category</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-6">
            {categories.map((category) => (
              <Card 
                key={category.id} 
                className="bg-[#1F1F1F] border-[#2A2A2A] hover:border-[#5799EF] transition-all duration-300 hover:shadow-lg hover:shadow-black/50 cursor-pointer p-6 text-center group"
              >
                <div className="mb-3">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-[#2A2A2A] rounded-full group-hover:bg-[#5799EF] transition-colors">
                    <PlayCircle className="text-[#F5C518] group-hover:text-white transition-colors" size={24} />
                  </div>
                </div>
                <h3 className="text-white font-semibold mb-1">{category.name}</h3>
                <p className="text-[#AAAAAA] text-sm">{category.podcast_count} podcasts</p>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;