import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  FolderClock, 
  Search, 
  Filter, 
  Download, 
  ExternalLink, 
  RefreshCw, 
  Calendar, 
  CheckCircle2, 
  AlertTriangle,
  FileText,
  Eye,
  ArrowRight
} from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

export default function PatientHistory({ onNavigateStudio }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedModality, setSelectedModality] = useState("ALL");
  const [downloadingId, setDownloadingId] = useState(null);
  const [previewScan, setPreviewScan] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const resp = await axios.get(`${API_BASE}/api/history`);
      setScans(resp.data.scans || []);
    } catch (err) {
      console.error("Failed to load patient history:", err);
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

      const resp = await axios.post(`${API_BASE}/api/export-pdf`, payload, {
        responseType: 'blob'
      });

      const blob = new Blob([resp.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `RSNA_Report_${payload.patient_id}.pdf`;
      link.click();
    } catch (err) {
      console.error("Error downloading report:", err);
      alert("Failed to export PDF report.");
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredScans = scans.filter((scan) => {
    const matchesSearch = 
      (scan.patient_name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (scan.prediction || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      String(scan.scan_id).includes(searchQuery);

    const matchesModality = 
      selectedModality === "ALL" ||
      (scan.scan_type && scan.scan_type.toUpperCase() === selectedModality);

    return matchesSearch && matchesModality;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-[#070b14] text-slate-100 p-6 md:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-950/60 border border-blue-500/30 text-blue-300 text-xs font-mono mb-2">
            <FolderClock className="w-3.5 h-3.5" />
            <span>PACS Archive & Audit Records</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
            Patient Scan History
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Historical repository of AI-screened radiographs, diagnostic impressions, and archived reports.
          </p>
        </div>

        <button
          onClick={fetchHistory}
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/50 text-xs font-mono text-slate-300 hover:text-cyan-300 transition-colors flex items-center space-x-2 self-start md:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>REFRESH ARCHIVE</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-[#0e1626]/80 p-4 rounded-xl border border-slate-800/80">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by Patient, ID, or Finding..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-700/70 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* Modality Filter Pills */}
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          {["ALL", "CHEST", "BONE"].map((m) => (
            <button
              key={m}
              onClick={() => setSelectedModality(m)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors cursor-pointer ${
                selectedModality === m
                  ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/30"
                  : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
              }`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Scans Table */}
      <div className="bg-[#0e1626]/80 border border-slate-800/80 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-16 text-center text-slate-400 space-y-3">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-cyan-400" />
            <p className="text-sm font-mono">Querying PACS Database...</p>
          </div>
        ) : filteredScans.length === 0 ? (
          <div className="p-16 text-center text-slate-500 space-y-4">
            <FolderClock className="w-12 h-12 mx-auto text-slate-600" />
            <div>
              <p className="text-base font-semibold text-slate-300">No Patient Records Found</p>
              <p className="text-xs text-slate-500 mt-1">
                {searchQuery ? "Try refining your search filters." : "Run your first diagnostic scan in the AI Studio."}
              </p>
            </div>
            {onNavigateStudio && (
              <button
                onClick={onNavigateStudio}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-xs font-semibold inline-flex items-center space-x-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
              >
                <span>OPEN AI DIAGNOSTIC STUDIO</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800/80 bg-slate-900/60 text-slate-400 font-mono uppercase text-[11px]">
                  <th className="p-4">Scan Date</th>
                  <th className="p-4">Patient Name & ID</th>
                  <th className="p-4">Modality</th>
                  <th className="p-4">Diagnostic Impression</th>
                  <th className="p-4">Confidence</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {filteredScans.map((scan) => {
                  const isAbn = 
                    (scan.prediction || "").toLowerCase().includes("fracture") ||
                    (scan.prediction || "").toLowerCase().includes("pneumonia") ||
                    (scan.prediction || "").toLowerCase().includes("abnormal");

                  return (
                    <tr key={scan.scan_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="p-4 text-slate-300 font-mono whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-3.5 h-3.5 text-slate-500" />
                          <span>{scan.scan_date ? scan.scan_date.split(" ")[0] : "Recent"}</span>
                        </div>
                      </td>

                      <td className="p-4">
                        <div className="font-semibold text-slate-100">{scan.patient_name || "Anonymous"}</div>
                        <div className="text-[11px] text-slate-400 font-mono">
                          {scan.patient_age} yrs • {scan.patient_gender} • ID: {scan.patient_national_id || `#${scan.scan_id}`}
                        </div>
                      </td>

                      <td className="p-4">
                        <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 font-mono text-[11px] text-cyan-300">
                          {scan.scan_type}
                        </span>
                      </td>

                      <td className="p-4">
                        <div className="inline-flex items-center space-x-1.5">
                          {isAbn ? (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full bg-rose-950/60 border border-rose-500/40 text-rose-300 font-semibold text-[11px]">
                              <AlertTriangle className="w-3 h-3 text-rose-400" />
                              <span>{scan.prediction}</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 font-semibold text-[11px]">
                              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                              <span>{scan.prediction}</span>
                            </span>
                          )}
                        </div>
                      </td>

                      <td className="p-4 font-mono font-bold text-slate-200">
                        {((scan.confidence || 0.95) * 100).toFixed(1)}%
                      </td>

                      <td className="p-4 text-right whitespace-nowrap">
                        <div className="inline-flex items-center space-x-2">
                          <button
                            onClick={() => handleDownloadPdf(scan)}
                            disabled={downloadingId === scan.scan_id}
                            className="px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 border border-blue-500/30 font-medium transition-colors flex items-center space-x-1.5 cursor-pointer"
                            title="Download RSNA PDF Report"
                          >
                            <Download className="w-3 h-3" />
                            <span>{downloadingId === scan.scan_id ? "Generating..." : "PDF Report"}</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
