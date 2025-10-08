import React, { useState, useEffect } from 'react';
import { Youtube, FileText, ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { toast } from 'sonner';
import YouTubeImportFlow from '../components/contribution/YouTubeImportFlow';
import ManualEntryFlow from '../components/contribution/ManualEntryFlow';

const ContributePageAdvanced = () => {
  const [entryMode, setEntryMode] = useState(null); // null, 'youtube', 'manual'

  // Landing page with two options
  const renderLandingPage = () => (
    <div className="min-h-screen bg-[#0F0F0F] text-white py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-[#F5C518]">
            Contribute to PodDB Pro
          </h1>
          <p className="text-xl text-gray-300 mb-2">
            Help us build the largest podcast database
          </p>
          <p className="text-gray-400">
            Choose how you'd like to add a podcast
          </p>
        </div>

        {/* Two Option Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Option 1: YouTube Import */}
          <Card 
            className="bg-[#1F1F1F] border-2 border-gray-700 hover:border-[#5799EF] transition-all duration-300 cursor-pointer p-8 text-center"
            onClick={() => setEntryMode('youtube')}
          >
            <div className="flex flex-col items-center space-y-4">
              <div className="w-20 h-20 bg-[#5799EF] rounded-full flex items-center justify-center">
                <Youtube className="w-10 h-10 text-white" />
              </div>
              
              <h2 className="text-2xl font-bold text-white">
                Import from YouTube Playlist
              </h2>
              
              <p className="text-gray-400 text-base">
                Automatically import podcast details and all episodes from a YouTube playlist
              </p>
              
              <div className="pt-4 space-y-2 text-sm text-gray-400 text-left w-full">
                <div className="flex items-start gap-2">
                  <span className="text-[#F5C518]">✓</span>
                  <span>Auto-fetch podcast info from playlist</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[#F5C518]">✓</span>
                  <span>Import all episodes at once</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[#F5C518]">✓</span>
                  <span>Auto-sync new episodes daily</span>
                </div>
              </div>

              <Button className="bg-[#5799EF] hover:bg-[#4A8BDB] text-white w-full mt-4">
                Import from Playlist
              </Button>
            </div>
          </Card>

          {/* Option 2: Manual Entry */}
          <Card 
            className="bg-[#1F1F1F] border-2 border-gray-700 hover:border-[#5799EF] transition-all duration-300 cursor-pointer p-8 text-center"
            onClick={() => setEntryMode('manual')}
          >
            <div className="flex flex-col items-center space-y-4">
              <div className="w-20 h-20 bg-[#F5C518] rounded-full flex items-center justify-center">
                <FileText className="w-10 h-10 text-[#0F0F0F]" />
              </div>
              
              <h2 className="text-2xl font-bold text-white">
                Add Manually
              </h2>
              
              <p className="text-gray-400 text-base">
                Add podcast details and episodes one by one with full control
              </p>
              
              <div className="pt-4 space-y-2 text-sm text-gray-400 text-left w-full">
                <div className="flex items-start gap-2">
                  <span className="text-[#F5C518]">✓</span>
                  <span>Enter custom podcast information</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[#F5C518]">✓</span>
                  <span>Add episodes from any source</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-[#F5C518]">✓</span>
                  <span>Complete flexibility</span>
                </div>
              </div>

              <Button className="bg-[#F5C518] hover:bg-[#E5B718] text-[#0F0F0F] w-full mt-4">
                Add Manually
              </Button>
            </div>
          </Card>
        </div>

        {/* Info Section */}
        <div className="mt-12 text-center">
          <Card className="bg-[#1F1F1F] border-gray-700 p-6 max-w-2xl mx-auto">
            <h3 className="text-xl font-semibold text-[#F5C518] mb-3">
              Why Contribute?
            </h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-400">
              <div>
                <div className="text-[#5799EF] text-2xl mb-2">📊</div>
                <p>Help build the most comprehensive podcast database</p>
              </div>
              <div>
                <div className="text-[#5799EF] text-2xl mb-2">🎯</div>
                <p>Get recognition for your contributions</p>
              </div>
              <div>
                <div className="text-[#5799EF] text-2xl mb-2">🚀</div>
                <p>Support the podcast community</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );

  // Render based on entry mode
  if (!entryMode) {
    return renderLandingPage();
  }

  return (
    <div className="min-h-screen bg-[#0F0F0F] text-white py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => setEntryMode(null)}
          className="mb-6 text-gray-400 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Options
        </Button>

        {/* Render selected flow */}
        {entryMode === 'youtube' && <YouTubeImportFlow />}
        {entryMode === 'manual' && <ManualEntryFlow />}
      </div>
    </div>
  );
};

export default ContributePageAdvanced;