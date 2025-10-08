import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Upload, Plus, Trash2, CheckCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { createContribution, getCategories, getLanguages } from '../services/api';

const ContributePage = () => {
  const [availableCategories, setAvailableCategories] = useState([]);
  const [availableLanguages, setAvailableLanguages] = useState([]);
  
  useEffect(() => {
    loadOptions();
  }, []);

  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    youtubePlaylistId: '',
    categories: [],
    languages: [],
    location: '',
    website: '',
    spotifyUrl: '',
    applePodcastsUrl: '',
    jioSaavnUrl: '',
    instagramUrl: '',
    twitterUrl: '',
    youtubeUrl: '',
    teamMembers: [],
    coverImage: null
  });

  const totalSteps = 6;

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleCategory = (category) => {
    if (formData.categories.includes(category)) {
      updateFormData('categories', formData.categories.filter(c => c !== category));
    } else {
      updateFormData('categories', [...formData.categories, category]);
    }
  };

  const toggleLanguage = (language) => {
    if (formData.languages.includes(language)) {
      updateFormData('languages', formData.languages.filter(l => l !== language));
    } else {
      updateFormData('languages', [...formData.languages, language]);
    }
  };

  const addTeamMember = () => {
    const newMember = {
      id: Date.now(),
      name: '',
      role: 'Host',
      bio: '',
      profilePhoto: null
    };
    updateFormData('teamMembers', [...formData.teamMembers, newMember]);
  };

  const removeTeamMember = (id) => {
    updateFormData('teamMembers', formData.teamMembers.filter(m => m.id !== id));
  };

  const updateTeamMember = (id, field, value) => {
    updateFormData('teamMembers', formData.teamMembers.map(m => 
      m.id === id ? { ...m, [field]: value } : m
    ));
  };

  const handleSubmit = async () => {
    try {
      const contributionData = {
        title: formData.title,
        description: formData.description,
        youtube_playlist_id: formData.youtubePlaylistId,
        categories: formData.categories,
        languages: formData.languages,
        location: formData.location,
        website: formData.website,
        spotify_url: formData.spotifyUrl,
        apple_podcasts_url: formData.applePodcastsUrl,
        jiosaavn_url: formData.jioSaavnUrl,
        instagram_url: formData.instagramUrl,
        twitter_url: formData.twitterUrl,
        youtube_url: formData.youtubeUrl,
        team_members: formData.teamMembers,
        cover_image: formData.coverImage
      };

      await createContribution(contributionData);
      
      toast.success("Contribution Submitted!", {
        description: "Your podcast submission is pending review. We'll notify you once it's approved.",
      });
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        youtubePlaylistId: '',
        categories: [],
        languages: [],
        location: '',
        website: '',
        spotifyUrl: '',
        applePodcastsUrl: '',
        jioSaavnUrl: '',
        instagramUrl: '',
        twitterUrl: '',
        youtubeUrl: '',
        teamMembers: [],
        coverImage: null
      });
      setCurrentStep(1);
    } catch (error) {
      console.error('Error submitting contribution:', error);
      toast.error("Submission Failed", {
        description: error.response?.data?.detail || "Please try again later or make sure you're logged in.",
      });
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center space-x-2 mb-8">
      {[...Array(totalSteps)].map((_, index) => (
        <React.Fragment key={index}>
          <div className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold ${
            currentStep > index + 1 ? 'bg-[#5CB85C] text-white' :
            currentStep === index + 1 ? 'bg-[#5799EF] text-white' :
            'bg-[#2A2A2A] text-[#AAAAAA]'
          }`}>
            {currentStep > index + 1 ? <CheckCircle size={20} /> : index + 1}
          </div>
          {index < totalSteps - 1 && (
            <div className={`w-12 h-1 ${currentStep > index + 1 ? 'bg-[#5CB85C]' : 'bg-[#2A2A2A]'}`} />
          )}
        </React.Fragment>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-[#141414] py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Contribute a Podcast</h1>
          <p className="text-[#AAAAAA]">Help us build the most comprehensive podcast database</p>
        </div>

        {renderStepIndicator()}

        <Card className="bg-[#1F1F1F] border-[#2A2A2A] p-8">
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-white mb-6">Basic Information</h2>
              
              <div>
                <Label className="text-[#AAAAAA] mb-2">Podcast Title *</Label>
                <Input
                  value={formData.title}
                  onChange={(e) => updateFormData('title', e.target.value)}
                  placeholder="Enter podcast title"
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">Description *</Label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => updateFormData('description', e.target.value)}
                  placeholder="Describe the podcast..."
                  rows={4}
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">YouTube Playlist ID *</Label>
                <Input
                  value={formData.youtubePlaylistId}
                  onChange={(e) => updateFormData('youtubePlaylistId', e.target.value)}
                  placeholder="PLxxxxxxxxx"
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
                <p className="text-xs text-[#AAAAAA] mt-1">We'll automatically import episodes from this playlist</p>
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">Categories *</Label>
                <div className="flex flex-wrap gap-2">
                  {availableCategories.map(cat => (
                    <Badge
                      key={cat}
                      onClick={() => toggleCategory(cat)}
                      className={`cursor-pointer ${
                        formData.categories.includes(cat)
                          ? 'bg-[#5799EF] text-white hover:bg-[#4A7BC8]'
                          : 'bg-[#2A2A2A] text-[#AAAAAA] hover:bg-[#3A3A3A]'
                      }`}
                    >
                      {cat}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">Languages *</Label>
                <div className="flex flex-wrap gap-2">
                  {availableLanguages.map(lang => (
                    <Badge
                      key={lang}
                      onClick={() => toggleLanguage(lang)}
                      className={`cursor-pointer ${
                        formData.languages.includes(lang)
                          ? 'bg-[#5799EF] text-white hover:bg-[#4A7BC8]'
                          : 'bg-[#2A2A2A] text-[#AAAAAA] hover:bg-[#3A3A3A]'
                      }`}
                    >
                      {lang}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">Location</Label>
                <Input
                  value={formData.location}
                  onChange={(e) => updateFormData('location', e.target.value)}
                  placeholder="City, State, Country"
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">Official Website</Label>
                <Input
                  value={formData.website}
                  onChange={(e) => updateFormData('website', e.target.value)}
                  placeholder="https://podcast-website.com"
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>
            </div>
          )}

          {/* Step 2: Platform Links */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-white mb-6">Platform Links</h2>
              
              <div>
                <Label className="text-[#AAAAAA] mb-2">Spotify URL</Label>
                <Input
                  value={formData.spotifyUrl}
                  onChange={(e) => updateFormData('spotifyUrl', e.target.value)}
                  placeholder="https://open.spotify.com/show/..."
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">Apple Podcasts URL</Label>
                <Input
                  value={formData.applePodcastsUrl}
                  onChange={(e) => updateFormData('applePodcastsUrl', e.target.value)}
                  placeholder="https://podcasts.apple.com/..."
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">JioSaavn URL</Label>
                <Input
                  value={formData.jioSaavnUrl}
                  onChange={(e) => updateFormData('jioSaavnUrl', e.target.value)}
                  placeholder="https://www.jiosaavn.com/..."
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>
            </div>
          )}

          {/* Step 3: Social Media */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-white mb-6">Social Media Links</h2>
              
              <div>
                <Label className="text-[#AAAAAA] mb-2">Instagram URL</Label>
                <Input
                  value={formData.instagramUrl}
                  onChange={(e) => updateFormData('instagramUrl', e.target.value)}
                  placeholder="https://instagram.com/..."
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">Twitter/X URL</Label>
                <Input
                  value={formData.twitterUrl}
                  onChange={(e) => updateFormData('twitterUrl', e.target.value)}
                  placeholder="https://twitter.com/..."
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>

              <div>
                <Label className="text-[#AAAAAA] mb-2">YouTube Channel URL</Label>
                <Input
                  value={formData.youtubeUrl}
                  onChange={(e) => updateFormData('youtubeUrl', e.target.value)}
                  placeholder="https://youtube.com/@..."
                  className="bg-[#2A2A2A] border-[#2A2A2A] text-white focus:border-[#5799EF]"
                />
              </div>
            </div>
          )}

          {/* Step 4: Team Management */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Team Members</h2>
                <Button onClick={addTeamMember} className="bg-[#5799EF] hover:bg-[#4A7BC8] text-white">
                  <Plus size={16} className="mr-2" />
                  Add Member
                </Button>
              </div>

              {formData.teamMembers.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-[#AAAAAA] mb-4">No team members added yet</p>
                  <Button onClick={addTeamMember} className="bg-[#5799EF] hover:bg-[#4A7BC8] text-white">
                    Add First Member
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {formData.teamMembers.map((member) => (
                    <Card key={member.id} className="bg-[#2A2A2A] border-[#3A3A3A] p-4">
                      <div className="flex items-start justify-between mb-4">
                        <h3 className="text-white font-semibold">Team Member</h3>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => removeTeamMember(member.id)}
                          className="text-[#D9534F] hover:text-white hover:bg-[#D9534F]"
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                      <div className="space-y-3">
                        <Input
                          value={member.name}
                          onChange={(e) => updateTeamMember(member.id, 'name', e.target.value)}
                          placeholder="Name"
                          className="bg-[#1F1F1F] border-[#1F1F1F] text-white focus:border-[#5799EF]"
                        />
                        <select
                          value={member.role}
                          onChange={(e) => updateTeamMember(member.id, 'role', e.target.value)}
                          className="w-full bg-[#1F1F1F] border border-[#1F1F1F] text-white rounded-md px-3 py-2 focus:outline-none focus:border-[#5799EF]"
                        >
                          <option value="Host">Host</option>
                          <option value="Producer">Producer</option>
                          <option value="Editor">Editor</option>
                          <option value="Guest">Guest</option>
                        </select>
                        <Textarea
                          value={member.bio}
                          onChange={(e) => updateTeamMember(member.id, 'bio', e.target.value)}
                          placeholder="Brief bio..."
                          rows={2}
                          className="bg-[#1F1F1F] border-[#1F1F1F] text-white focus:border-[#5799EF]"
                        />
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 5: Episode Import */}
          {currentStep === 5 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-white mb-6">Episode Import</h2>
              
              <div className="bg-[#2A2A2A] border border-[#3A3A3A] rounded-lg p-6 text-center">
                <Upload className="text-[#F5C518] mx-auto mb-4" size={48} />
                <p className="text-white font-semibold mb-2">Automatic Episode Import</p>
                <p className="text-[#AAAAAA] text-sm mb-4">
                  Episodes will be automatically imported from the YouTube playlist ID you provided:<br/>
                  <span className="text-[#5799EF] font-mono">{formData.youtubePlaylistId || 'Not provided'}</span>
                </p>
                <p className="text-[#AAAAAA] text-xs">
                  We'll fetch episode titles, descriptions, thumbnails, and metadata from YouTube.
                </p>
              </div>
            </div>
          )}

          {/* Step 6: Preview & Submit */}
          {currentStep === 6 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-white mb-6">Review & Submit</h2>
              
              <div className="space-y-4">
                <div className="bg-[#2A2A2A] rounded-lg p-4">
                  <h3 className="text-white font-semibold mb-2">Basic Information</h3>
                  <p className="text-[#AAAAAA] text-sm"><span className="text-white">Title:</span> {formData.title || 'Not provided'}</p>
                  <p className="text-[#AAAAAA] text-sm"><span className="text-white">Description:</span> {formData.description || 'Not provided'}</p>
                  <p className="text-[#AAAAAA] text-sm"><span className="text-white">Categories:</span> {formData.categories.join(', ') || 'None selected'}</p>
                  <p className="text-[#AAAAAA] text-sm"><span className="text-white">Languages:</span> {formData.languages.join(', ') || 'None selected'}</p>
                </div>

                <div className="bg-[#2A2A2A] rounded-lg p-4">
                  <h3 className="text-white font-semibold mb-2">Team Members</h3>
                  <p className="text-[#AAAAAA] text-sm">{formData.teamMembers.length} members added</p>
                </div>

                <div className="bg-[#0F0F0F] border border-[#F5C518] rounded-lg p-4">
                  <p className="text-[#AAAAAA] text-sm text-center">
                    By submitting, you confirm that all information is accurate and you have the right to share this content.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-[#2A2A2A]">
            <Button
              onClick={prevStep}
              disabled={currentStep === 1}
              variant="outline"
              className="bg-transparent border-[#2A2A2A] text-white hover:bg-[#2A2A2A] disabled:opacity-50"
            >
              <ChevronLeft size={16} className="mr-2" />
              Previous
            </Button>

            {currentStep < totalSteps ? (
              <Button
                onClick={nextStep}
                className="bg-[#5799EF] hover:bg-[#4A7BC8] text-white"
              >
                Next
                <ChevronRight size={16} className="ml-2" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                className="bg-[#5CB85C] hover:bg-[#4A9A4A] text-white"
              >
                Submit Contribution
                <CheckCircle size={16} className="ml-2" />
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ContributePage;