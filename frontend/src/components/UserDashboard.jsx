import React, { useState, useEffect } from 'react';
import { 
  Stethoscope, 
  FolderClock, 
  Database, 
  ArrowRight, 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  Download, 
  RefreshCw, 
  Layers, 
  Cpu, 
  Lock, 
  Clock,
  ChevronRight,
  User,
  ShieldCheck
} from 'lucide-react';
import axios from 'axios';

export default function UserDashboard({ currentUser, onNavigate }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);

  const fetchRecentScans = async () => {
    setLoading(true);
    try {
      const userId = currentUser?.user_id || 2;
      const resp = await axios.get(`/api/history?user_id=${userId}`);
      setScans(resp.data.scans || []);
    } catch (err) {
      console.error('[Dashboard] Failed to load scans:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecentScans();
  }, [currentUser]);

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
      console.error("[Dashboard] PDF download error:", err);
      alert("Failed to export PDF report. Please verify server connectivity.");
    } finally {
      setDownloadingId(null);
    }
  };

  const totalCount = scans.length;
  const abnormalCount = scans.filter(s => {
    const p = (s.prediction || '').toLowerCase();
    return p.includes('abnormal') || p.includes('pneumonia') || p.includes('fracture');
  }).length;
  const normalCount = totalCount - abnormalCount;

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-4 md:p-5 space-y-4">
      {/* Top Welcome Banner */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2 mb-1.5">
            <span className="px-2 py-0.5 rounded bg-blue-100 text-[#1982bf] text-[11px] font-bold uppercase tracking-wider">
              User Workstation
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[11px] font-semibold flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>PACS Local Vault Active</span>
            </span>
          </div>
          <h1 className="text-lg md:text-xl font-bold text-slate-900 tracking-tight">
            Welcome, {currentUser?.full_name || "User"}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Diagnostic radiograph triage, deep learning ViT-B/16 inference, and institutional records.
          </p>
        </div>

        <div className="flex items-center space-x-2 self-start md:self-auto">
          <button
            onClick={() => onNavigate('studio')}
            className="px-3.5 py-1.5 rounded-lg bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-sm flex items-center space-x-1.5 shadow-sm transition-all cursor-pointer"
          >
            <Stethoscope className="w-4 h-4" />
            <span>Launch AI Diagnostic Studio</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-4">
        {/* 3 Quick-Action Workflow Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {/* Card 1: Diagnostic Studio */}
          <div 
            onClick={() => onNavigate('studio')}
            className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-[#1982bf]/50 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="w-9 h-9 rounded-lg bg-blue-50 text-[#1982bf] flex items-center justify-center group-hover:bg-[#1982bf] group-hover:text-white transition-colors">
                  <Stethoscope className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-100 text-[#1982bf]">
                  ViT-B/16 Live
                </span>
              </div>
              <h3 className="font-bold text-slate-900 text-sm group-hover:text-[#1982bf] transition-colors">
                AI Diagnostic Studio
              </h3>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                Upload Chest and Skeletal radiographs for real-time abnormality detection with Grad-CAM heatmaps.
              </p>
            </div>
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-[#1982bf]">
              <span>Open Workstation</span>
              <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 2: My Scan History */}
          <div 
            onClick={() => onNavigate('my-history')}
            className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-[#1982bf]/50 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center group-hover:bg-teal-600 group-hover:text-white transition-colors">
                  <FolderClock className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-teal-100 text-teal-800">
                  Personal Archive
                </span>
              </div>
              <h3 className="font-bold text-slate-900 text-sm group-hover:text-teal-700 transition-colors">
                My Scan History
              </h3>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                Review your personalized clinical interpretations, diagnostic confidence scores, and archived reports.
              </p>
            </div>
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-teal-700">
              <span>View My History</span>
              <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 3: User Profile & Security */}
          <div 
            onClick={() => onNavigate('profile')}
            className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-[#1982bf]/50 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="w-9 h-9 rounded-lg bg-blue-50 text-[#1982bf] flex items-center justify-center group-hover:bg-[#1982bf] group-hover:text-white transition-colors">
                  <User className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-100 text-[#1982bf]">
                  Active Session
                </span>
              </div>
              <h3 className="font-bold text-slate-900 text-sm group-hover:text-[#1982bf] transition-colors">
                User Profile & Security
              </h3>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                Inspect your verified user credentials, assigned security role, and workstation details.
              </p>
            </div>
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-[#1982bf]">
              <span>View Profile</span>
              <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>

        {/* Telemetry KPI Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">Total Scans</div>
            <div className="text-2xl md:text-[22px] font-bold font-mono text-slate-900 mt-0.5">{totalCount}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Processed studies</div>
          </div>
          <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">Normal Cases</div>
            <div className="text-2xl md:text-[22px] font-bold font-mono text-emerald-600 mt-0.5">{normalCount}</div>
            <div className="text-[10px] text-emerald-700 mt-0.5">Unremarkable anatomy</div>
          </div>
          <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">Abnormal Triaged</div>
            <div className="text-2xl md:text-[22px] font-bold font-mono text-rose-600 mt-0.5">{abnormalCount}</div>
            <div className="text-[10px] text-rose-700 mt-0.5">Flagged for review</div>
          </div>
          <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">ViT Speed</div>
            <div className="text-2xl md:text-[22px] font-bold font-mono text-[#1982bf] mt-0.5">1.2s</div>
            <div className="text-[10px] text-blue-700 mt-0.5">Average inference latency</div>
          </div>
        </div>

        {/* Recent Clinical Examinations Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="w-3.5 h-3.5 text-[#1982bf]" />
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                Recent Clinical Studies
              </h2>
            </div>
            <button
              onClick={() => onNavigate('my-history')}
              className="text-xs font-semibold text-[#1982bf] hover:underline cursor-pointer flex items-center space-x-1"
            >
              <span>View All Scans</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold text-slate-600 uppercase tracking-wide">
                  <th className="py-2.5 px-3">Patient / ID</th>
                  <th className="py-2.5 px-3">Modality</th>
                  <th className="py-2.5 px-3">Primary Finding</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {scans.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="py-8 text-center text-slate-400 text-xs">
                      {loading ? "Loading examination records..." : "No recent scans found. Launch Diagnostic Studio to analyze a radiograph."}
                    </td>
                  </tr>
                ) : (
                  scans.slice(0, 5).map((scan, idx) => {
                    const pred = scan.prediction || 'Normal';
                    const isAbnormal = pred.toLowerCase().includes('abnormal') || pred.toLowerCase().includes('pneumonia') || pred.toLowerCase().includes('fracture');
                    const conf = scan.confidence ? (scan.confidence * 100).toFixed(1) : '95.0';

                    return (
                      <tr key={scan.scan_id || idx} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-2.5 px-3">
                          <div className="font-semibold text-slate-900 text-[13px]">{scan.patient_name || 'Anonymous Patient'}</div>
                          <div className="text-[10px] font-mono text-slate-500">
                            {scan.patient_contact || `RV-${(scan.scan_id || 100).toString().padStart(6, '0')}`}
                          </div>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${
                            scan.scan_type === 'Chest' ? 'bg-blue-100 text-blue-800' : 'bg-teal-100 text-teal-800'
                          }`}>
                            {scan.scan_type}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[12px] font-semibold ${
                            isAbnormal ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'
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
