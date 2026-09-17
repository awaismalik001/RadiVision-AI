import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  FolderArchive, 
  Clock, 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight
} from 'lucide-react';

export default function PatientHistory({ currentUser, isMyHistory = false, onNavigateStudio }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedModality, setSelectedModality] = useState("ALL");
  const [downloadingId, setDownloadingId] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const isInstitutionalAdmin = currentUser?.role === 'Admin' && !isMyHistory;
      const url = isInstitutionalAdmin
        ? '/api/history'
        : `/api/history?user_id=${currentUser?.user_id || 2}`;
      const resp = await axios.get(url);
      setScans(resp.data.scans || []);
    } catch (err) {
      console.error("[PatientHistory] Failed to load scan records:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [currentUser, isMyHistory]);

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

  const handleDownloadPdf = async (scan) => {
    setDownloadingId(scan.scan_id);
    try {
      const payload = {
        patient_id: scan.patient_national_id || `RV-${scan.scan_id}`,
        patient_name: scan.patient_name || "Patient Record",
        patient_age: scan.patient_age || 35,
        patient_gender: scan.patient_gender || "Female",
        scan_type: scan.scan_type,
        prediction: scan.prediction,
        confidence: scan.confidence,
        body_region: scan.body_region,
        annotated_image_path: scan.annotated_image_path || scan.raw_image_path,
        date: scan.scan_date,
        location: "New York"
      };

      const resp = await axios.post('/api/export-pdf', payload, {
        responseType: 'blob'
      });

      const blob = new Blob([resp.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `RadiVision_Report_Scan_${scan.scan_id}.pdf`;
      link.click();
    } catch (err) {
      console.error("[PatientHistory] PDF download error:", err);
      alert("Failed to export PDF report. Please verify server connectivity.");
    } finally {
      setDownloadingId(null);
    }
  };

  // Filter scans
  const filteredScans = scans.filter((scan) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = isMyHistory
      ? (scan.prediction && scan.prediction.toLowerCase().includes(q)) ||
        (scan.scan_type && scan.scan_type.toLowerCase().includes(q))
      : (scan.patient_name && scan.patient_name.toLowerCase().includes(q)) ||
        (scan.patient_contact && scan.patient_contact.toLowerCase().includes(q)) ||
        (scan.prediction && scan.prediction.toLowerCase().includes(q));

    const matchesModality =
      selectedModality === "ALL" ||
      (scan.scan_type && scan.scan_type.toUpperCase() === selectedModality);

    // If "My Scan History", filter to current user if recorded; fallback to all personal scans in workstation
    return matchesSearch && matchesModality;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-4 md:p-5 space-y-4">
      {/* Top Header */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-200 pb-3">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded bg-blue-50 border border-blue-200 text-[#1982bf] text-[11px] font-semibold mb-1.5">
            {isMyHistory ? <Clock className="w-3 h-3" /> : <FolderArchive className="w-3 h-3" />}
            <span>{isMyHistory ? "User Scan Archive" : "PACS Institutional Records"}</span>
          </div>
          <h1 className="text-lg md:text-xl font-bold text-slate-900 tracking-tight">
            {isMyHistory ? "My Scan History" : "PACS Patient Records"}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isMyHistory 
              ? "Personal examinations, diagnostic impressions, and archived reports under your account." 
              : "Complete hospital repository of AI-screened radiographs, diagnostic findings, and audit logs."}
          </p>
        </div>

        <div className="flex items-center space-x-2 self-start md:self-auto">
          <button
            onClick={fetchHistory}
            className="px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-sm font-semibold text-slate-700 transition-colors flex items-center space-x-1.5 cursor-pointer shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#1982bf]' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={onNavigateStudio}
            className="px-3.5 py-1.5 rounded-lg bg-[#1982bf] hover:bg-[#156ea3] text-sm font-semibold text-white transition-colors flex items-center space-x-1.5 cursor-pointer shadow-sm"
          >
            <span>New Scan Ingestion</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-3">
        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
          <div className="relative w-full sm:w-80">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={isMyHistory ? "Search by Diagnosis or Modality..." : "Search by Patient, MRN, or Diagnosis..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-8 pr-3 py-1.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#1982bf] focus:bg-white transition-all"
            />
          </div>

          {/* Modality Filter Pills */}
          <div className="flex items-center space-x-1.5 w-full sm:w-auto">
            <Filter className="w-3.5 h-3.5 text-slate-400 mr-1 hidden sm:inline" />
            {["ALL", "CHEST", "BONE"].map((mod) => (
              <button
                key={mod}
                onClick={() => setSelectedModality(mod)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold tracking-wider transition-all cursor-pointer ${
                  selectedModality === mod
                    ? "bg-[#1982bf] text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {mod}
              </button>
            ))}
          </div>
        </div>

        {/* Scan Records Table / Cards */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold text-slate-600 uppercase tracking-wide">
                  {!isMyHistory && <th className="py-2.5 px-3">Patient / National ID</th>}
                  <th className="py-2.5 px-3">Modality</th>
                  <th className="py-2.5 px-3">ViT Diagnostic Finding</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3">Date & Timestamp</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredScans.length === 0 ? (
                  <tr>
                    <td colSpan={isMyHistory ? 5 : 6} className="py-10 text-center text-slate-400 text-xs">
                      {loading ? "Loading scan archive..." : "No scan records found matching your filters."}
                    </td>
                  </tr>
                ) : (
                  filteredScans.map((scan, idx) => {
                    const pred = scan.prediction || 'Normal';
                    const isAbnormal = pred.toLowerCase().includes('abnormal') || pred.toLowerCase().includes('pneumonia') || pred.toLowerCase().includes('fracture');
                    const conf = scan.confidence ? (scan.confidence * 100).toFixed(1) : '95.0';

                    return (
                      <tr key={scan.scan_id || idx} className="hover:bg-slate-50/80 transition-colors">
                        {!isMyHistory && (
                          <td className="py-2.5 px-3">
                            <div className="font-semibold text-slate-900 text-[13px]">{scan.patient_name || 'Anonymous Patient'}</div>
                            <div className="text-[10px] font-mono text-slate-500">
                              {scan.patient_contact || `RV-${(scan.scan_id || 100).toString().padStart(6, '0')}`}
                            </div>
                          </td>
                        )}

                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${
                            scan.scan_type === 'Chest' ? 'bg-blue-100 text-blue-800' : 'bg-teal-100 text-teal-800'
                          }`}>
                            {scan.scan_type}
                          </span>
                        </td>

                        <td className="py-2.5 px-3">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[12px] font-semibold ${
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

                        <td className="py-2.5 px-3 font-mono font-semibold text-[13px] text-slate-700">
                          {conf}%
                        </td>

                        <td className="py-2.5 px-3 text-slate-600 text-[12px] font-mono whitespace-nowrap">
                          <div className="flex items-center space-x-1.5">
                            <Clock className="w-3 h-3 text-slate-400 shrink-0" />
                            <span>{formatDateTime(scan.scan_date)}</span>
                          </div>
                        </td>

                        <td className="py-2.5 px-3 text-right">
                          <button
                            onClick={() => handleDownloadPdf(scan)}
                            disabled={downloadingId === scan.scan_id}
                            className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-[#1982bf] hover:bg-[#156ea3] text-white text-[13px] font-semibold shadow-sm transition-all cursor-pointer"
                          >
                            {downloadingId === scan.scan_id ? (
                              <RefreshCw className="w-3 h-3 animate-spin" />
                            ) : (
                              <Download className="w-3 h-3" />
                            )}
                            <span>PDF</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
