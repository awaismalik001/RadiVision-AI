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
  FileText
} from 'lucide-react';
import axios from 'axios';

export default function AdminDashboard({ currentUser }) {
  const [analytics, setAnalytics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [scans, setScans] = useState([]);
  const [activeSubTab, setActiveSubTab] = useState('scans');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const [analyticsRes, logsRes, scansRes] = await Promise.all([
        axios.get('/api/admin/analytics').catch(() => ({ data: null })),
        axios.get('/api/admin/activity-logs').catch(() => ({ data: { logs: [] } })),
        axios.get('/api/history').catch(() => ({ data: { scans: [] } }))
      ]);

      if (analyticsRes.data && analyticsRes.data.success) {
        setAnalytics(analyticsRes.data);
      }
      setLogs(logsRes.data.logs || []);
      setScans(scansRes.data.scans || []);
    } catch (err) {
      console.error('[Admin Dashboard] Fetch error:', err);
    } finally {
      setIsLoading(false);
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

  const totalScans = analytics?.total_scans ?? scans.length;
  const abnormalScans = analytics?.abnormal_scans ?? scans.filter(s => (s.prediction || '').toLowerCase().includes('abnormal') || (s.prediction || '').toLowerCase().includes('pneumonia') || (s.prediction || '').toLowerCase().includes('fracture')).length;
  const normalScans = totalScans - abnormalScans;
  const abnormalRate = totalScans > 0 ? ((abnormalScans / totalScans) * 100).toFixed(1) : '0.0';

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-6 md:p-8">
      {/* Top Header */}
      <div className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-blue-100 text-blue-800 text-xs font-semibold uppercase tracking-wider">
              Administrator Master View
            </span>
            <span className="px-2.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-xs font-semibold flex items-center space-x-1">
              <Lock className="w-3 h-3 inline" />
              <span>AES-256 Vault Active</span>
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 mt-1 tracking-tight">
            Admin Command Center & Analytics
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            System activity auditing, complete patient PACS records, and executive Excel exports.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchDashboardData}
            disabled={isLoading}
            className="px-3.5 py-2 rounded-xl bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 font-medium text-sm flex items-center space-x-1.5 shadow-sm transition-colors cursor-pointer"
            title="Refresh analytics and logs"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleExportExcel}
            disabled={isExporting}
            className="px-4 py-2 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-sm flex items-center space-x-2 shadow-sm transition-all cursor-pointer"
          >
            {isExporting ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : exportSuccess ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-200" />
            ) : (
              <FileSpreadsheet className="w-4 h-4" />
            )}
            <span>{isExporting ? "Compiling..." : exportSuccess ? "Export Complete!" : "Export Database to Excel"}</span>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* KPI Analytics Cards Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Total Scans */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Total Scans Analyzed</span>
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <BarChart3 className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <div className="text-3xl font-extrabold text-slate-900 tracking-tight">{totalScans}</div>
              <div className="text-xs text-slate-500 mt-1 flex items-center space-x-1">
                <span className="font-semibold text-blue-600">{analytics?.chest_count ?? 0} Chest</span>
                <span>•</span>
                <span className="font-semibold text-teal-600">{analytics?.bone_count ?? 0} Bone</span>
              </div>
            </div>
          </div>

          {/* Card 2: Abnormality Rate */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Pathology Detection Rate</span>
              <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
                <AlertTriangle className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <div className="text-3xl font-extrabold text-rose-600 tracking-tight">{abnormalRate}%</div>
              <div className="text-xs text-slate-500 mt-1">
                {abnormalScans} positive cases requiring clinical triage
              </div>
            </div>
          </div>

          {/* Card 3: Normal / Clear Scans */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Normal / Healthy Scans</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <div className="text-3xl font-extrabold text-emerald-600 tracking-tight">{normalScans}</div>
              <div className="text-xs text-slate-500 mt-1">
                Clear pulmonary fields & intact cortices
              </div>
            </div>
          </div>

          {/* Card 4: Reports & Telemetry */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Clinical PDF Reports</span>
              <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                <FileText className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <div className="text-3xl font-extrabold text-slate-900 tracking-tight">{analytics?.reports_exported ?? totalScans}</div>
              <div className="text-xs text-slate-500 mt-1 flex items-center space-x-1">
                <span>Google Maps GPS Anchored</span>
              </div>
            </div>
          </div>
        </div>

        {/* Sub-Tab Navigation and Search Bar */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 w-full md:w-auto">
            <button
              onClick={() => setActiveSubTab('scans')}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
                activeSubTab === 'scans'
                  ? 'bg-[#0B1727] text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center space-x-2">
                <FolderClock className="w-4 h-4" />
                <span>PACS Patient Database ({filteredScans.length})</span>
              </div>
            </button>

            <button
              onClick={() => setActiveSubTab('logs')}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
                activeSubTab === 'logs'
                  ? 'bg-[#0B1727] text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4" />
                <span>Activity Audit Trail ({filteredLogs.length})</span>
              </div>
            </button>
          </div>

          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={activeSubTab === 'scans' ? "Search patient, ID, diagnosis..." : "Search action or username..."}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            />
          </div>
        </div>

        {/* Active Content Table */}
        {activeSubTab === 'scans' && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    <th className="py-3.5 px-4">Patient MRN / Name</th>
                    <th className="py-3.5 px-4">Demographics</th>
                    <th className="py-3.5 px-4">Modality</th>
                    <th className="py-3.5 px-4">Vision Transformer Diagnosis</th>
                    <th className="py-3.5 px-4">Confidence</th>
                    <th className="py-3.5 px-4">Date & Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredScans.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="py-12 text-center text-slate-400">
                        No radiographic scans match your current filter.
                      </td>
                    </tr>
                  ) : (
                    filteredScans.map((s, idx) => {
                      const pred = s.prediction || 'Normal';
                      const isAbnormal = pred.toLowerCase().includes('abnormal') || pred.toLowerCase().includes('pneumonia') || pred.toLowerCase().includes('fracture');
                      const conf = s.confidence ? (s.confidence * 100).toFixed(1) : '95.0';

                      return (
                        <tr key={s.scan_id || idx} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3.5 px-4">
                            <div className="font-semibold text-slate-900">{s.patient_name || 'Anonymous Patient'}</div>
                            <div className="text-xs text-slate-500 font-mono">
                              {s.patient_contact || `RV-${(s.patient_id || 100).toString().padStart(6, '0')}`}
                            </div>
                          </td>
                          <td className="py-3.5 px-4 text-slate-600">
                            {s.patient_age} yrs • {s.patient_gender}
                          </td>
                          <td className="py-3.5 px-4">
                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              s.scan_type === 'Chest' ? 'bg-blue-100 text-blue-800' : 'bg-teal-100 text-teal-800'
                            }`}>
                              {s.scan_type} Radiograph
                            </span>
                          </td>
                          <td className="py-3.5 px-4">
                            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                              isAbnormal ? 'bg-rose-100 text-rose-800 border border-rose-200' : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                            }`}>
                              {isAbnormal ? (
                                <AlertTriangle className="w-3 h-3 mr-1 text-rose-600" />
                              ) : (
                                <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
                              )}
                              {pred}
                            </span>
                          </td>
                          <td className="py-3.5 px-4 font-mono font-semibold text-slate-700">
                            {conf}%
                          </td>
                          <td className="py-3.5 px-4 text-slate-500 text-xs font-mono">
                            {s.scan_date ? new Date(s.scan_date).toLocaleString() : 'Recent'}
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
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    <th className="py-3.5 px-4">Log ID</th>
                    <th className="py-3.5 px-4">Timestamp</th>
                    <th className="py-3.5 px-4">User</th>
                    <th className="py-3.5 px-4">Security Action</th>
                    <th className="py-3.5 px-4">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredLogs.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="py-12 text-center text-slate-400">
                        No activity audit logs recorded yet.
                      </td>
                    </tr>
                  ) : (
                    filteredLogs.map((l, idx) => {
                      const isAuthFail = l.action === 'FAILED_LOGIN';
                      const isUpdate = l.action === 'CREDENTIAL_UPDATE';
                      return (
                        <tr key={l.log_id || idx} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3.5 px-4 font-mono text-xs text-slate-400">
                            #{l.log_id}
                          </td>
                          <td className="py-3.5 px-4 text-xs font-mono text-slate-500">
                            {l.timestamp ? new Date(l.timestamp).toLocaleString() : 'N/A'}
                          </td>
                          <td className="py-3.5 px-4 font-semibold text-slate-900">
                            {l.username || 'SYSTEM'}
                          </td>
                          <td className="py-3.5 px-4">
                            <span className={`px-2 py-0.5 rounded-md text-xs font-mono font-semibold ${
                              isAuthFail ? 'bg-rose-100 text-rose-800' :
                              isUpdate ? 'bg-amber-100 text-amber-800' :
                              'bg-slate-100 text-slate-800'
                            }`}>
                              {l.action}
                            </span>
                          </td>
                          <td className="py-3.5 px-4 text-slate-600 text-xs">
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
      </div>
    </div>
  );
}
