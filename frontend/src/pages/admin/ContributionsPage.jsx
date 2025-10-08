import React, { useState, useEffect } from 'react';
import { Eye, Check, X, FileText, Clock, CheckCircle, XCircle } from 'lucide-react';
import { getContributions, getContributionDetails, approveContribution, rejectContribution } from '../../services/adminApi';
import { useToast } from '../../hooks/use-toast';

export default function ContributionsPage() {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    contribution_type: '',
    page: 1,
    limit: 20
  });
  const [selectedContribution, setSelectedContribution] = useState(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadContributions();
  }, [filters]);

  const loadContributions = async () => {
    try {
      setLoading(true);
      const data = await getContributions(filters);
      setContributions(data.contributions);
    } catch (error) {
      console.error('Failed to load contributions:', error);
      toast({
        title: "Error",
        description: "Failed to load contributions",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (contributionId) => {
    try {
      const data = await getContributionDetails(contributionId);
      setSelectedContribution(data.contribution);
      setShowReviewModal(true);
    } catch (error) {
      console.error('Failed to load contribution details:', error);
      toast({
        title: "Error",
        description: "Failed to load contribution details",
        variant: "destructive"
      });
    }
  };

  const handleApprove = async (contributionId) => {
    if (!window.confirm('Are you sure you want to approve this contribution?')) return;
    
    try {
      setActionLoading(true);
      await approveContribution(contributionId);
      toast({
        title: "Success",
        description: "Contribution approved successfully",
      });
      loadContributions();
      setShowReviewModal(false);
    } catch (error) {
      console.error('Failed to approve contribution:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to approve contribution",
        variant: "destructive"
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      toast({
        title: "Error",
        description: "Please provide a rejection reason",
        variant: "destructive"
      });
      return;
    }

    try {
      setActionLoading(true);
      await rejectContribution(selectedContribution.id, {
        status: 'rejected',
        rejection_reason: rejectionReason
      });
      toast({
        title: "Success",
        description: "Contribution rejected successfully",
      });
      loadContributions();
      setShowRejectModal(false);
      setShowReviewModal(false);
      setRejectionReason('');
    } catch (error) {
      console.error('Failed to reject contribution:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to reject contribution",
        variant: "destructive"
      });
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-[#F5C518] text-black',
      in_review: 'bg-[#5799EF] text-white',
      approved: 'bg-[#5CB85C] text-white',
      rejected: 'bg-[#D9534F] text-white'
    };
    return styles[status] || 'bg-gray-600 text-white';
  };

  const getTypeBadge = (type) => {
    const labels = {
      new_podcast: 'New Podcast',
      update_podcast: 'Update',
      new_episode: 'New Episode',
      new_person: 'New Person'
    };
    return labels[type] || type;
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getRelativeTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    const seconds = Math.floor(Date.now() / 1000 - timestamp);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' min ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
    return Math.floor(seconds / 86400) + ' days ago';
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-[#F5C518] mb-8">Contribution Review</h1>

        {/* Filters */}
        <div className="bg-[#1F1F1F] rounded-lg p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
                className="w-full bg-[#252525] border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-[#5799EF]"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="in_review">In Review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                value={filters.contribution_type}
                onChange={(e) => setFilters({ ...filters, contribution_type: e.target.value, page: 1 })}
                className="w-full bg-[#252525] border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-[#5799EF]"
              >
                <option value="">All Types</option>
                <option value="new_podcast">New Podcast</option>
                <option value="update_podcast">Update Podcast</option>
                <option value="new_episode">New Episode</option>
                <option value="new_person">New Person</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Sort By</label>
              <select
                value={filters.sort_by || 'created_at'}
                onChange={(e) => setFilters({ ...filters, sort_by: e.target.value, page: 1 })}
                className="w-full bg-[#252525] border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-[#5799EF]"
              >
                <option value="created_at">Newest First</option>
                <option value="created_at">Oldest First</option>
              </select>
            </div>
          </div>
        </div>

        {/* Contributions Table */}
        <div className="bg-[#1F1F1F] rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-[#252525] border-b border-gray-700">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-medium">ID</th>
                <th className="px-6 py-4 text-left text-sm font-medium">Type</th>
                <th className="px-6 py-4 text-left text-sm font-medium">Title</th>
                <th className="px-6 py-4 text-left text-sm font-medium">Submitter</th>
                <th className="px-6 py-4 text-left text-sm font-medium">Submitted</th>
                <th className="px-6 py-4 text-left text-sm font-medium">Status</th>
                <th className="px-6 py-4 text-left text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-400">
                    Loading contributions...
                  </td>
                </tr>
              ) : contributions.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-400">
                    No contributions found
                  </td>
                </tr>
              ) : (
                contributions.map((contrib) => (
                  <tr key={contrib.id} className="border-b border-gray-800 hover:bg-[#252525] transition-colors">
                    <td className="px-6 py-4">#{contrib.id}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-[#252525] text-gray-300">
                        {getTypeBadge(contrib.contribution_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="max-w-xs truncate">
                        {contrib.submitted_data?.title || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {contrib.submitter_avatar && (
                          <img src={contrib.submitter_avatar} alt="" className="w-6 h-6 rounded-full" />
                        )}
                        <span>{contrib.submitter_username}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {getRelativeTime(contrib.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(contrib.status)}`}>
                        {contrib.status === 'pending' && <Clock className="w-3 h-3 mr-1" />}
                        {contrib.status === 'approved' && <CheckCircle className="w-3 h-3 mr-1" />}
                        {contrib.status === 'rejected' && <XCircle className="w-3 h-3 mr-1" />}
                        {contrib.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleViewDetails(contrib.id)}
                          className="p-2 bg-[#5799EF] hover:bg-[#4A88DE] rounded-lg transition-colors"
                          title="Review"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {(contrib.status === 'pending' || contrib.status === 'in_review') && (
                          <>
                            <button
                              onClick={() => handleApprove(contrib.id)}
                              className="p-2 bg-[#5CB85C] hover:bg-[#4BA64C] rounded-lg transition-colors"
                              title="Quick Approve"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedContribution(contrib);
                                setShowRejectModal(true);
                              }}
                              className="p-2 bg-[#D9534F] hover:bg-[#C8433F] rounded-lg transition-colors"
                              title="Quick Reject"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Review Modal */}
        {showReviewModal && selectedContribution && (
          <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
            <div className="bg-[#1F1F1F] rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-800 flex items-center justify-between sticky top-0 bg-[#1F1F1F] z-10">
                <h2 className="text-2xl font-bold">Review Contribution #{selectedContribution.id}</h2>
                <button
                  onClick={() => setShowReviewModal(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="p-6">
                {/* Submitter Info */}
                <div className="mb-6 p-4 bg-[#252525] rounded-lg">
                  <h3 className="font-bold mb-2">Submitter Information</h3>
                  <div className="flex items-center gap-4">
                    {selectedContribution.submitter_avatar && (
                      <img src={selectedContribution.submitter_avatar} alt="" className="w-12 h-12 rounded-full" />
                    )}
                    <div>
                      <p className="font-medium">{selectedContribution.submitter_name || selectedContribution.submitter_username}</p>
                      <p className="text-sm text-gray-400">{selectedContribution.submitter_email}</p>
                      <p className="text-xs text-gray-500">Total Contributions: {selectedContribution.contribution_count || 0}</p>
                    </div>
                  </div>
                </div>

                {/* Submitted Data */}
                <div className="mb-6">
                  <h3 className="font-bold mb-4">Submitted Data</h3>
                  <div className="space-y-4">
                    {Object.entries(selectedContribution.submitted_data || {}).map(([key, value]) => (
                      <div key={key} className="p-4 bg-[#252525] rounded-lg">
                        <p className="text-sm font-medium text-gray-400 mb-1">{key.replace(/_/g, ' ').toUpperCase()}</p>
                        <p className="text-white">{typeof value === 'object' ? JSON.stringify(value) : value}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4 pt-6 border-t border-gray-800">
                  <button
                    onClick={() => handleApprove(selectedContribution.id)}
                    disabled={actionLoading}
                    className="flex-1 bg-[#5CB85C] hover:bg-[#4BA64C] text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {actionLoading ? 'Processing...' : 'Approve'}
                  </button>
                  <button
                    onClick={() => setShowRejectModal(true)}
                    disabled={actionLoading}
                    className="flex-1 bg-[#D9534F] hover:bg-[#C8433F] text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Reject
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Reject Modal */}
        {showRejectModal && (
          <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
            <div className="bg-[#1F1F1F] rounded-lg max-w-md w-full p-6">
              <h2 className="text-xl font-bold mb-4">Reject Contribution</h2>
              <p className="text-gray-400 mb-4">Please provide a reason for rejection:</p>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Explain why this submission is being rejected..."
                className="w-full bg-[#252525] border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-[#5799EF] mb-4 min-h-[120px]"
              />
              <div className="flex items-center gap-4">
                <button
                  onClick={() => {
                    setShowRejectModal(false);
                    setRejectionReason('');
                  }}
                  className="flex-1 bg-[#252525] hover:bg-[#2F2F2F] text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReject}
                  disabled={actionLoading || !rejectionReason.trim()}
                  className="flex-1 bg-[#D9534F] hover:bg-[#C8433F] text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {actionLoading ? 'Rejecting...' : 'Reject'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
