import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { toast } from 'sonner';
import { ChevronRight, ChevronLeft, CheckCircle, Loader2 } from 'lucide-react';
import SmartSearchCombobox from '../SmartSearchCombobox';
import EpisodeManagementSection from './EpisodeManagementSection';
import TeamManagementSection from './TeamManagementSection';
import { 
  searchCategories, 
  searchLanguages, 
  searchLocations,
  addNewCategory,
  addNewLanguage,
  createContribution
} from '../../services/api';

const ContributionForm = ({ initialData = {}, mode = 'manual' }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: initialData.title || '',
    description: initialData.description || '',
    coverImage: initialData.coverImage || '',
    youtubePlaylistUrl: initialData.youtubePlaylistUrl || '',
    channelName: initialData.channelName || '',
    categories: [],
    languages: [],
    location: '',
    state: '',
    country: '',
    website: '',
    spotifyUrl: '',
    applePodcastsUrl: '',
    jioSaavnUrl: '',
    amazonUrl: '',
    instagramUrl: '',
    youtubeUrl: '',
    twitterUrl: '',
    facebookUrl: '',
    linkedinUrl: '',
    episodes: initialData.episodes || [],
    teamMembers: []
  });

  const totalSteps = 5;

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCategorySearch = async (query) => {
    try {
      return await searchCategories(query, 10);
    } catch (error) {
      console.error('Category search error:', error);
      return [];
    }
  };

  const handleAddNewCategory = async (data) => {
    try {
      const newCategory = await addNewCategory(data.name, data.description, data.icon);
      toast.success('Category added successfully');
      return newCategory;
    } catch (error) {
      console.error('Add category error:', error);
      throw error;
    }
  };

  const handleLanguageSearch = async (query) => {
    try {
      return await searchLanguages(query, 10);
    } catch (error) {
      console.error('Language search error:', error);
      return [];
    }
  };

  const handleAddNewLanguage = async (data) => {
    try {
      const newLanguage = await addNewLanguage(data.code, data.name, data.native_name);
      toast.success('Language added successfully');
      return newLanguage;
    } catch (error) {
      console.error('Add language error:', error);
      throw error;
    }
  };

  const handleLocationSearch = async (query) => {
    try {
      const results = await searchLocations(query, 10);
      // Format locations for display
      return results.map((loc, idx) => ({
        id: idx,
        name: `${loc.location}${loc.state ? ', ' + loc.state : ''}${loc.country ? ', ' + loc.country : ''}`,
        location: loc.location,
        state: loc.state,
        country: loc.country
      }));
    } catch (error) {
      console.error('Location search error:', error);
      return [];
    }
  };

  const handleLocationSelect = (items) => {
    if (items.length > 0) {
      const selected = items[0];
      updateFormData('location', selected.location);
      updateFormData('state', selected.state);
      updateFormData('country', selected.country);
    }
  };

  const handleSubmit = async () => {
    // Validation
    if (!formData.title) {
      toast.error('Please enter a podcast title');
      return;
    }

    if (formData.categories.length === 0) {
      toast.error('Please select at least one category');
      return;
    }

    if (formData.languages.length === 0) {
      toast.error('Please select at least one language');
      return;
    }

    setSubmitting(true);

    try {
      const contributionData = {
        title: formData.title,
        description: formData.description,
        cover_image: formData.coverImage,
        youtube_playlist_id: formData.youtubePlaylistUrl,
        categories: formData.categories.map(c => c.name),
        languages: formData.languages.map(l => l.name),
        location: formData.location,
        state: formData.state,
        country: formData.country,
        website: formData.website,
        spotify_url: formData.spotifyUrl,
        apple_podcasts_url: formData.applePodcastsUrl,
        jiosaavn_url: formData.jioSaavnUrl,
        amazon_url: formData.amazonUrl,
        instagram_url: formData.instagramUrl,
        youtube_url: formData.youtubeUrl,
        twitter_url: formData.twitterUrl,
        facebook_url: formData.facebookUrl,
        linkedin_url: formData.linkedinUrl,
        episodes: formData.episodes,
        team_members: formData.teamMembers
      };

      await createContribution(contributionData);
      
      toast.success('Contribution Submitted!', {
        description: 'Your podcast submission is pending review. Thank you for contributing!'
      });

      // Redirect or reset
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);

    } catch (error) {
      console.error('Submission error:', error);
      toast.error('Submission Failed', {
        description: error.response?.data?.detail || 'Please try again or make sure you are logged in.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8 space-x-2">
      {[1, 2, 3, 4, 5].map((step) => (
        <React.Fragment key={step}>
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
              step === currentStep
                ? 'bg-[#5799EF] text-white'
                : step < currentStep
                ? 'bg-[#5CB85C] text-white'
                : 'bg-[#2A2A2A] text-gray-400'
            }`}
          >
            {step < currentStep ? <CheckCircle className="w-5 h-5" /> : step}
          </div>
          {step < 5 && (
            <div
              className={`w-12 h-1 ${
                step < currentStep ? 'bg-[#5CB85C]' : 'bg-[#2A2A2A]'
              }`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );

  // Step 1: Basic Information
  const renderStep1 = () => (
    <Card className="bg-[#1F1F1F] border-gray-700 p-6">
      <h3 className="text-2xl font-bold text-[#F5C518] mb-6">Basic Information</h3>
      
      <div className="space-y-4">
        <div>
          <Label className="text-gray-300">Podcast Title *</Label>
          <Input
            value={formData.title}
            onChange={(e) => updateFormData('title', e.target.value)}
            placeholder="Enter podcast title"
            className="bg-[#2A2A2A] border-gray-600 text-white"
          />
        </div>

        <div>
          <Label className="text-gray-300">Description</Label>
          <Textarea
            value={formData.description}
            onChange={(e) => updateFormData('description', e.target.value)}
            placeholder="Enter podcast description"
            className="bg-[#2A2A2A] border-gray-600 text-white"
            rows={5}
          />
        </div>

        {mode === 'youtube' && formData.channelName && (
          <div>
            <Label className="text-gray-300">Channel/Host</Label>
            <Input
              value={formData.channelName}
              readOnly
              className="bg-[#2A2A2A] border-gray-600 text-gray-400"
            />
          </div>
        )}

        <div>
          <Label className="text-gray-300">Cover Image URL</Label>
          <Input
            value={formData.coverImage}
            onChange={(e) => updateFormData('coverImage', e.target.value)}
            placeholder="https://example.com/image.jpg"
            className="bg-[#2A2A2A] border-gray-600 text-white"
          />
          {formData.coverImage && (
            <div className="mt-2">
              <img 
                src={formData.coverImage} 
                alt="Cover preview" 
                className="w-32 h-32 object-cover rounded"
                onError={(e) => e.target.style.display = 'none'}
              />
            </div>
          )}
        </div>

        <SmartSearchCombobox
          label="Categories *"
          placeholder="Search or add categories"
          onSearch={handleCategorySearch}
          onAddNew={handleAddNewCategory}
          onSelect={(items) => updateFormData('categories', items)}
          value={formData.categories}
          displayKey="name"
          addNewFields={[
            { name: 'name', label: 'Category Name', type: 'text', placeholder: 'e.g., Technology' },
            { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Category description' },
            { name: 'icon', label: 'Icon', type: 'text', placeholder: 'e.g., Laptop' }
          ]}
        />

        <SmartSearchCombobox
          label="Languages *"
          placeholder="Search or add languages"
          onSearch={handleLanguageSearch}
          onAddNew={handleAddNewLanguage}
          onSelect={(items) => updateFormData('languages', items)}
          value={formData.languages}
          displayKey="name"
          addNewFields={[
            { name: 'name', label: 'Language Name', type: 'text', placeholder: 'e.g., Hindi' },
            { name: 'code', label: 'Language Code', type: 'text', placeholder: 'e.g., hi' },
            { name: 'native_name', label: 'Native Name', type: 'text', placeholder: 'e.g., हिन्दी' }
          ]}
        />

        <SmartSearchCombobox
          label="Location"
          placeholder="Search location"
          onSearch={handleLocationSearch}
          onSelect={handleLocationSelect}
          value={formData.location ? [{ id: 1, name: formData.location }] : []}
          multiSelect={false}
          displayKey="name"
        />
      </div>
    </Card>
  );

  // Step 2: Platform Links
  const renderStep2 = () => (
    <Card className="bg-[#1F1F1F] border-gray-700 p-6">
      <h3 className="text-2xl font-bold text-[#F5C518] mb-6">Platform & Social Links</h3>
      
      <div className="space-y-4">
        <div>
          <Label className="text-gray-300">Official Website</Label>
          <Input
            value={formData.website}
            onChange={(e) => updateFormData('website', e.target.value)}
            placeholder="https://podcast-website.com"
            className="bg-[#2A2A2A] border-gray-600 text-white"
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <Label className="text-gray-300">Spotify URL</Label>
            <Input
              value={formData.spotifyUrl}
              onChange={(e) => updateFormData('spotifyUrl', e.target.value)}
              placeholder="https://open.spotify.com/..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
          <div>
            <Label className="text-gray-300">Apple Podcasts URL</Label>
            <Input
              value={formData.applePodcastsUrl}
              onChange={(e) => updateFormData('applePodcastsUrl', e.target.value)}
              placeholder="https://podcasts.apple.com/..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <Label className="text-gray-300">JioSaavn URL</Label>
            <Input
              value={formData.jioSaavnUrl}
              onChange={(e) => updateFormData('jioSaavnUrl', e.target.value)}
              placeholder="https://www.jiosaavn.com/..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
          <div>
            <Label className="text-gray-300">Amazon Music URL</Label>
            <Input
              value={formData.amazonUrl}
              onChange={(e) => updateFormData('amazonUrl', e.target.value)}
              placeholder="https://music.amazon.com/..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
        </div>

        <h4 className="text-lg font-semibold text-white mt-6 mb-3">Social Media</h4>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <Label className="text-gray-300">Instagram</Label>
            <Input
              value={formData.instagramUrl}
              onChange={(e) => updateFormData('instagramUrl', e.target.value)}
              placeholder="https://instagram.com/..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
          <div>
            <Label className="text-gray-300">YouTube</Label>
            <Input
              value={formData.youtubeUrl}
              onChange={(e) => updateFormData('youtubeUrl', e.target.value)}
              placeholder="https://youtube.com/@..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <Label className="text-gray-300">Twitter/X</Label>
            <Input
              value={formData.twitterUrl}
              onChange={(e) => updateFormData('twitterUrl', e.target.value)}
              placeholder="https://twitter.com/..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
          <div>
            <Label className="text-gray-300">Facebook</Label>
            <Input
              value={formData.facebookUrl}
              onChange={(e) => updateFormData('facebookUrl', e.target.value)}
              placeholder="https://facebook.com/..."
              className="bg-[#2A2A2A] border-gray-600 text-white"
            />
          </div>
        </div>

        <div>
          <Label className="text-gray-300">LinkedIn</Label>
          <Input
            value={formData.linkedinUrl}
            onChange={(e) => updateFormData('linkedinUrl', e.target.value)}
            placeholder="https://linkedin.com/..."
            className="bg-[#2A2A2A] border-gray-600 text-white"
          />
        </div>
      </div>
    </Card>
  );

  // Step 3: Episodes
  const renderStep3 = () => (
    <EpisodeManagementSection
      episodes={formData.episodes}
      onEpisodesChange={(episodes) => updateFormData('episodes', episodes)}
      mode={mode}
    />
  );

  // Step 4: Team Members
  const renderStep4 = () => (
    <TeamManagementSection
      teamMembers={formData.teamMembers}
      episodes={formData.episodes}
      onTeamMembersChange={(members) => updateFormData('teamMembers', members)}
    />
  );

  // Step 5: Review & Submit
  const renderStep5 = () => (
    <Card className="bg-[#1F1F1F] border-gray-700 p-6">
      <h3 className="text-2xl font-bold text-[#F5C518] mb-6">Review & Submit</h3>
      
      <div className="space-y-6">
        <div>
          <h4 className="text-lg font-semibold text-white mb-2">Podcast Information</h4>
          <div className="bg-[#2A2A2A] p-4 rounded space-y-2 text-sm">
            <p><span className="text-gray-400">Title:</span> <span className="text-white">{formData.title}</span></p>
            <p><span className="text-gray-400">Categories:</span> <span className="text-white">{formData.categories.map(c => c.name).join(', ')}</span></p>
            <p><span className="text-gray-400">Languages:</span> <span className="text-white">{formData.languages.map(l => l.name).join(', ')}</span></p>
            {formData.location && <p><span className="text-gray-400">Location:</span> <span className="text-white">{formData.location}</span></p>}
          </div>
        </div>

        <div>
          <h4 className="text-lg font-semibold text-white mb-2">Episodes</h4>
          <div className="bg-[#2A2A2A] p-4 rounded">
            <p className="text-white">{formData.episodes.length} episodes added</p>
          </div>
        </div>

        <div>
          <h4 className="text-lg font-semibold text-white mb-2">Team Members</h4>
          <div className="bg-[#2A2A2A] p-4 rounded">
            <p className="text-white">{formData.teamMembers.length} team members added</p>
          </div>
        </div>

        <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded">
          <p className="text-yellow-300 text-sm">
            Your contribution will be reviewed by our team. Once approved, it will be visible on PodDB Pro.
          </p>
        </div>
      </div>
    </Card>
  );

  return (
    <div>
      {renderStepIndicator()}

      <div className="mb-6">
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}
        {currentStep === 4 && renderStep4()}
        {currentStep === 5 && renderStep5()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          onClick={prevStep}
          disabled={currentStep === 1}
          variant="outline"
          className="border-gray-600 text-gray-300"
        >
          <ChevronLeft className="w-4 h-4 mr-2" />
          Previous
        </Button>

        {currentStep < totalSteps ? (
          <Button
            onClick={nextStep}
            className="bg-[#5799EF] hover:bg-[#4A8BDB] text-white"
          >
            Next
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={submitting}
            className="bg-[#5CB85C] hover:bg-[#4CAF50] text-white"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                Submit Contribution
                <CheckCircle className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
};

export default ContributionForm;