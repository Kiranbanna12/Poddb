import React, { useState, useEffect, useRef } from 'react';
import { Youtube, AlertCircle, CheckCircle, Loader2, Download } from 'lucide-react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { toast } from 'sonner';
import { fetchYouTubePlaylistInitial, fetchYouTubePlaylistBatch } from '../../services/api';
import ContributionForm from './ContributionForm';

const YouTubeImportFlow = () => {
  const [step, setStep] = useState('input'); // 'input', 'fetching', 'form'
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [error, setError] = useState(null);
  const [fetchedData, setFetchedData] = useState(null);
  
  // Background fetching state
  const [isBackgroundFetching, setIsBackgroundFetching] = useState(false);
  const [totalEpisodes, setTotalEpisodes] = useState(0);
  const [loadedEpisodes, setLoadedEpisodes] = useState(0);
  const [allEpisodes, setAllEpisodes] = useState([]);
  const backgroundFetchRef = useRef(null);

  const validateYouTubeUrl = (url) => {
    return url.includes('youtube.com/playlist?list=') || url.includes('list=');
  };

  const handleFetchPlaylist = async () => {
    setError(null);

    if (!playlistUrl) {
      setError('Please enter a YouTube playlist URL');
      return;
    }

    if (!validateYouTubeUrl(playlistUrl)) {
      setError('Please enter a valid YouTube playlist URL');
      return;
    }

    setStep('fetching');

    try {
      // Fetch first 10 episodes only
      const data = await fetchYouTubePlaylistInitial(playlistUrl);
      
      setFetchedData({
        playlist: data.playlist,
        episodes: data.episodes
      });
      
      setAllEpisodes(data.episodes);
      setLoadedEpisodes(data.episodes.length);
      setTotalEpisodes(data.total_episodes || data.episodes.length);
      
      setStep('form');
      toast.success(`Loaded first ${data.episodes.length} episodes. Form is ready!`);
      
      // Start background fetching if there are more episodes
      if (data.total_episodes && data.total_episodes > data.episodes.length) {
        startBackgroundFetch(playlistUrl, data.episodes.length, data.total_episodes);
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to fetch playlist. Please check the URL and try again.'
      );
      setStep('input');
    }
  };
  
  const startBackgroundFetch = async (url, startFrom, total) => {
    setIsBackgroundFetching(true);
    let currentIndex = startFrom;
    const batchSize = 20;
    
    backgroundFetchRef.current = async () => {
      try {
        while (currentIndex < total) {
          const data = await fetchYouTubePlaylistBatch(url, currentIndex, batchSize);
          
          if (data.episodes && data.episodes.length > 0) {
            setAllEpisodes(prev => [...prev, ...data.episodes]);
            setLoadedEpisodes(prev => prev + data.episodes.length);
            currentIndex += data.episodes.length;
            
            // Update the form data with new episodes
            setFetchedData(prev => ({
              ...prev,
              episodes: [...prev.episodes, ...data.episodes]
            }));
            
            console.log(`Background fetch: Loaded ${currentIndex}/${total} episodes`);
          } else {
            break;
          }
          
          // Small delay to avoid overwhelming the API
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        setIsBackgroundFetching(false);
        toast.success(`All ${currentIndex} episodes loaded successfully!`);
      } catch (err) {
        console.error('Background fetch error:', err);
        setIsBackgroundFetching(false);
        toast.error('Background fetching stopped. You can continue with loaded episodes.');
      }
    };
    
    // Start the background fetch
    backgroundFetchRef.current();
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (backgroundFetchRef.current) {
        backgroundFetchRef.current = null;
      }
    };
  }, []);

  // Step 1: URL Input
  if (step === 'input') {
    return (
      <Card className="bg-[#1F1F1F] border-gray-700 p-8 max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-[#5799EF] rounded-full flex items-center justify-center mx-auto mb-4">
            <Youtube className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Import from YouTube</h2>
          <p className="text-gray-400">
            Enter a YouTube playlist URL to automatically import podcast details and episodes
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <Label className="text-[#F5C518] text-lg">YouTube Playlist URL</Label>
            <Input
              type="text"
              placeholder="https://youtube.com/playlist?list=..."
              value={playlistUrl}
              onChange={(e) => setPlaylistUrl(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleFetchPlaylist()}
              className="mt-2 bg-[#2A2A2A] border-gray-600 text-white text-lg h-14"
            />
            <p className="text-sm text-gray-400 mt-2">
              Example: https://youtube.com/playlist?list=PLxxxxxx
            </p>
          </div>

          {error && (
            <Alert className="bg-red-900/20 border-red-900">
              <AlertCircle className="w-4 h-4" />
              <AlertDescription className="text-red-300">{error}</AlertDescription>
            </Alert>
          )}

          <Button
            onClick={handleFetchPlaylist}
            className="w-full bg-[#5799EF] hover:bg-[#4A8BDB] text-white h-12 text-lg"
          >
            Fetch Playlist Data
          </Button>
        </div>

        <div className="mt-8 space-y-3 text-sm text-gray-400">
          <h3 className="text-white font-semibold mb-2">What happens next?</h3>
          <div className="flex items-start gap-2">
            <CheckCircle className="w-5 h-5 text-[#5CB85C] flex-shrink-0 mt-0.5" />
            <span>We'll fetch the playlist title, description, and channel name</span>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="w-5 h-5 text-[#5CB85C] flex-shrink-0 mt-0.5" />
            <span>All videos in the playlist will be imported as episodes</span>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="w-5 h-5 text-[#5CB85C] flex-shrink-0 mt-0.5" />
            <span>Thumbnails will be uploaded to our image storage</span>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="w-5 h-5 text-[#5CB85C] flex-shrink-0 mt-0.5" />
            <span>You can review and edit the information before submitting</span>
          </div>
        </div>
      </Card>
    );
  }

  // Step 2: Fetching
  if (step === 'fetching') {
    return (
      <Card className="bg-[#1F1F1F] border-gray-700 p-12 max-w-2xl mx-auto text-center">
        <Loader2 className="w-16 h-16 animate-spin text-[#5799EF] mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Fetching Playlist Data...</h2>
        <p className="text-gray-400">
          This may take a few moments. Please wait while we import your playlist.
        </p>
      </Card>
    );
  }

  // Step 3: Form with fetched data
  if (step === 'form' && fetchedData) {
    return (
      <div>
        {/* Background Loading Status */}
        {isBackgroundFetching && (
          <Card className="bg-[#1F1F1F] border-[#5799EF] p-4 mb-6 max-w-5xl mx-auto">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Download className="w-5 h-5 text-[#5799EF] animate-pulse" />
                <div>
                  <p className="text-white font-medium">Loading episodes in background...</p>
                  <p className="text-sm text-gray-400">
                    {loadedEpisodes} of {totalEpisodes} episodes loaded
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-[#5799EF] font-bold text-lg">
                    {Math.round((loadedEpisodes / totalEpisodes) * 100)}%
                  </p>
                </div>
                <Loader2 className="w-5 h-5 text-[#5799EF] animate-spin" />
              </div>
            </div>
            <div className="mt-3 bg-[#2A2A2A] rounded-full h-2 overflow-hidden">
              <div 
                className="bg-[#5799EF] h-full transition-all duration-500"
                style={{ width: `${(loadedEpisodes / totalEpisodes) * 100}%` }}
              />
            </div>
          </Card>
        )}
        
        {/* Success Status */}
        {!isBackgroundFetching && totalEpisodes > 10 && (
          <Card className="bg-green-900/20 border-green-600 p-4 mb-6 max-w-5xl mx-auto">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <p className="text-green-300">
                All {totalEpisodes} episodes loaded successfully! You can now fill the form.
              </p>
            </div>
          </Card>
        )}
        
        <ContributionForm 
          initialData={{
            title: fetchedData.playlist.title,
            description: fetchedData.playlist.description,
            coverImage: fetchedData.playlist.cover_image_cloudinary,
            youtubePlaylistUrl: playlistUrl,
            channelName: fetchedData.playlist.channel_name,
            episodes: fetchedData.episodes
          }}
          mode="youtube"
        />
      </div>
    );
  }

  return null;
};

export default YouTubeImportFlow;
