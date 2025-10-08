import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { LayoutDashboard, FileText, Podcast, Users, RefreshCw, Activity } from 'lucide-react';
import { getContributionStats, getSyncStats } from '../../services/adminApi';

export default function AdminDashboard() {
  const [contributionStats, setContributionStats] = useState(null);
  const [syncStats, setSyncStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const [contribData, syncData] = await Promise.all([
        getContributionStats(),
        getSyncStats()
      ]);
      setContributionStats(contribData.stats);
      setSyncStats(syncData.stats);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-[#F5C518] mb-8">Admin Dashboard</h1>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {loading ? (
            <>
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bg-[#1F1F1F] rounded-lg p-6 animate-pulse">
                  <div className="h-4 bg-gray-700 rounded w-3/4 mb-4"></div>
                  <div className="h-8 bg-gray-700 rounded w-1/2"></div>
                </div>
              ))}
            </>
          ) : (
            <>
              <div className="bg-[#1F1F1F] rounded-lg p-6 border border-[#F5C518]">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-gray-400">Pending</h3>
                  <FileText className="w-5 h-5 text-[#F5C518]" />
                </div>
                <p className="text-3xl font-bold">{contributionStats?.pending || 0}</p>
              </div>

              <div className="bg-[#1F1F1F] rounded-lg p-6 border border-[#5799EF]">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-gray-400">In Review</h3>
                  <Activity className="w-5 h-5 text-[#5799EF]" />
                </div>
                <p className="text-3xl font-bold">{contributionStats?.in_review || 0}</p>
              </div>

              <div className="bg-[#1F1F1F] rounded-lg p-6 border border-[#5CB85C]">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-gray-400">Approved Today</h3>
                  <FileText className="w-5 h-5 text-[#5CB85C]" />
                </div>
                <p className="text-3xl font-bold">{contributionStats?.approved_today || 0}</p>
              </div>

              <div className="bg-[#1F1F1F] rounded-lg p-6 border border-[#D9534F]">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-gray-400">Rejected Today</h3>
                  <FileText className="w-5 h-5 text-[#D9534F]" />
                </div>
                <p className="text-3xl font-bold">{contributionStats?.rejected_today || 0}</p>
              </div>
            </>
          )}
        </div>

        {/* Sync Stats */}
        {syncStats && (
          <div className="bg-[#1F1F1F] rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-[#5799EF]" />
              Sync Statistics Today
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-gray-400 text-sm">Total Playlists</p>
                <p className="text-2xl font-bold">{syncStats.total_playlists}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Auto-Sync Enabled</p>
                <p className="text-2xl font-bold text-[#5799EF]">{syncStats.auto_sync_enabled}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Syncs Today</p>
                <p className="text-2xl font-bold text-[#5CB85C]">{syncStats.syncs_today}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Episodes Synced</p>
                <p className="text-2xl font-bold text-[#F5C518]">{syncStats.episodes_synced_today}</p>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            to="/admin/contributions"
            className="bg-[#1F1F1F] hover:bg-[#252525] rounded-lg p-6 transition-colors"
          >
            <FileText className="w-8 h-8 text-[#F5C518] mb-4" />
            <h3 className="text-lg font-bold mb-2">Review Contributions</h3>
            <p className="text-gray-400">Approve or reject user submissions</p>
          </Link>

          <Link
            to="/admin/podcasts"
            className="bg-[#1F1F1F] hover:bg-[#252525] rounded-lg p-6 transition-colors"
          >
            <Podcast className="w-8 h-8 text-[#5799EF] mb-4" />
            <h3 className="text-lg font-bold mb-2">Manage Podcasts</h3>
            <p className="text-gray-400">Edit and manage podcast entries</p>
          </Link>

          <Link
            to="/admin/people"
            className="bg-[#1F1F1F] hover:bg-[#252525] rounded-lg p-6 transition-colors"
          >
            <Users className="w-8 h-8 text-[#5CB85C] mb-4" />
            <h3 className="text-lg font-bold mb-2">Manage People</h3>
            <p className="text-gray-400">Edit hosts, guests, and team members</p>
          </Link>

          <Link
            to="/admin/sync"
            className="bg-[#1F1F1F] hover:bg-[#252525] rounded-lg p-6 transition-colors"
          >
            <RefreshCw className="w-8 h-8 text-[#F5C518] mb-4" />
            <h3 className="text-lg font-bold mb-2">Sync Management</h3>
            <p className="text-gray-400">Manage YouTube playlist syncing</p>
          </Link>

          <Link
            to="/admin/episodes"
            className="bg-[#1F1F1F] hover:bg-[#252525] rounded-lg p-6 transition-colors"
          >
            <LayoutDashboard className="w-8 h-8 text-[#5799EF] mb-4" />
            <h3 className="text-lg font-bold mb-2">Manage Episodes</h3>
            <p className="text-gray-400">Edit and organize episodes</p>
          </Link>

          <Link
            to="/admin/activity"
            className="bg-[#1F1F1F] hover:bg-[#252525] rounded-lg p-6 transition-colors"
          >
            <Activity className="w-8 h-8 text-[#D9534F] mb-4" />
            <h3 className="text-lg font-bold mb-2">Activity Logs</h3>
            <p className="text-gray-400">View admin action history</p>
          </Link>
        </div>
      </div>
    </div>
  );
}