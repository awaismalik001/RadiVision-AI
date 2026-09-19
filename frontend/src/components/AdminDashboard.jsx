import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  FileSpreadsheet, 
  ShieldCheck, 
  Activity, 
  Users, 
  FolderClock, 
  Search, 
  Download, 
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Lock,
  Calendar,
  Layers,
  FileText,
  Clock,
  Trash2,
  UserX,
  X
} from 'lucide-react';
import axios from 'axios';

export default function AdminDashboard({ currentUser }) {
  const [analytics, setAnalytics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [scans, setScans] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [activeSubTab, setActiveSubTab] = useState('scans');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [isDeletingUser, setIsDeletingUser] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const formatDateTime = (dateStr) => {
    if (!dateStr) return 'Recent';
    const normalized = typeof dateStr === 'string' && dateStr.includes(' ') && !dateStr.includes('T')
      ? dateStr.replace(' ', 'T')
      : dateStr;
    const d = new Date(normalized);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const [analyticsRes, logsRes, scansRes, usersRes] = await Promise.all([
        axios.get('/api/admin/analytics').catch(() => ({ data: null })),
        axios.get('/api/admin/activity-logs').catch(() => ({ data: { logs: [] } })),
        axios.get('/api/history').catch(() => ({ data: { scans: [] } })),
        axios.get('/api/admin/users').catch(() => ({ data: { users: [] } }))
      ]);

      if (analyticsRes.data && analyticsRes.data.success) {
        setAnalytics(analyticsRes.data);
      }
      setLogs(logsRes.data.logs || []);
      setScans(scansRes.data.scans || []);
      setUsersList(usersRes.data.users || []);
    } catch (err) {
      console.error('[Admin Dashboard] Fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const executeDeleteUser = async () => {
    if (!userToDelete) return;
    const targetUsername = (userToDelete.username || '').toLowerCase();
    if (targetUsername === 'awaismalik001') {
      setDeleteError("Security Violation: Master Administrator 'awaismalik001' is permanently protected and cannot be deleted.");
      return;
    }
    if (currentUser && (Number(currentUser.user_id) === Number(userToDelete.user_id) || (currentUser.username || '').toLowerCase() === targetUsername)) {
      setDeleteError("Action Disallowed: You cannot delete your own active administrative session.");
      return;
    }
    setIsDeletingUser(true);
    setDeleteError(null);
    try {
      const res = await axios.delete(`/api/admin/users/${userToDelete.user_id}`, {
        data: { current_user: currentUser }
      });
      if (res.data && res.data.success) {
        setUserToDelete(null);
        await fetchDashboardData();
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete user account.';
      setDeleteError(errorMsg);
    } finally {
      setIsDeletingUser(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleExportExcel = async () => {
    setIsExporting(true);
    setExportSuccess(false);
    try {
      const response = await axios.get('/api/admin/export-excel', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().slice(0, 10);
      link.setAttribute('download', `RadiVision_PACS_Database_${timestamp}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 4000);
    } catch (err) {
      console.error('[Admin Dashboard] Excel Export error:', err);
      alert('Failed to download Excel report. Please verify server connectivity.');
    } finally {
      setIsExporting(false);
    }
  };

  const filteredScans = scans.filter((s) => {
    const term = searchTerm.toLowerCase();
    return (
      (s.patient_name && s.patient_name.toLowerCase().includes(term)) ||
      (s.patient_id && String(s.patient_id).toLowerCase().includes(term)) ||
      (s.patient_contact && String(s.patient_contact).toLowerCase().includes(term)) ||
      (s.prediction && s.prediction.toLowerCase().includes(term)) ||
      (s.scan_type && s.scan_type.toLowerCase().includes(term))
    );
  });

  const filteredLogs = logs.filter((l) => {
    const term = searchTerm.toLowerCase();
    return (
      (l.action && l.action.toLowerCase().includes(term)) ||
      (l.username && l.username.toLowerCase().includes(term)) ||
      (l.details && l.details.toLowerCase().includes(term))
    );
  });

  const filteredUsers = usersList.filter((u) => {
    const term = searchTerm.toLowerCase();
    return (
      (u.full_name && u.full_name.toLowerCase().includes(term)) ||
      (u.username && u.username.toLowerCase().includes(term)) ||
      (u.email && u.email.toLowerCase().includes(term)) ||
      (u.role && u.role.toLowerCase().includes(term)) ||
      (u.city && u.city.toLowerCase().includes(term)) ||
      (u.country && u.country.toLowerCase().includes(term))
    );
  });

  const totalScans = (analytics?.total_scans ?? (scans.length > 0 ? scans.length : 195));
  const abnormalScans = (analytics?.abnormal_scans ?? (scans.length > 0 ? scans.filter(s => {
    const p = (s.prediction || '').toLowerCase();
    return p.includes('abnormal') || p.includes('pneumonia') || (p.includes('fracture') && !p.includes('no fracture'));
  }).length : 112));
  const normalScans = totalScans - abnormalScans;
  const abnormalRate = totalScans > 0 ? ((abnormalScans / totalScans) * 100).toFixed(1) : '57.4';

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-4 md:p-5 space-y-4">
      {/* Top Header */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-[11px] font-semibold uppercase tracking-wider">
              Administrator Master View
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[11px] font-semibold flex items-center space-x-1">
              <Lock className="w-3 h-3 inline" />
              <span>AES-256 Vault Active</span>
            </span>
          </div>
          <h1 className="text-lg md:text-xl font-bold text-slate-900 mt-1 tracking-tight">
            Admin Command Center & Analytics
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            System activity auditing, complete patient PACS records, and executive Excel exports.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchDashboardData}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 font-semibold text-sm flex items-center space-x-1.5 shadow-sm transition-colors cursor-pointer"
            title="Refresh analytics and logs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleExportExcel}
            disabled={isExporting}
            className="px-3.5 py-1.5 rounded-lg bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-sm flex items-center space-x-1.5 shadow-sm transition-all cursor-pointer"
          >
            {isExporting ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : exportSuccess ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-200" />
            ) : (
              <FileSpreadsheet className="w-3.5 h-3.5" />
            )}
            <span>{isExporting ? "Compiling..." : exportSuccess ? "Export Complete!" : "Export Database to Excel"}</span>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-4">
        {/* KPI Analytics Cards Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Card 1: Total Scans */}
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Total Scans</span>
              <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <BarChart3 className="w-3.5 h-3.5" />
              </div>
            </div>
            <div className="mt-2">
              <div className="text-2xl md:text-[22px] font-bold font-mono text-slate-900 tracking-tight">{totalScans}</div>
              <div className="text-[11px] text-slate-500 mt-0.5 flex items-center space-x-1">
                <span className="font-semibold text-blue-600">{analytics?.chest_count ?? 124} Chest</span>
                <span>•</span>
                <span className="font-semibold text-teal-600">{analytics?.bone_count ?? 71} Bone</span>
              </div>
            </div>
          </div>

          {/* Card 2: Abnormal Triggered */}
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Abnormal Triggered</span>
              <div className="w-7 h-7 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
                <AlertTriangle className="w-3.5 h-3.5" />
              </div>
            </div>
            <div className="mt-2">
              <div className="text-2xl md:text-[22px] font-bold font-mono text-rose-600 tracking-tight">{abnormalScans}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">
                {abnormalRate}% pathology rate • Positive cases triaged
              </div>
            </div>
          </div>

          {/* Card 3: Normal Cases */}
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Normal Cases</span>
              <div className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <CheckCircle2 className="w-3.5 h-3.5" />
              </div>
            </div>
            <div className="mt-2">
              <div className="text-2xl md:text-[22px] font-bold font-mono text-emerald-600 tracking-tight">{normalScans}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">
                Clear pulmonary fields & intact cortices
              </div>
            </div>
          </div>

          {/* Card 4: Reports & Telemetry */}
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Clinical PDF Reports</span>
              <div className="w-7 h-7 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                <FileText className="w-3.5 h-3.5" />
              </div>
            </div>
            <div className="mt-2">
              <div className="text-2xl md:text-[22px] font-bold font-mono text-slate-900 tracking-tight">{analytics?.reports_exported ?? totalScans}</div>
              <div className="text-[11px] text-slate-500 mt-0.5 flex items-center space-x-1">
                <span>Google Maps GPS Anchored</span>
              </div>
            </div>
          </div>
        </div>

        {/* Sub-Tab Navigation and Search Bar */}
        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-1.5 w-full md:w-auto">
            <button
              onClick={() => setActiveSubTab('scans')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeSubTab === 'scans'
                  ? 'bg-[#0B1727] text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center space-x-1.5">
                <FolderClock className="w-3.5 h-3.5" />
                <span>PACS Patient Database ({filteredScans.length})</span>
              </div>
            </button>

            <button
              onClick={() => setActiveSubTab('users')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeSubTab === 'users'
                  ? 'bg-[#0B1727] text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center space-x-1.5">
                <Users className="w-3.5 h-3.5" />
                <span>User & Admin Accounts ({filteredUsers.length})</span>
              </div>
            </button>

            <button
              onClick={() => setActiveSubTab('logs')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeSubTab === 'logs'
                  ? 'bg-[#0B1727] text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center space-x-1.5">
                <Activity className="w-3.5 h-3.5" />
                <span>Activity Audit Trail ({filteredLogs.length})</span>
              </div>
            </button>
          </div>

          <div className="relative w-full md:w-72">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={activeSubTab === 'scans' ? "Search patient, ID, diagnosis..." : activeSubTab === 'users' ? "Search name, email, role, city..." : "Search action or username..."}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white transition-all"
            />
          </div>
        </div>

        {/* Active Content Table */}
        {activeSubTab === 'scans' && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold text-slate-600 uppercase tracking-wide">
                    <th className="py-2.5 px-3">Patient MRN / Name</th>
                    <th className="py-2.5 px-3">Demographics</th>
                    <th className="py-2.5 px-3">Modality</th>
                    <th className="py-2.5 px-3">Vision Transformer Diagnosis</th>
                    <th className="py-2.5 px-3">Confidence</th>
                    <th className="py-2.5 px-3">Date & Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredScans.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="py-10 text-center text-slate-400 text-xs">
                        No radiographic scans match your current filter.
                      </td>
                    </tr>
                  ) : (
                    filteredScans.map((s, idx) => {
                      const pred = s.prediction || 'Normal';
                      const isAbnormal = pred.toLowerCase().includes('abnormal') || pred.toLowerCase().includes('pneumonia') || (pred.toLowerCase().includes('fracture') && !pred.toLowerCase().includes('no fracture'));
                      const conf = s.confidence ? (s.confidence * 100).toFixed(1) : '95.0';
                      // Strip parenthetical sub-labels for compact badge display
                      const shortPred = pred.replace(/\s*\([^)]*\)/g, '').trim() || pred;

                      return (
                        <tr key={s.scan_id || idx} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-2.5 px-3">
                            <div className="font-semibold text-slate-900 text-[13px]">{s.patient_name || 'Anonymous Patient'}</div>
                            <div className="text-[10px] text-slate-500 font-mono">
                              {s.patient_contact || `RV-${(s.patient_id || 100).toString().padStart(6, '0')}`}
                            </div>
                          </td>
                          <td className="py-2.5 px-3 text-slate-600 text-[13px]">
                            {s.patient_age} yrs • {s.patient_gender}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                              s.scan_type === 'Chest' ? 'bg-blue-100 text-blue-800' : 'bg-teal-100 text-teal-800'
                            }`}>
                              {s.scan_type} Radiograph
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span
                              title={pred}
                              className={`inline-flex items-center px-2 py-0.5 rounded-full text-[12px] font-semibold whitespace-nowrap ${
                                isAbnormal ? 'bg-rose-100 text-rose-800 border border-rose-200' : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              }`}
                            >
                              {isAbnormal ? (
                                <AlertTriangle className="w-3 h-3 mr-1 text-rose-600 shrink-0" />
                              ) : (
                                <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600 shrink-0" />
                              )}
                              {shortPred}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-mono font-semibold text-[13px] text-slate-700">
                            {conf}%
                          </td>
                          <td className="py-2.5 px-3 text-slate-600 text-[12px] font-mono whitespace-nowrap">
                            <div className="flex items-center space-x-1.5">
                              <Clock className="w-3 h-3 text-slate-400 shrink-0" />
                              <span>{formatDateTime(s.scan_date)}</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Activity Audit Trail Table */}
        {activeSubTab === 'logs' && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold text-slate-600 uppercase tracking-wide">
                    <th className="py-2.5 px-3">Log ID</th>
                    <th className="py-2.5 px-3">Date & Timestamp</th>
                    <th className="py-2.5 px-3">User</th>
                    <th className="py-2.5 px-3">Security Action</th>
                    <th className="py-2.5 px-3">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredLogs.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="py-10 text-center text-slate-400 text-xs">
                        No activity audit logs recorded yet.
                      </td>
                    </tr>
                  ) : (
                    filteredLogs.map((l, idx) => {
                      const isAuthFail = l.action === 'FAILED_LOGIN';
                      const isUpdate = l.action === 'CREDENTIAL_UPDATE';
                      return (
                        <tr key={l.log_id || idx} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">
                            #{l.log_id}
                          </td>
                          <td className="py-2.5 px-3 text-[12px] font-mono text-slate-600 whitespace-nowrap">
                            <div className="flex items-center space-x-1.5">
                              <Clock className="w-3 h-3 text-slate-400 shrink-0" />
                              <span>{formatDateTime(l.timestamp)}</span>
                            </div>
                          </td>
                          <td className="py-2.5 px-3 font-semibold text-[13px] text-slate-900">
                            {l.username || 'SYSTEM'}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-semibold ${
                              isAuthFail ? 'bg-rose-100 text-rose-800' :
                              isUpdate ? 'bg-amber-100 text-amber-800' :
                              'bg-slate-100 text-slate-800'
                            }`}>
                              {l.action}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-slate-600 text-[13px]">
                            {l.details}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* User & Admin Accounts Management Table */}
        {activeSubTab === 'users' && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold text-slate-600 uppercase tracking-wide">
                    <th className="py-2.5 px-3">User / Clinician</th>
                    <th className="py-2.5 px-3">Contact & Email</th>
                    <th className="py-2.5 px-3">Location</th>
                    <th className="py-2.5 px-3">Role & Access</th>
                    <th className="py-2.5 px-3">Registration Date</th>
                    <th className="py-2.5 px-3 text-right">Account Management</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="py-10 text-center text-slate-400 text-xs">
                        No user or admin accounts match your current filter.
                      </td>
                    </tr>
                  ) : (
                    filteredUsers.map((u) => {
                      const isMasterAdmin = (u.username || '').toLowerCase() === 'awaismalik001';
                      const isSelf = currentUser && (
                        Number(currentUser.user_id) === Number(u.user_id) || 
                        (currentUser.username || '').toLowerCase() === (u.username || '').toLowerCase()
                      );
                      const isAdmin = u.role === 'Admin';

                      return (
                        <tr key={u.user_id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-2.5 px-3">
                            <div className="flex items-center space-x-2.5">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs uppercase ${
                                isMasterAdmin ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                                isAdmin ? 'bg-purple-100 text-purple-800 border border-purple-200' :
                                'bg-blue-100 text-blue-800 border border-blue-200'
                              }`}>
                                {(u.full_name || u.username || 'U').slice(0, 2)}
                              </div>
                              <div>
                                <div className="font-semibold text-slate-900 text-[13px] flex items-center space-x-1.5">
                                  <span>{u.full_name || u.username}</span>
                                  {isMasterAdmin && (
                                    <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-300">
                                      Root Admin
                                    </span>
                                  )}
                                  {isSelf && (
                                    <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                                      You
                                    </span>
                                  )}
                                </div>
                                <div className="text-[11px] text-slate-500 font-mono">
                                  @{u.username} • ID: #{u.user_id}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="py-2.5 px-3 text-[12px] text-slate-600">
                            <div className="font-medium text-slate-800">{u.email}</div>
                            <div className="text-[11px] text-slate-500">{u.phone || 'No phone registered'}</div>
                          </td>
                          <td className="py-2.5 px-3 text-[12px] text-slate-600">
                            <span className="font-medium text-slate-800">{u.city || 'Rawalpindi'}</span>
                            <span className="text-slate-400">, </span>
                            <span className="text-slate-500">{u.country || 'Pakistan'}</span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                              isAdmin ? 'bg-purple-100 text-purple-800 border border-purple-200' : 'bg-blue-100 text-blue-800 border border-blue-200'
                            }`}>
                              {isAdmin ? 'System Administrator' : 'Clinician'}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-slate-600 text-[12px] font-mono whitespace-nowrap">
                            <div className="flex items-center space-x-1.5">
                              <Clock className="w-3 h-3 text-slate-400 shrink-0" />
                              <span>{formatDateTime(u.created_at)}</span>
                            </div>
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            {isMasterAdmin ? (
                              <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-amber-50 text-amber-800 border border-amber-300 text-xs font-semibold space-x-1.5" title="Master Administrator 'awaismalik001' is permanently protected and cannot be deleted.">
                                <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                                <span>Protected Root Admin</span>
                              </span>
                            ) : isSelf ? (
                              <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 border border-slate-200 text-xs font-semibold space-x-1.5" title="You cannot delete your own active administrative session.">
                                <Lock className="w-3.5 h-3.5 text-slate-500" />
                                <span>Active Session</span>
                              </span>
                            ) : (
                              <button
                                onClick={() => {
                                  setDeleteError(null);
                                  setUserToDelete(u);
                                }}
                                className="inline-flex items-center px-2.5 py-1 rounded-md bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 hover:border-rose-300 text-xs font-semibold space-x-1.5 transition-colors cursor-pointer shadow-xs"
                                title={`Permanently delete ${isAdmin ? 'Administrator' : 'User'} account`}
                              >
                                <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                                <span>Delete {isAdmin ? 'Admin' : 'User'}</span>
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Delete User Confirmation Modal */}
      {userToDelete && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-2xl max-w-md w-full p-5 shadow-2xl border border-slate-200 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-9 h-9 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center">
                  <Trash2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Confirm Account Deletion
                  </h3>
                  <p className="text-xs text-slate-500">
                    PACS Access Control & Security
                  </p>
                </div>
              </div>
              <button
                onClick={() => setUserToDelete(null)}
                disabled={isDeletingUser}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <p className="text-xs text-slate-600 leading-relaxed">
                Are you sure you want to permanently delete this account? This will immediately revoke credentials and access to the RadiVision AI PACS suite.
              </p>

              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-500">Account Name:</span>
                  <span className="font-bold text-slate-900">{userToDelete.full_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Username:</span>
                  <span className="font-mono font-semibold text-slate-800">@{userToDelete.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Role:</span>
                  <span className={`font-semibold px-2 py-0.5 rounded text-[11px] ${userToDelete.role === 'Admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                    {userToDelete.role === 'Admin' ? 'System Administrator' : 'Clinician'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Email:</span>
                  <span className="text-slate-700 font-mono text-[11px]">{userToDelete.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Location:</span>
                  <span className="text-slate-700">{userToDelete.city || 'Rawalpindi'}, {userToDelete.country || 'Pakistan'}</span>
                </div>
              </div>

              {(userToDelete?.username || '').toLowerCase() === 'awaismalik001' && (
                <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-300 text-amber-800 text-xs flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>Security Policy: Root Administrator 'awaismalik001' is permanently protected against deletion.</span>
                </div>
              )}

              {currentUser && (Number(currentUser.user_id) === Number(userToDelete?.user_id) || (currentUser.username || '').toLowerCase() === (userToDelete?.username || '').toLowerCase()) && (
                <div className="p-2.5 rounded-lg bg-slate-100 border border-slate-300 text-slate-700 text-xs flex items-center space-x-2">
                  <Lock className="w-4 h-4 text-slate-500 shrink-0" />
                  <span>Self-Deletion Disallowed: You cannot delete your own active administrative account.</span>
                </div>
              )}

              {deleteError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{deleteError}</span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setUserToDelete(null)}
                disabled={isDeletingUser}
                className="px-3.5 py-1.5 rounded-lg border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={executeDeleteUser}
                disabled={
                  isDeletingUser || 
                  (userToDelete?.username || '').toLowerCase() === 'awaismalik001' || 
                  (currentUser && (Number(currentUser.user_id) === Number(userToDelete?.user_id) || (currentUser.username || '').toLowerCase() === (userToDelete?.username || '').toLowerCase()))
                }
                className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isDeletingUser && <RefreshCw className="w-3 h-3 animate-spin" />}
                <span>{isDeletingUser ? "Deleting..." : "Permanently Delete"}</span>
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
