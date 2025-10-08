import React, { useState, useEffect } from 'react';
import {
  getSyncDashboard,
  getSyncJobs,
  getSyncErrors,
  getSyncConfig,
  updateSyncConfig,
  getApiUsage,
  runFullSync,
  checkNewEpisodes,
  recalculateAnalytics,
  enableSync,
  disableSync,
  resolveError
} from '../../services/adminApi';
import { Play, RefreshCw, Activity, AlertCircle, Settings, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react';

const SyncManagementPage = () => {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [errors, setErrors] = useState([]);
  const [config, setConfig] = useState({});
  const [apiUsage, setApiUsage] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [syncing, setSyncing] = useState(false);
  const [configEdit, setConfigEdit] = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [dashData, jobsData, errorsData, configData, usageData] = await Promise.all([
        getSyncDashboard(),
        getSyncJobs({ limit: 20 }),
        getSyncErrors({ limit: 50, resolved: false }),
        getSyncConfig(),
        getApiUsage(30)
      ]);

      setDashboard(dashData);
      setJobs(jobsData.jobs || []);
      setErrors(errorsData.errors || []);
      setConfig(configData.config || {});
      setApiUsage(usageData.usage || []);
    } catch (error) {
      console.error('Error loading sync data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSync = async (type) => {
    setSyncing(true);
    try {
      let result;
      if (type === 'full') {
        result = await runFullSync();
      } else if (type === 'new_episodes') {
        result = await checkNewEpisodes();
      } else if (type === 'analytics') {
        result = await recalculateAnalytics();
      }
      
      alert(result.message || 'Sync started successfully');
      loadData();
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSyncing(false);
    }
  };

  const handleToggleSync = async () => {
    try {
      const syncEnabled = config.sync_enabled?.value === 'true';
      if (syncEnabled) {
        await disableSync();
        alert('Sync system disabled');
      } else {
        await enableSync();
        alert('Sync system enabled');
      }
      loadData();
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleConfigUpdate = async (key, value) => {
    try {
      await updateSyncConfig(key, value);
      alert('Configuration updated successfully');
      loadData();
      setConfigEdit(null);
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleResolveError = async (errorId) => {
    try {
      await resolveError(errorId);
      loadData();
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      running: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      paused: 'bg-orange-100 text-orange-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#0D0D0D]">
        <div className="text-white">Loading sync data...</div>
      </div>
    );
  }

  const syncEnabled = config.sync_enabled?.value === 'true';
  const isRunning = dashboard?.current_status?.is_running || false;

  return (
    <div className="min-h-screen bg-[#0D0D0D] text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-[#111111]">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Sync Management</h1>
              <p className="text-gray-400 mt-1">Automated YouTube data synchronization</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleToggleSync}
                className={`px-4 py-2 rounded-lg font-medium ${
                  syncEnabled
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {syncEnabled ? 'Disable Sync' : 'Enable Sync'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Status Cards */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
          {/* Current Status */}
          <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-400">Status</h3>
              <Activity className="w-5 h-5 text-blue-500" />
            </div>
            <p className={`text-2xl font-bold ${isRunning ? 'text-blue-500' : 'text-gray-500'}`}>
              {isRunning ? 'Running' : 'Idle'}
            </p>
          </div>

          {/* Last Sync */}
          <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-400">Last Sync</h3>
              <Clock className="w-5 h-5 text-purple-500" />
            </div>
            <p className="text-sm font-bold">
              {dashboard?.last_sync?.completed_at
                ? formatTime(dashboard.last_sync.completed_at)
                : 'Never'}
            </p>
          </div>

          {/* Today's Stats */}
          <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-400">Podcasts Synced</h3>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-2xl font-bold text-green-500">
              {dashboard?.today_stats?.podcasts_synced || 0}
            </p>
          </div>

          {/* New Episodes */}
          <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-400">New Episodes</h3>
              <CheckCircle className="w-5 h-5 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold text-yellow-500">
              {dashboard?.last_sync?.new_episodes_found || 0}
            </p>
          </div>

          {/* Errors */}
          <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-400">Errors</h3>
              <AlertCircle className="w-5 h-5 text-red-500" />
            </div>
            <p className="text-2xl font-bold text-red-500">
              {dashboard?.today_stats?.errors || 0}
            </p>
          </div>
        </div>

        {/* API Usage */}
        <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800 mb-6">
          <h3 className="text-lg font-bold mb-4">YouTube API Quota Usage</h3>
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span>
                {dashboard?.api_usage?.quota_used || 0} / {dashboard?.api_usage?.quota_limit || 10000} units
              </span>
              <span>{dashboard?.api_usage?.percentage?.toFixed(1) || 0}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-4">
              <div
                className={`h-4 rounded-full transition-all ${
                  (dashboard?.api_usage?.percentage || 0) > 90
                    ? 'bg-red-500'
                    : (dashboard?.api_usage?.percentage || 0) > 70
                    ? 'bg-yellow-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(dashboard?.api_usage?.percentage || 0, 100)}%` }}
              />
            </div>
          </div>
          <p className="text-sm text-gray-400">
            {dashboard?.api_usage?.requests_count || 0} API requests made today
          </p>
        </div>

        {/* Action Buttons */}
        <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800 mb-6">
          <h3 className="text-lg font-bold mb-4">Manual Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => handleRunSync('full')}
              disabled={syncing}
              className={`flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                syncing 
                  ? 'bg-gray-700 cursor-not-allowed opacity-50' 
                  : 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
              }`}
            >
              <Play className="w-5 h-5" />
              Run Full Sync
            </button>
            <button
              onClick={() => handleRunSync('new_episodes')}
              disabled={syncing}
              className={`flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                syncing 
                  ? 'bg-gray-700 cursor-not-allowed opacity-50' 
                  : 'bg-yellow-600 hover:bg-yellow-700 cursor-pointer'
              }`}
            >
              <RefreshCw className="w-5 h-5" />
              Check New Episodes
            </button>
            <button
              onClick={() => handleRunSync('analytics')}
              disabled={syncing}
              className={`flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                syncing 
                  ? 'bg-gray-700 cursor-not-allowed opacity-50' 
                  : 'bg-green-600 hover:bg-green-700 cursor-pointer'
              }`}
            >
              <Activity className="w-5 h-5" />
              Recalculate Analytics
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-800 mb-6">
          <div className="flex gap-4">
            {['overview', 'jobs', 'errors', 'config'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === tab
                    ? 'text-yellow-500 border-b-2 border-yellow-500'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'jobs' && (
          <div className="bg-[#1A1A1A] rounded-lg border border-gray-800 overflow-hidden">
            <div className="p-6 border-b border-gray-800">
              <h3 className="text-lg font-bold">Sync Job History</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[#111111] text-gray-400 text-sm">
                  <tr>
                    <th className="px-6 py-3 text-left">Job ID</th>
                    <th className="px-6 py-3 text-left">Type</th>
                    <th className="px-6 py-3 text-left">Status</th>
                    <th className="px-6 py-3 text-left">Started</th>
                    <th className="px-6 py-3 text-left">Duration</th>
                    <th className="px-6 py-3 text-left">Processed</th>
                    <th className="px-6 py-3 text-left">Updated</th>
                    <th className="px-6 py-3 text-left">New Episodes</th>
                    <th className="px-6 py-3 text-left">Errors</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {jobs.length === 0 ? (
                    <tr>
                      <td colSpan="9" className="px-6 py-8 text-center text-gray-400">
                        No sync jobs found
                      </td>
                    </tr>
                  ) : (
                    jobs.map((job) => (
                      <tr key={job.id} className="hover:bg-[#111111] transition-colors">
                        <td className="px-6 py-4">#{job.id}</td>
                        <td className="px-6 py-4 capitalize">{job.job_type.replace('_', ' ')}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(job.status)}`}>
                            {job.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-400">
                          {formatTime(job.started_at)}
                        </td>
                        <td className="px-6 py-4 text-sm">{formatDuration(job.duration_seconds)}</td>
                        <td className="px-6 py-4">{job.items_processed}</td>
                        <td className="px-6 py-4 text-green-500">{job.items_updated}</td>
                        <td className="px-6 py-4 text-yellow-500">{job.new_episodes_found}</td>
                        <td className="px-6 py-4 text-red-500">{job.items_failed}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'errors' && (
          <div className="bg-[#1A1A1A] rounded-lg border border-gray-800 overflow-hidden">
            <div className="p-6 border-b border-gray-800">
              <h3 className="text-lg font-bold">Recent Errors</h3>
            </div>
            <div className="divide-y divide-gray-800">
              {errors.length === 0 ? (
                <div className="px-6 py-8 text-center text-gray-400">
                  No errors found
                </div>
              ) : (
                errors.map((error) => (
                  <div key={error.id} className="p-6 hover:bg-[#111111] transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="px-2 py-1 bg-red-900/30 text-red-400 text-xs font-medium rounded">
                            {error.error_type}
                          </span>
                          <span className="text-gray-400 text-sm">
                            {error.entity_type}: {error.entity_title || error.youtube_id}
                          </span>
                          <span className="text-gray-500 text-sm">
                            {formatTime(error.created_at)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-300">{error.error_message}</p>
                        {error.retry_attempt > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            Retry attempt: {error.retry_attempt}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => handleResolveError(error.id)}
                        className="ml-4 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                      >
                        Resolve
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'config' && (
          <div className="bg-[#1A1A1A] rounded-lg border border-gray-800 overflow-hidden">
            <div className="p-6 border-b border-gray-800">
              <h3 className="text-lg font-bold">Configuration Settings</h3>
            </div>
            <div className="divide-y divide-gray-800">
              {Object.entries(config).map(([key, data]) => (
                <div key={key} className="p-6 hover:bg-[#111111] transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium mb-1">{key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</h4>
                      <p className="text-sm text-gray-400 mb-2">{data.description}</p>
                      {configEdit === key ? (
                        <div className="flex gap-2">
                          <input
                            type={data.type === 'number' ? 'number' : 'text'}
                            defaultValue={data.value}
                            className="px-3 py-1 bg-[#0D0D0D] border border-gray-700 rounded text-sm"
                            id={`config-${key}`}
                          />
                          <button
                            onClick={() => {
                              const value = document.getElementById(`config-${key}`).value;
                              handleConfigUpdate(key, value);
                            }}
                            className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setConfigEdit(null)}
                            className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <p className="text-sm font-mono">
                          {data.type === 'boolean' ? (data.value === 'true' ? 'Enabled' : 'Disabled') : data.value}
                        </p>
                      )}
                    </div>
                    {configEdit !== key && (
                      <button
                        onClick={() => setConfigEdit(key)}
                        className="ml-4 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                      >
                        Edit
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-[#1A1A1A] rounded-lg p-6 border border-gray-800">
              <h3 className="text-lg font-bold mb-4">System Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Sync System</p>
                  <p className="font-medium">{syncEnabled ? 'Enabled' : 'Disabled'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Next Scheduled Sync</p>
                  <p className="font-medium">{dashboard?.next_sync || 'Not scheduled'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Last Sync Duration</p>
                  <p className="font-medium">{formatDuration(dashboard?.last_sync?.duration_seconds)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Items Processed</p>
                  <p className="font-medium">{dashboard?.last_sync?.items_processed || 0}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SyncManagementPage;
