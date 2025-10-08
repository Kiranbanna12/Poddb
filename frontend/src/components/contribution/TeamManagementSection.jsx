import React, { useState } from 'react';
import { Plus, Trash2, Users, Search, CheckCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { toast } from 'sonner';
import { searchPeople, createPerson } from '../../services/api';

const TeamManagementSection = ({ teamMembers, episodes, onTeamMembersChange }) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEpisodeAssignment, setShowEpisodeAssignment] = useState(false);
  const [currentMember, setCurrentMember] = useState(null);
  
  // Search State
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showAddNew, setShowAddNew] = useState(false);

  // New Person Form State
  const [newPersonData, setNewPersonData] = useState({
    full_name: '',
    role: 'Host',
    bio: '',
    date_of_birth: '',
    location: '',
    profile_photo_url: '',
    instagram_url: '',
    youtube_url: '',
    twitter_url: '',
    facebook_url: '',
    linkedin_url: '',
    website_url: ''
  });

  // Episode Assignment State
  const [selectedEpisodes, setSelectedEpisodes] = useState([]);
  const [episodeSearchTerm, setEpisodeSearchTerm] = useState('');

  const handleSearchPeople = async (query) => {
    if (!query) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const results = await searchPeople(query, 10);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Failed to search people');
    } finally {
      setSearching(false);
    }
  };

  const handleSelectExistingPerson = (person) => {
    setCurrentMember(person);
    setSearchTerm('');
    setSearchResults([]);
    setShowAddNew(false);
    
    // Show episode assignment
    setSelectedEpisodes([]);
    setShowEpisodeAssignment(true);
  };

  const handleAddNewPerson = () => {
    setShowAddNew(true);
    setSearchResults([]);
    setNewPersonData({ ...newPersonData, full_name: searchTerm });
  };

  const handleCreateNewPerson = async () => {
    if (!newPersonData.full_name) {
      toast.error('Please enter person name');
      return;
    }

    try {
      const createdPerson = await createPerson(newPersonData);
      setCurrentMember(createdPerson);
      toast.success('Person added successfully');
      
      // Reset form
      setShowAddNew(false);
      setNewPersonData({
        full_name: '',
        role: 'Host',
        bio: '',
        date_of_birth: '',
        location: '',
        profile_photo_url: '',
        instagram_url: '',
        youtube_url: '',
        twitter_url: '',
        facebook_url: '',
        linkedin_url: '',
        website_url: ''
      });
      
      // Show episode assignment
      setSelectedEpisodes([]);
      setShowEpisodeAssignment(true);
      
    } catch (error) {
      console.error('Create person error:', error);
      toast.error('Failed to create person');
    }
  };

  const handleSaveTeamMember = () => {
    if (!currentMember) return;

    const memberWithEpisodes = {
      ...currentMember,
      assigned_episodes: selectedEpisodes
    };

    onTeamMembersChange([...teamMembers, memberWithEpisodes]);
    toast.success(`${currentMember.full_name} added to team`);
    
    // Reset
    setShowAddModal(false);
    setShowEpisodeAssignment(false);
    setCurrentMember(null);
    setSelectedEpisodes([]);
  };

  const handleRemoveTeamMember = (memberId) => {
    if (window.confirm('Remove this team member?')) {
      onTeamMembersChange(teamMembers.filter(m => m.id !== memberId));
      toast.success('Team member removed');
    }
  };

  const toggleEpisodeSelection = (episodeId) => {
    if (selectedEpisodes.includes(episodeId)) {
      setSelectedEpisodes(selectedEpisodes.filter(id => id !== episodeId));
    } else {
      setSelectedEpisodes([...selectedEpisodes, episodeId]);
    }
  };

  const selectAllEpisodes = () => {
    if (selectedEpisodes.length === episodes.length) {
      setSelectedEpisodes([]);
    } else {
      setSelectedEpisodes(episodes.map(ep => ep.id));
    }
  };

  const filteredEpisodes = episodes.filter(ep =>
    ep.title.toLowerCase().includes(episodeSearchTerm.toLowerCase())
  );

  return (
    <Card className="bg-[#1F1F1F] border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-[#F5C518]">Team Members</h3>
          <p className="text-sm text-gray-400 mt-1">{teamMembers.length} members added</p>
        </div>
        <Button
          onClick={() => {
            setShowAddModal(true);
            setShowAddNew(false);
            setSearchTerm('');
            setSearchResults([]);
          }}
          className="bg-[#5799EF] hover:bg-[#4A8BDB] text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Team Member
        </Button>
      </div>

      {/* Team Members List */}
      {teamMembers.length === 0 ? (
        <div className="text-center py-12 bg-[#2A2A2A] rounded-lg">
          <Users className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400 mb-4">No team members added yet</p>
          <Button
            onClick={() => setShowAddModal(true)}
            className="bg-[#5799EF] hover:bg-[#4A8BDB] text-white"
          >
            Add Your First Team Member
          </Button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {teamMembers.map((member) => (
            <Card key={member.id} className="bg-[#2A2A2A] border-gray-700 p-4">
              <div className="flex items-start gap-3">
                {/* Profile Photo */}
                {member.profile_photo_url ? (
                  <img
                    src={member.profile_photo_url}
                    alt={member.full_name}
                    className="w-16 h-16 rounded-full object-cover flex-shrink-0"
                    onError={(e) => {
                      e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(member.full_name)}&background=5799EF&color=fff`;
                    }}
                  />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-[#5799EF] flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xl font-bold">
                      {member.full_name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                )}

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-white font-semibold">{member.full_name}</h4>
                      <Badge className="bg-gray-700 text-gray-300 mt-1">
                        {member.role}
                      </Badge>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveTeamMember(member.id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-900/20"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  {member.bio && (
                    <p className="text-sm text-gray-400 mt-2 line-clamp-2">
                      {member.bio}
                    </p>
                  )}
                  
                  {member.assigned_episodes && member.assigned_episodes.length > 0 && (
                    <p className="text-xs text-gray-500 mt-2">
                      Featured in {member.assigned_episodes.length} episodes
                    </p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add Team Member Modal */}
      {showAddModal && !showEpisodeAssignment && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <Card className="bg-[#1F1F1F] border-gray-700 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-[#F5C518]">Add Team Member</h3>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowAddModal(false);
                  setShowAddNew(false);
                  setSearchTerm('');
                  setSearchResults([]);
                }}
                className="text-gray-400"
              >
                ✕
              </Button>
            </div>

            {!showAddNew ? (
              <>
                {/* Search Existing People */}
                <div className="mb-6">
                  <Label className="text-gray-300 mb-2">Search Existing Team Members</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      value={searchTerm}
                      onChange={(e) => {
                        setSearchTerm(e.target.value);
                        handleSearchPeople(e.target.value);
                      }}
                      placeholder="Type to search..."
                      className="pl-10 bg-[#2A2A2A] border-gray-600 text-white"
                    />
                  </div>

                  {/* Search Results */}
                  {searchResults.length > 0 && (
                    <div className="mt-2 bg-[#2A2A2A] rounded-lg border border-gray-700 max-h-60 overflow-y-auto">
                      {searchResults.map((person) => (
                        <div
                          key={person.id}
                          onClick={() => handleSelectExistingPerson(person)}
                          className="p-3 hover:bg-[#333333] cursor-pointer border-b border-gray-800 last:border-b-0"
                        >
                          <div className="flex items-center gap-3">
                            {person.profile_photo_url ? (
                              <img
                                src={person.profile_photo_url}
                                alt={person.full_name}
                                className="w-10 h-10 rounded-full object-cover"
                              />
                            ) : (
                              <div className="w-10 h-10 rounded-full bg-[#5799EF] flex items-center justify-center">
                                <span className="text-white font-bold">
                                  {person.full_name.charAt(0).toUpperCase()}
                                </span>
                              </div>
                            )}
                            <div>
                              <p className="text-white font-medium">{person.full_name}</p>
                              <p className="text-xs text-gray-400">{person.role}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {searching && (
                    <p className="text-gray-400 text-sm mt-2">Searching...</p>
                  )}
                </div>

                {/* Add New Person Button */}
                <div className="pt-4 border-t border-gray-700">
                  <Button
                    onClick={handleAddNewPerson}
                    className="w-full bg-[#F5C518] hover:bg-[#E5B718] text-[#0F0F0F]"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add New Person
                  </Button>
                </div>
              </>
            ) : (
              <>
                {/* Add New Person Form */}
                <div className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-gray-300">Full Name *</Label>
                      <Input
                        value={newPersonData.full_name}
                        onChange={(e) => setNewPersonData({ ...newPersonData, full_name: e.target.value })}
                        placeholder="Enter full name"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                    </div>
                    <div>
                      <Label className="text-gray-300">Role *</Label>
                      <select
                        value={newPersonData.role}
                        onChange={(e) => setNewPersonData({ ...newPersonData, role: e.target.value })}
                        className="w-full bg-[#2A2A2A] border border-gray-600 text-white rounded-md px-3 py-2"
                      >
                        <option value="Host">Host</option>
                        <option value="Guest">Guest</option>
                        <option value="Producer">Producer</option>
                        <option value="Editor">Editor</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <Label className="text-gray-300">Bio</Label>
                    <Textarea
                      value={newPersonData.bio}
                      onChange={(e) => setNewPersonData({ ...newPersonData, bio: e.target.value })}
                      placeholder="Brief biography"
                      className="bg-[#2A2A2A] border-gray-600 text-white"
                      rows={3}
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-gray-300">Date of Birth</Label>
                      <Input
                        type="date"
                        value={newPersonData.date_of_birth}
                        onChange={(e) => setNewPersonData({ ...newPersonData, date_of_birth: e.target.value })}
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                    </div>
                    <div>
                      <Label className="text-gray-300">Location</Label>
                      <Input
                        value={newPersonData.location}
                        onChange={(e) => setNewPersonData({ ...newPersonData, location: e.target.value })}
                        placeholder="City, Country"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                    </div>
                  </div>

                  <div>
                    <Label className="text-gray-300">Profile Photo URL</Label>
                    <Input
                      value={newPersonData.profile_photo_url}
                      onChange={(e) => setNewPersonData({ ...newPersonData, profile_photo_url: e.target.value })}
                      placeholder="https://example.com/photo.jpg"
                      className="bg-[#2A2A2A] border-gray-600 text-white"
                    />
                  </div>

                  <div className="pt-4 border-t border-gray-700">
                    <h4 className="text-lg font-semibold text-white mb-3">Social Media Links</h4>
                    <div className="grid md:grid-cols-2 gap-3">
                      <Input
                        value={newPersonData.instagram_url}
                        onChange={(e) => setNewPersonData({ ...newPersonData, instagram_url: e.target.value })}
                        placeholder="Instagram URL"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                      <Input
                        value={newPersonData.youtube_url}
                        onChange={(e) => setNewPersonData({ ...newPersonData, youtube_url: e.target.value })}
                        placeholder="YouTube URL"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                      <Input
                        value={newPersonData.twitter_url}
                        onChange={(e) => setNewPersonData({ ...newPersonData, twitter_url: e.target.value })}
                        placeholder="Twitter URL"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                      <Input
                        value={newPersonData.facebook_url}
                        onChange={(e) => setNewPersonData({ ...newPersonData, facebook_url: e.target.value })}
                        placeholder="Facebook URL"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                      <Input
                        value={newPersonData.linkedin_url}
                        onChange={(e) => setNewPersonData({ ...newPersonData, linkedin_url: e.target.value })}
                        placeholder="LinkedIn URL"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                      <Input
                        value={newPersonData.website_url}
                        onChange={(e) => setNewPersonData({ ...newPersonData, website_url: e.target.value })}
                        placeholder="Website URL"
                        className="bg-[#2A2A2A] border-gray-600 text-white"
                      />
                    </div>
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button
                      onClick={handleCreateNewPerson}
                      className="flex-1 bg-[#5CB85C] hover:bg-[#4CAF50] text-white"
                    >
                      Create Person
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowAddNew(false)}
                      className="border-gray-600 text-gray-300"
                    >
                      Back
                    </Button>
                  </div>
                </div>
              </>
            )}
          </Card>
        </div>
      )}

      {/* Episode Assignment Modal */}
      {showEpisodeAssignment && currentMember && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <Card className="bg-[#1F1F1F] border-gray-700 p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold text-[#F5C518]">Assign Episodes</h3>
                <p className="text-sm text-gray-400 mt-1">
                  Select episodes featuring {currentMember.full_name}
                </p>
              </div>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowEpisodeAssignment(false);
                  setShowAddModal(false);
                  setCurrentMember(null);
                }}
                className="text-gray-400"
              >
                ✕
              </Button>
            </div>

            {/* Episode Search */}
            <div className="mb-4">
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    value={episodeSearchTerm}
                    onChange={(e) => setEpisodeSearchTerm(e.target.value)}
                    placeholder="Search episodes..."
                    className="pl-10 bg-[#2A2A2A] border-gray-600 text-white"
                  />
                </div>
                <Button
                  onClick={selectAllEpisodes}
                  variant="outline"
                  className="border-gray-600 text-gray-300"
                >
                  {selectedEpisodes.length === episodes.length ? 'Deselect All' : 'Select All'}
                </Button>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {selectedEpisodes.length} of {episodes.length} episodes selected
              </p>
            </div>

            {/* Episodes List */}
            {episodes.length === 0 ? (
              <div className="text-center py-8 bg-[#2A2A2A] rounded-lg">
                <p className="text-gray-400">No episodes available</p>
                <p className="text-xs text-gray-500 mt-1">Add episodes first before assigning team members</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredEpisodes.map((episode) => (
                  <div
                    key={episode.id}
                    onClick={() => toggleEpisodeSelection(episode.id)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedEpisodes.includes(episode.id)
                        ? 'bg-[#5799EF] bg-opacity-20 border border-[#5799EF]'
                        : 'bg-[#2A2A2A] hover:bg-[#333333]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {/* Checkbox */}
                      <div className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                        selectedEpisodes.includes(episode.id)
                          ? 'bg-[#5799EF] border-[#5799EF]'
                          : 'border-gray-600'
                      }`}>
                        {selectedEpisodes.includes(episode.id) && (
                          <CheckCircle className="w-4 h-4 text-white" />
                        )}
                      </div>

                      {/* Episode Info */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className="bg-gray-700 text-gray-300 text-xs">
                            Episode {episode.episode_number}
                          </Badge>
                        </div>
                        <p className="text-white text-sm font-medium">{episode.title}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Save Button */}
            <div className="flex gap-2 pt-6 border-t border-gray-700 mt-6">
              <Button
                onClick={handleSaveTeamMember}
                className="flex-1 bg-[#5CB85C] hover:bg-[#4CAF50] text-white"
              >
                Add to Team ({selectedEpisodes.length} episodes)
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowEpisodeAssignment(false);
                  setSelectedEpisodes([]);
                }}
                className="border-gray-600 text-gray-300"
              >
                Cancel
              </Button>
            </div>
          </Card>
        </div>
      )}
    </Card>
  );
};

export default TeamManagementSection;