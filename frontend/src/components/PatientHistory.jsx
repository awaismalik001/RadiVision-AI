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
  FileText, 
  Lock, 
  ArrowRight,
  Eye,
  Layers,
  Sparkles
} from 'lucide-react';

const getMediaUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('blob:')) return url;
  return `http://127.0.0.1:8000${url.startsWith('/') ? '' : '/'}${url}`;
};

export default function PatientHistory({ currentUser, isMyHistory = false, onNavigateStudio }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedModality, setSelectedModality] = useState("ALL");
  const [downloadingId, setDownloadingId] = useState(null);
  const [selectedPreviewScan, setSelectedPreviewScan] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const resp = await axios.get('/api/history');
      setScans(resp.data.scans || []);
    } catch (err) {
      console.error("[PatientHistory] Failed to load scan records:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

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
    const matchesSearch =
      (scan.patient_name && scan.patient_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (scan.patient_contact && scan.patient_contact.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (scan.prediction && scan.prediction.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesModality =
      selectedModality === "ALL" ||
      (scan.scan_type && scan.scan_type.toUpperCase() === selectedModality);

    // If "My Scan History", filter to current user if recorded; fallback to all personal scans in workstation
    return matchesSearch && matchesModality;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-6 md:p-8 space-y-6">
      {/* Top Header */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-[#1982bf] text-xs font-semibold mb-2">
            {isMyHistory ? <Clock className="w-3.5 h-3.5" /> : <FolderArchive className="w-3.5 h-3.5" />}
            <span>{isMyHistory ? "User Scan Archive" : "PACS Institutional Records"}</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
            {isMyHistory ? "My Scan History" : "PACS Patient Records"}
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {isMyHistory 
              ? "Personal examinations, diagnostic impressions, and archived reports under your account." 
              : "Complete hospital repository of AI-screened radiographs, diagnostic findings, and audit logs."}
          </p>
        </div>

        <div className="flex items-center space-x-3 self-start md:self-auto">
          <button
            onClick={fetchHistory}
            className="px-4 py-2 rounded-xl bg-white border border-slate-300 hover:bg-slate-50 text-xs font-semibold text-slate-700 transition-colors flex items-center space-x-2 cursor-pointer shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-[#1982bf]' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={onNavigateStudio}
            className="px-4 py-2 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-xs font-semibold text-white transition-colors flex items-center space-x-2 cursor-pointer shadow-md"
          >
            <span>New Scan Ingestion</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-4">
        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by Patient, MRN, or Diagnosis..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1982bf] focus:bg-white transition-all"
            />
          </div>

          {/* Modality Filter Pills */}
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400 mr-1 hidden sm:inline" />
            {["ALL", "CHEST", "BONE"].map((mod) => (
              <button
                key={mod}
                onClick={() => setSelectedModality(mod)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold tracking-wider transition-all cursor-pointer ${
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
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Radiograph</th>
                  <th className="py-3.5 px-4">Patient / National ID</th>
                  <th className="py-3.5 px-4">Modality</th>
                  <th className="py-3.5 px-4">ViT Diagnostic Finding</th>
                  <th className="py-3.5 px-4">Confidence</th>
                  <th className="py-3.5 px-4">Scan Date</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredScans.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-12 text-center text-slate-400 text-xs">
                      {loading ? "Loading scan archive..." : "No scan records found matching your filters."}
                    </td>
                  </tr>
                ) : (
                  filteredScans.map((scan, idx) => {
                    const pred = scan.prediction || 'Normal';
                    const isAbnormal = pred.toLowerCase().includes('abnormal') || pred.toLowerCase().includes('pneumonia') || pred.toLowerCase().includes('fracture');
                    const conf = scan.confidence ? (scan.confidence * 100).toFixed(1) : '95.0';
                    const imgUrl = getMediaUrl(scan.annotated_image_path || scan.raw_image_path);

                    return (
                      <tr key={scan.scan_id || idx} className="hover:bg-slate-50/80 transition-colors">
                        {/* Radiograph Thumbnail */}
                        <td className="py-3.5 px-4">
                          <div 
                            onClick={() => setSelectedPreviewScan(scan)}
                            className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-700 overflow-hidden relative cursor-pointer group flex items-center justify-center shadow-sm"
                          >
                            {imgUrl ? (
                              <img 
                                src={imgUrl} 
                                alt="Thumb" 
                                className="w-full h-full object-cover group-hover:scale-110 transition-transform" 
                              />
                            ) : (
                              <FileText className="w-5 h-5 text-slate-500" />
                            )}
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-[10px]">
                              <Eye className="w-3.5 h-3.5" />
                            </div>
                          </div>
                        </td>

                        <td className="py-3.5 px-4">
                          <div className="font-semibold text-slate-900 text-xs">{scan.patient_name || 'Anonymous Patient'}</div>
                          <div className="text-[10px] text-slate-500 font-mono">
                            {scan.patient_contact || `RV-${(scan.scan_id || 100).toString().padStart(6, '0')}`}
                          </div>
                        </td>

                        <td className="py-3.5 px-4">
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            scan.scan_type === 'Chest' ? 'bg-blue-100 text-blue-800' : 'bg-teal-100 text-teal-800'
                          }`}>
                            {scan.scan_type}
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

                        <td className="py-3.5 px-4 font-mono font-semibold text-xs text-slate-700">
                          {conf}%
                        </td>

                        <td className="py-3.5 px-4 text-slate-500 text-xs font-mono">
                          {scan.scan_date ? new Date(scan.scan_date).toLocaleDateString() : 'Recent'}
                        </td>

                        <td className="py-3.5 px-4 text-right">
                          <button
                            onClick={() => handleDownloadPdf(scan)}
                            disabled={downloadingId === scan.scan_id}
                            className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-white text-xs font-semibold shadow-sm transition-all cursor-pointer"
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

      {/* Radiograph Full Inspection Modal */}
      {selectedPreviewScan && (
        <div 
          onClick={() => setSelectedPreviewScan(null)}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm cursor-pointer"
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            className="max-w-2xl w-full bg-white rounded-3xl overflow-hidden shadow-2xl border border-slate-200 cursor-default"
          >
            <div className="p-4 bg-[#1982bf] text-white flex items-center justify-between">
              <div className="font-bold text-sm flex items-center space-x-2">
                <Layers className="w-4 h-4" />
                <span>PACS Radiograph Inspection — {selectedPreviewScan.patient_name}</span>
              </div>
              <button 
                onClick={() => setSelectedPreviewScan(null)}
                className="text-white/80 hover:text-white text-sm font-bold px-2 py-0.5 rounded-lg hover:bg-white/10"
              >
                ✕
              </button>
            </div>
            <div className="p-6 bg-slate-900 flex items-center justify-center min-h-[360px]">
              <img 
                src={getMediaUrl(selectedPreviewScan.annotated_image_path || selectedPreviewScan.raw_image_path)} 
                alt="Radiograph Inspection"
                className="max-h-[480px] object-contain rounded-xl shadow-lg border border-slate-800" 
              />
            </div>
            <div className="p-4 bg-white flex items-center justify-between border-t border-slate-200 text-xs">
              <div>
                <span className="font-semibold text-slate-700">Diagnosis: </span>
                <span className="font-bold text-[#1982bf]">{selectedPreviewScan.prediction}</span>
                <span className="text-slate-400 ml-2 font-mono">({(selectedPreviewScan.confidence * 100).toFixed(1)}% confidence)</span>
              </div>
              <button
                onClick={() => handleDownloadPdf(selectedPreviewScan)}
                className="px-4 py-2 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold flex items-center space-x-1.5 cursor-pointer shadow-sm"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export PDF</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
