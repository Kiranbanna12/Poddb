import React, { useState } from 'react';
import { Plus, Trash2, Edit2, GripVertical, Youtube, Video, ChevronDown } from 'lucide-react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { toast } from 'sonner';
import { fetchYouTubeVideo, fetchYouTubePlaylist } from '../../services/api';

const EpisodeManagementSection = ({ episodes, onEpisodesChange, mode }) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSeasonModal, setShowSeasonModal] = useState(false);
  const [addMode, setAddMode] = useState('single'); // 'single' or 'playlist'
  const [loading, setLoading] = useState(false);
  
  // Display state - Load More functionality
  const [displayCount, setDisplayCount] = useState(10);
  
  // Add Episode Form State
  const [videoUrl, setVideoUrl] = useState('');
  const [playlistUrl, setPlaylistUrl] = useState('');
  
  // Season Form State
  const [seasonNumber, setSeasonNumber] = useState('');
  const [seasonTitle, setSeasonTitle] = useState('');
  const [seasonDescription, setSeasonDescription] = useState('');
  
  const handleLoadMore = () => {
    setDisplayCount(prev => Math.min(prev + 20, episodes.length));
  };

  const handleAddSingleEpisode = async () => {
    if (!videoUrl) {
      toast.error('Please enter a YouTube video URL');
      return;
    }

    setLoading(true);
    try {
      const episodeData = await fetchYouTubeVideo(videoUrl);
      
      const newEpisode = {
        id: Date.now(),
        episode_number: episodes.length + 1,
        title: episodeData.video.title,
        description: episodeData.video.description,
        thumbnail: episodeData.video.thumbnail_cloudinary,
        youtube_video_id: episodeData.video.video_id,
        published_date: episodeData.video.published_at,
        duration: episodeData.video.duration,
        season_number: 1
      };

      onEpisodesChange([...episodes, newEpisode]);
      toast.success('Episode added successfully');
      setVideoUrl('');
      setShowAddModal(false);
    } catch (error) {
      console.error('Error adding episode:', error);
      toast.error(error.response?.data?.detail || 'Failed to fetch episode. Please check the URL.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddMultipleEpisodes = async () => {
    if (!playlistUrl) {
      toast.error('Please enter a YouTube playlist URL');
      return;
    }

    setLoading(true);
    try {
      const playlistData = await fetchYouTubePlaylist(playlistUrl);
      
      const newEpisodes = playlistData.episodes.map((ep, index) => ({
        id: Date.now() + index,
        episode_number: episodes.length + index + 1,
        title: ep.title,
        description: ep.description,
        thumbnail: ep.thumbnail_cloudinary,
        youtube_video_id: ep.video_id,
        published_date: ep.published_at,
        duration: ep.duration,
        season_number: 1
      }));

      onEpisodesChange([...episodes, ...newEpisodes]);
      toast.success(`${newEpisodes.length} episodes added successfully`);
      setPlaylistUrl('');
      setShowAddModal(false);
    } catch (error) {
      console.error('Error adding episodes:', error);
      toast.error(error.response?.data?.detail || 'Failed to fetch playlist. Please check the URL.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSeason = async () => {
    if (!seasonNumber) {
      toast.error('Please enter season number');
      return;
    }

    // This would open the add episodes modal with season context
    toast.info('Add episodes to this season', {
      description: 'Use the Add Episodes button to add episodes to this season'
    });
    setShowSeasonModal(false);
  };

  const handleDeleteEpisode = (episodeId) => {
    if (window.confirm('Are you sure you want to delete this episode?')) {
      onEpisodesChange(episodes.filter(ep => ep.id !== episodeId));
      toast.success('Episode deleted');
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <Card className="bg-[#1F1F1F] border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-[#F5C518]">Episodes</h3>
          <p className="text-sm text-gray-400 mt-1">{episodes.length} episodes added</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => {
              setAddMode('single');
              setShowAddModal(true);
            }}
            className="bg-[#5799EF] hover:bg-[#4A8BDB] text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Episode
          </Button>
          <Button
            onClick={() => setShowSeasonModal(true)}
            className="bg-[#F5C518] hover:bg-[#E5B718] text-[#0F0F0F]"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Season
          </Button>
        </div>
      </div>

      {/* Episodes List */}
      {episodes.length === 0 ? (
        <div className="text-center py-12 bg-[#2A2A2A] rounded-lg">
          <Video className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400 mb-4">No episodes added yet</p>
          <Button
            onClick={() => {
              setAddMode('single');
              setShowAddModal(true);
            }}
            className="bg-[#5799EF] hover:bg-[#4A8BDB] text-white"
          >
            Add Your First Episode
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {episodes.slice(0, displayCount).map((episode, index) => (
            <div
              key={episode.id}
              className="bg-[#2A2A2A] rounded-lg p-4 flex items-start gap-4 hover:bg-[#333333] transition-colors"
            >
              {/* Thumbnail */}
              {episode.thumbnail && (
                <img
                  src={episode.thumbnail}
                  alt={episode.title}
                  className="w-32 h-20 object-cover rounded flex-shrink-0"
                  onError={(e) => e.target.style.display = 'none'}
                />
              )}

              {/* Episode Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className="bg-[#5799EF] text-white">
                        Episode {episode.episode_number}
                      </Badge>
                      {episode.season_number && (
                        <Badge className="bg-gray-700 text-gray-300">
                          Season {episode.season_number}
                        </Badge>
                      )}
                    </div>
                    <h4 className="text-white font-semibold mb-1 line-clamp-2">
                      {episode.title}
                    </h4>
                    <p className="text-sm text-gray-400 line-clamp-2 mb-2">
                      {episode.description}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>Duration: {formatDuration(episode.duration)}</span>
                      <span>Published: {formatDate(episode.published_date)}</span>
                      {episode.youtube_video_id && (
                        <a
                          href={`https://youtube.com/watch?v=${episode.youtube_video_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#5799EF] hover:underline flex items-center gap-1"
                        >
                          <Youtube className="w-3 h-3" />
                          Watch
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteEpisode(episode.id)}
                    className="text-red-400 hover:text-red-300 hover:bg-red-900/20 flex-shrink-0"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
          
          {/* Load More Button */}
          {displayCount < episodes.length && (
            <div className="text-center py-6">
              <Button
                onClick={handleLoadMore}
                className="bg-[#2A2A2A] hover:bg-[#333333] text-white border border-gray-600"
              >
                <ChevronDown className="w-4 h-4 mr-2" />
                Load More Episodes ({episodes.length - displayCount} remaining)
              </Button>
            </div>
          )}
          
          {/* All Episodes Loaded Message */}
          {displayCount >= episodes.length && episodes.length > 10 && (
            <div className="text-center py-4 text-gray-400 text-sm">
              All {episodes.length} episodes displayed
            </div>
          )}
        </div>
      )}

      {/* Add Episode Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <Card className="bg-[#1F1F1F] border-gray-700 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-[#F5C518]">Add Episodes</h3>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowAddModal(false);
                  setVideoUrl('');
                  setPlaylistUrl('');
                }}
                className="text-gray-400"
              >
                ✕
              </Button>
            </div>

            {/* Tab Selection */}
            <div className="flex gap-2 mb-6">
              <Button
                onClick={() => setAddMode('single')}
                className={addMode === 'single' ? 'bg-[#5799EF] text-white' : 'bg-[#2A2A2A] text-gray-400'}
              >
                <Video className="w-4 h-4 mr-2" />
                Single Video
              </Button>
              <Button
                onClick={() => setAddMode('playlist')}
                className={addMode === 'playlist' ? 'bg-[#5799EF] text-white' : 'bg-[#2A2A2A] text-gray-400'}
              >
                <Youtube className="w-4 h-4 mr-2" />
                Playlist
              </Button>
            </div>

            {/* Single Video Tab */}
            {addMode === 'single' && (
              <div className="space-y-4">
                <div>
                  <Label className="text-gray-300">YouTube Video URL</Label>
                  <Input
                    value={videoUrl}
                    onChange={(e) => setVideoUrl(e.target.value)}
                    placeholder="https://youtube.com/watch?v=..."
                    className="bg-[#2A2A2A] border-gray-600 text-white"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Example: https://youtube.com/watch?v=dQw4w9WgXcQ
                  </p>
                </div>

                <Button
                  onClick={handleAddSingleEpisode}
                  disabled={loading}
                  className="w-full bg-[#5CB85C] hover:bg-[#4CAF50] text-white"
                >
                  {loading ? 'Fetching...' : 'Fetch & Add Episode'}
                </Button>
              </div>
            )}

            {/* Playlist Tab */}
            {addMode === 'playlist' && (
              <div className="space-y-4">
                <div>
                  <Label className="text-gray-300">YouTube Playlist URL</Label>
                  <Input
                    value={playlistUrl}
                    onChange={(e) => setPlaylistUrl(e.target.value)}
                    placeholder="https://youtube.com/playlist?list=..."
                    className="bg-[#2A2A2A] border-gray-600 text-white"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    All videos in this playlist will be added as episodes
                  </p>
                </div>

                <Button
                  onClick={handleAddMultipleEpisodes}
                  disabled={loading}
                  className="w-full bg-[#5CB85C] hover:bg-[#4CAF50] text-white"
                >
                  {loading ? 'Fetching...' : 'Fetch All Episodes'}
                </Button>
              </div>
            )}

            <div className="mt-6 p-4 bg-yellow-900/20 border border-yellow-700 rounded">
              <p className="text-yellow-300 text-sm">
                <strong>Note:</strong> YouTube Data API is required for automatic fetching. 
                If API is not configured, you may need to add episodes manually.
              </p>
            </div>
          </Card>
        </div>
      )}

      {/* Add Season Modal */}
      {showSeasonModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <Card className="bg-[#1F1F1F] border-gray-700 p-6 max-w-xl w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-[#F5C518]">Add Season</h3>
              <Button
                variant="ghost"
                onClick={() => setShowSeasonModal(false)}
                className="text-gray-400"
              >
                ✕
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <Label className="text-gray-300">Season Number *</Label>
                <Input
                  type="number"
                  value={seasonNumber}
                  onChange={(e) => setSeasonNumber(e.target.value)}
                  placeholder="e.g., 1, 2, 3"
                  className="bg-[#2A2A2A] border-gray-600 text-white"
                />
              </div>

              <div>
                <Label className="text-gray-300">Season Title</Label>
                <Input
                  value={seasonTitle}
                  onChange={(e) => setSeasonTitle(e.target.value)}
                  placeholder="e.g., Season 1, First Season"
                  className="bg-[#2A2A2A] border-gray-600 text-white"
                />
              </div>

              <div>
                <Label className="text-gray-300">Season Description</Label>
                <Textarea
                  value={seasonDescription}
                  onChange={(e) => setSeasonDescription(e.target.value)}
                  placeholder="Optional description for this season"
                  className="bg-[#2A2A2A] border-gray-600 text-white"
                  rows={3}
                />
              </div>

              <Button
                onClick={handleAddSeason}
                className="w-full bg-[#5CB85C] hover:bg-[#4CAF50] text-white"
              >
                Create Season
              </Button>
            </div>
          </Card>
        </div>
      )}
    </Card>
  );
};

export default EpisodeManagementSection;