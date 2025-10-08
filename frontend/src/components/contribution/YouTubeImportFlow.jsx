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
      const data = await fetchYouTubePlaylist(playlistUrl);
      setFetchedData(data);
      setStep('form');
      toast.success(`Fetched ${data.episodes.length} episodes from playlist`);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to fetch playlist. Please check the URL and try again.'
      );
      setStep('input');
    }
  };

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
    );
  }

  return null;
};

export default YouTubeImportFlow;
