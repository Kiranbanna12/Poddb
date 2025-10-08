import React, { useState, useEffect } from 'react';
import { Star, TrendingUp, TrendingDown, Minus, Filter } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { getRankings, getCategories, getLanguages } from '../services/api';

const RankingsPage = () => {
  const [activeTab, setActiveTab] = useState('overall');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLanguage, setSelectedLanguage] = useState('all');
  const [rankedPodcasts, setRankedPodcasts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadRankings();
  }, [activeTab, selectedCategory, selectedLanguage]);

  const loadInitialData = async () => {
    try {
      const [categoriesData, languagesData] = await Promise.all([
        getCategories(),
        getLanguages()
      ]);
      setCategories(categoriesData);
      setLanguages(languagesData);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const loadRankings = async () => {
    try {
      setLoading(true);
      const filters = { limit: 20 };
      if (selectedCategory !== 'all') filters.category = selectedCategory;
      if (selectedLanguage !== 'all') filters.language = selectedLanguage;
      
      const data = await getRankings(activeTab, filters);
      setRankedPodcasts(data);
    } catch (error) {
      console.error('Error loading rankings:', error);
      setRankedPodcasts([]);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return <div className="w-8 h-8 rounded-full bg-[#FFD700] flex items-center justify-center text-black font-bold text-sm">1</div>;
    if (rank === 2) return <div className="w-8 h-8 rounded-full bg-[#C0C0C0] flex items-center justify-center text-black font-bold text-sm">2</div>;
    if (rank === 3) return <div className="w-8 h-8 rounded-full bg-[#CD7F32] flex items-center justify-center text-white font-bold text-sm">3</div>;
    return <div className="w-8 h-8 rounded-full bg-[#2A2A2A] flex items-center justify-center text-white font-bold text-sm">{rank}</div>;
  };

  const getRankChange = (change) => {
    if (change > 0) return <div className="flex items-center text-[#5CB85C] text-sm"><TrendingUp size={16} className="mr-1" />+{change}</div>;
    if (change < 0) return <div className="flex items-center text-[#D9534F] text-sm"><TrendingDown size={16} className="mr-1" />{change}</div>;
    return <div className="flex items-center text-[#AAAAAA] text-sm"><Minus size={16} /></div>;
  };

  const filteredPodcasts = rankedPodcasts;

  return (
    <div className="min-h-screen bg-[#141414] py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Podcast Rankings</h1>
          <p className="text-[#AAAAAA]">Discover the most popular podcasts based on views, ratings, and engagement</p>
        </div>

        {/* Filters */}
        <Card className="bg-[#1F1F1F] border-[#2A2A2A] p-6 mb-8">
          <div className="flex items-center mb-4">
            <Filter className="text-[#F5C518] mr-2" size={20} />
            <h2 className="text-white font-semibold">Filters</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-[#AAAAAA] text-sm mb-2 block">Category</label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-full bg-[#2A2A2A] border-[#2A2A2A] text-white">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent className="bg-[#2A2A2A] border-[#3A3A3A]">
                  <SelectItem value="all" className="text-white hover:bg-[#3A3A3A]">All Categories</SelectItem>
                  {categories.map(cat => (
                    <SelectItem key={cat.id} value={cat.name} className="text-white hover:bg-[#3A3A3A]">
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-[#AAAAAA] text-sm mb-2 block">Language</label>
              <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                <SelectTrigger className="w-full bg-[#2A2A2A] border-[#2A2A2A] text-white">
                  <SelectValue placeholder="All Languages" />
                </SelectTrigger>
                <SelectContent className="bg-[#2A2A2A] border-[#3A3A3A]">
                  <SelectItem value="all" className="text-white hover:bg-[#3A3A3A]">All Languages</SelectItem>
                  {languages.map(lang => (
                    <SelectItem key={lang.id} value={lang.name} className="text-white hover:bg-[#3A3A3A]">
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button 
                onClick={() => {
                  setSelectedCategory('all');
                  setSelectedLanguage('all');
                }}
                variant="outline"
                className="w-full bg-transparent border-[#5799EF] text-[#5799EF] hover:bg-[#5799EF] hover:text-white"
              >
                Reset Filters
              </Button>
            </div>
          </div>
        </Card>

        {/* Ranking Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-[#1F1F1F] border border-[#2A2A2A] mb-6">
            <TabsTrigger value="overall" className="data-[state=active]:bg-[#5799EF] data-[state=active]:text-white">
              Overall Rankings
            </TabsTrigger>
            <TabsTrigger value="weekly" className="data-[state=active]:bg-[#5799EF] data-[state=active]:text-white">
              Weekly Rankings
            </TabsTrigger>
            <TabsTrigger value="monthly" className="data-[state=active]:bg-[#5799EF] data-[state=active]:text-white">
              Monthly Rankings
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab}>
            {loading ? (
              <div className="text-center py-16">
                <p className="text-white text-lg">Loading rankings...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredPodcasts.map((podcast) => (
                <Card 
                  key={podcast.id} 
                  className="bg-[#1F1F1F] border-[#2A2A2A] hover:border-[#5799EF] transition-all duration-300 cursor-pointer"
                >
                  <div className="p-6">
                    <div className="flex items-center space-x-6">
                      {/* Rank Badge */}
                      <div className="flex flex-col items-center space-y-2">
                        {getRankBadge(podcast.rank)}
                        {getRankChange(podcast.rankChange)}
                      </div>

                      {/* Podcast Cover */}
                      <div className="flex-shrink-0">
                        <img 
                          src={podcast.coverImage} 
                          alt={podcast.title}
                          className="w-24 h-24 rounded-lg object-cover"
                        />
                      </div>

                      {/* Podcast Info */}
                      <div className="flex-1">
                        <h3 className="text-white font-semibold text-lg mb-2">{podcast.title}</h3>
                        <p className="text-[#AAAAAA] text-sm mb-3 line-clamp-1">{podcast.description}</p>
                        <div className="flex flex-wrap gap-2 mb-2">
                          {podcast.categories.map((cat, idx) => (
                            <Badge key={idx} className="bg-[#2A2A2A] text-[#AAAAAA] hover:bg-[#3A3A3A] text-xs">
                              {cat}
                            </Badge>
                          ))}
                          {podcast.languages.map((lang, idx) => (
                            <Badge key={idx} className="bg-[#2A2A2A] text-[#5799EF] hover:bg-[#3A3A3A] text-xs">
                              {lang}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Rating */}
                      <div className="flex flex-col items-center space-y-1">
                        <div className="flex items-center space-x-1">
                          <Star className="text-[#F5C518] fill-[#F5C518]" size={20} />
                          <span className="text-[#F5C518] font-bold text-2xl">{podcast.rating}</span>
                        </div>
                        <div className="text-[#AAAAAA] text-xs">/10</div>
                        <div className="text-[#AAAAAA] text-xs">({formatNumber(podcast.totalRatings)})</div>
                      </div>

                      {/* Statistics */}
                      <div className="hidden lg:flex flex-col space-y-2 text-right min-w-[120px]">
                        <div>
                          <div className="text-white font-semibold">{formatNumber(podcast.views)}</div>
                          <div className="text-[#AAAAAA] text-xs">Views</div>
                        </div>
                        <div>
                          <div className="text-white font-semibold">{formatNumber(podcast.likes)}</div>
                          <div className="text-[#AAAAAA] text-xs">Likes</div>
                        </div>
                        <div>
                          <div className="text-white font-semibold">{podcast.episodeCount}</div>
                          <div className="text-[#AAAAAA] text-xs">Episodes</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {filteredPodcasts.length === 0 && (
              <div className="text-center py-16">
                <p className="text-[#AAAAAA] text-lg">No podcasts found matching your filters.</p>
                <Button 
                  onClick={() => {
                    setSelectedCategory('all');
                    setSelectedLanguage('all');
                  }}
                  className="mt-4 bg-[#5799EF] hover:bg-[#4A7BC8] text-white"
                >
                  Reset Filters
                </Button>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default RankingsPage;