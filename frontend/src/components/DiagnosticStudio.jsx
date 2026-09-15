import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { 
  UploadCloud, 
  FileText, 
  MapPin, 
  CheckCircle2, 
  AlertTriangle, 
  Phone, 
  Mail, 
  Download, 
  RefreshCw, 
  Sparkles, 
  Layers, 
  Eye, 
  Stethoscope, 
  Activity,
  Crosshair,
  Building2,
  UserCheck
} from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

export default function DiagnosticStudio() {
  // Modality & Demographics State
  const [modality, setModality] = useState("Bone"); // 'Bone' or 'Chest'
  const [patientName, setPatientName] = useState("Sarah Chen");
  const [patientAge, setPatientAge] = useState(34);
  const [patientGender, setPatientGender] = useState("Female");
  const [patientId, setPatientId] = useState(`RV-${Math.floor(100000 + Math.random() * 900000)}`);
  const [location, setLocation] = useState("New York");

  // File & Prediction State
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [viewMode, setViewMode] = useState("annotated"); // 'original' | 'annotated' | 'split'
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const fileInputRef = useRef(null);

  // Quick Load Preset Samples from dataset
  const handleLoadSample = (sampleType) => {
    setModality(sampleType);
    if (sampleType === "Bone") {
      setPreviewUrl("/sample_bone.png");
      setPatientName("Sarah Chen");
      setPatientAge(34);
      setLocation("New York");
    } else {
      setPreviewUrl("/sample_chest.png");
      setPatientName("Ahmad Khan");
      setPatientAge(47);
      setLocation("Islamabad");
    }
    setAnalysisResult(null);
    setSelectedFile("SAMPLE_PRESET");
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResult(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResult(null);
    }
  };

  // Run AI Diagnostics
  const handleAnalyze = async () => {
    if (!selectedFile && !previewUrl) return;

    setAnalyzing(true);
    try {
      const formData = new FormData();
      if (selectedFile instanceof File) {
        formData.append("file", selectedFile);
      } else {
        // If using sample preset, fetch blob first
        const sampleResp = await fetch(previewUrl);
        const blob = await sampleResp.blob();
        formData.append("file", blob, `${modality.toLowerCase()}_sample.png`);
      }

      formData.append("modality", modality);
      formData.append("patient_name", patientName);
      formData.append("patient_age", patientAge);
      formData.append("patient_gender", patientGender);
      formData.append("patient_id", patientId);
      formData.append("location", location);

      const resp = await axios.post(`${API_BASE}/api/predict`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      setAnalysisResult(resp.data);
      setViewMode("annotated");
    } catch (err) {
      console.error("Analysis failed:", err);
      alert("Analysis error: Unable to connect to RadiVision AI backend at " + API_BASE);
    } finally {
      setAnalyzing(false);
    }
  };

  // Export RSNA-Style Clinical PDF
  const handleDownloadPdf = async () => {
    if (!analysisResult) return;
    setDownloadingPdf(true);

    try {
      const payload = {
        patient_id: analysisResult.patient_id,
        patient_name: analysisResult.patient_name,
        patient_age: analysisResult.patient_age,
        patient_gender: analysisResult.patient_gender,
        scan_type: analysisResult.scan_type,
        prediction: analysisResult.prediction,
        confidence: analysisResult.confidence,
        body_region: analysisResult.body_region,
        annotated_image_path: analysisResult.local_annotated_path,
        facilities: analysisResult.facilities,
        location: analysisResult.location
      };

      const resp = await axios.post(`${API_BASE}/api/export-pdf`, payload, {
        responseType: 'blob'
      });

      // Trigger download
      const blob = new Blob([resp.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `RSNA_Report_${analysisResult.patient_id}.pdf`;
      link.click();
    } catch (err) {
      console.error("PDF Export error:", err);
      alert("Failed to export PDF report. Please verify backend server is active.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const isAbnormal = analysisResult && (
    analysisResult.prediction.toLowerCase().includes("fracture") ||
    analysisResult.prediction.toLowerCase().includes("pneumonia") ||
    analysisResult.prediction.toLowerCase().includes("abnormal")
  );

  return (
    <div className="flex-1 overflow-y-auto bg-[#070b14] text-slate-100 p-6 md:p-8 space-y-6">
      {/* Top Banner / Studio Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Radiographic Diagnostic Workstation</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
            Diagnostic Inference Studio
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Deep learning multi-modal screening for Chest (Pneumonia) & Bone (Fractures) with GPS referrals.
          </p>
        </div>

        {/* Modality Selector Tabs */}
        <div className="flex items-center bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 self-start md:self-auto">
          <button
            onClick={() => { setModality("Chest"); setAnalysisResult(null); }}
            className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all cursor-pointer flex items-center space-x-2 ${
              modality === "Chest"
                ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-600/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>CHEST (Pneumonia)</span>
          </button>
          <button
            onClick={() => { setModality("Bone"); setAnalysisResult(null); }}
            className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all cursor-pointer flex items-center space-x-2 ${
              modality === "Bone"
                ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-600/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Crosshair className="w-4 h-4" />
            <span>BONE (Fracture)</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Left Controls & Demographics, Right Radiograph & Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Demographics & Ingestion Controls (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Patient Demographics Card */}
          <div className="p-5 rounded-2xl bg-[#0e1626]/80 border border-slate-800/80 backdrop-blur-md shadow-xl">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 mb-4 flex items-center space-x-2 font-mono">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              <span>1. Patient Demographics & GPS Location</span>
            </h3>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="col-span-2">
                <label className="text-slate-400 font-medium block mb-1">Patient Full Name</label>
                <input
                  type="text"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-700/80 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              <div>
                <label className="text-slate-400 font-medium block mb-1">Age</label>
                <input
                  type="number"
                  value={patientAge}
                  onChange={(e) => setPatientAge(parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900/90 border border-slate-700/80 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              <div>
                <label className="text-slate-400 font-medium block mb-1">Gender</label>
                <select
                  value={patientGender}
                  onChange={(e) => setPatientGender(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-700/80 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
                >
                  <option value="Female">Female</option>
                  <option value="Male">Male</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="col-span-2">
                <label className="text-slate-400 font-medium block mb-1 flex items-center justify-between">
                  <span>Current Patient Location (for Referrals)</span>
                  <span className="text-[10px] text-cyan-400 font-mono">GPS Anchored</span>
                </label>
                <div className="relative">
                  <MapPin className="w-4 h-4 text-cyan-400 absolute left-3 top-2.5" />
                  <select
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full bg-slate-900/90 border border-slate-700/80 rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
                  >
                    <option value="New York">New York, USA (Lenox Hill / NYU Langone)</option>
                    <option value="Islamabad">Islamabad, Pakistan (Shifa / Maroof Int)</option>
                    <option value="Karachi">Karachi, Pakistan (Aga Khan University)</option>
                    <option value="Lahore">Lahore, Pakistan (Shaukat Khanum)</option>
                    <option value="London">London, UK (St Thomas' Hospital)</option>
                  </select>
                </div>
              </div>

              <div className="col-span-2 pt-1 flex justify-between items-center text-[11px] text-slate-400 font-mono">
                <span>Assigned PACS ID: <strong className="text-cyan-300">{patientId}</strong></span>
                <button
                  type="button"
                  onClick={() => setPatientId(`RV-${Math.floor(100000 + Math.random() * 900000)}`)}
                  className="text-cyan-400 hover:underline cursor-pointer"
                >
                  Generate New
                </button>
              </div>
            </div>
          </div>

          {/* Radiograph Ingestion Dropzone */}
          <div className="p-5 rounded-2xl bg-[#0e1626]/80 border border-slate-800/80 backdrop-blur-md shadow-xl space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center space-x-2 font-mono">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              <span>2. Radiograph Ingestion</span>
            </h3>

            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-700/80 hover:border-cyan-500/70 bg-slate-900/40 rounded-xl p-6 text-center cursor-pointer transition-all hover:bg-slate-900/70 group"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
              <UploadCloud className="w-10 h-10 text-slate-400 group-hover:text-cyan-400 mx-auto mb-3 transition-colors" />
              <div className="text-sm font-medium text-slate-200">
                Drop DICOM or Radiograph Image Here
              </div>
              <div className="text-xs text-slate-400 mt-1 font-mono">
                Supports High-Res PNG, JPG, JPEG (Grayscale/RGB)
              </div>
            </div>

            {/* Instant Demo Presets */}
            <div className="pt-2">
              <div className="text-xs font-mono text-slate-400 mb-2">QUICK TEST PRESETS:</div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => handleLoadSample("Chest")}
                  className="px-3 py-2 rounded-lg bg-slate-800/70 hover:bg-cyan-950/60 border border-slate-700 hover:border-cyan-500/50 text-xs font-medium text-slate-300 hover:text-cyan-300 transition-all text-left cursor-pointer"
                >
                  🫁 Load Sample Chest X-Ray
                </button>
                <button
                  onClick={() => handleLoadSample("Bone")}
                  className="px-3 py-2 rounded-lg bg-slate-800/70 hover:bg-cyan-950/60 border border-slate-700 hover:border-cyan-500/50 text-xs font-medium text-slate-300 hover:text-cyan-300 transition-all text-left cursor-pointer"
                >
                  🦴 Load Sample Bone X-Ray
                </button>
              </div>
            </div>

            {/* Analyze Action Button */}
            <div className="pt-2">
              <button
                onClick={handleAnalyze}
                disabled={(!selectedFile && !previewUrl) || analyzing}
                className={`w-full py-3.5 rounded-xl font-bold text-sm tracking-wide flex items-center justify-center space-x-2 transition-all cursor-pointer ${
                  (!selectedFile && !previewUrl) || analyzing
                    ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                    : "bg-gradient-to-r from-cyan-600 via-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 border border-cyan-400/40"
                }`}
              >
                {analyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>RUNNING PYTORCH INFERENCE...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>ANALYZE RADIOGRAPH</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Radiograph Inspection & Clinical Results (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Radiograph Canvas Viewer */}
          <div className="p-5 rounded-2xl bg-[#0e1626]/80 border border-slate-800/80 backdrop-blur-md shadow-xl flex flex-col justify-between min-h-[460px]">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800/70 pb-3">
              <div className="flex items-center space-x-2">
                <Eye className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-mono font-bold tracking-wider text-slate-200 uppercase">
                  RADIOGRAPH INSPECTION CANVAS
                </span>
              </div>

              {/* View Switcher if analyzed */}
              {analysisResult && (
                <div className="flex items-center bg-slate-900/90 rounded-lg p-1 border border-slate-800 text-xs">
                  <button
                    onClick={() => setViewMode("annotated")}
                    className={`px-3 py-1 rounded font-medium transition-colors cursor-pointer ${
                      viewMode === "annotated" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Grad-CAM Overlay
                  </button>
                  <button
                    onClick={() => setViewMode("original")}
                    className={`px-3 py-1 rounded font-medium transition-colors cursor-pointer ${
                      viewMode === "original" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Raw Radiograph
                  </button>
                </div>
              )}
            </div>

            {/* Canvas Body */}
            <div className="relative flex-1 flex items-center justify-center bg-[#070b14] rounded-xl overflow-hidden border border-slate-800/80 min-h-[360px]">
              {previewUrl ? (
                <div className="relative max-h-[420px] w-full flex items-center justify-center p-2">
                  <img
                    src={
                      viewMode === "annotated" && analysisResult?.annotated_url
                        ? `${API_BASE}${analysisResult.annotated_url}`
                        : previewUrl
                    }
                    alt="Patient Radiograph"
                    className="max-h-[380px] max-w-full object-contain rounded-lg shadow-2xl filter contrast-110"
                  />
                  
                  {/* Holographic Crosshair Overlay */}
                  <div className="absolute inset-0 pointer-events-none border border-cyan-500/10" />
                </div>
              ) : (
                <div className="text-center p-8 text-slate-500">
                  <Layers className="w-12 h-12 mx-auto mb-3 opacity-30 text-cyan-400" />
                  <p className="text-sm font-medium">No Radiograph Loaded</p>
                  <p className="text-xs text-slate-600 mt-1 font-mono">Upload an X-ray or click a preset to initiate screening</p>
                </div>
              )}
            </div>
          </div>

          {/* Diagnostic Results Card (Displays when inference finishes) */}
          {analysisResult && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-5 rounded-2xl bg-[#0e1626]/80 border border-slate-800/80 backdrop-blur-md shadow-xl space-y-4"
            >
              {/* Abnormality Header Pill */}
              <div className={`p-4 rounded-xl border flex items-center justify-between ${
                isAbnormal
                  ? "bg-rose-950/40 border-rose-600/40 text-rose-200"
                  : "bg-emerald-950/40 border-emerald-600/40 text-emerald-200"
              }`}>
                <div className="flex items-center space-x-3">
                  {isAbnormal ? (
                    <AlertTriangle className="w-6 h-6 text-rose-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
                  )}
                  <div>
                    <div className="text-xs font-mono tracking-widest uppercase opacity-80">
                      DIAGNOSTIC IMPRESSION
                    </div>
                    <div className="text-lg font-extrabold tracking-wide">
                      {analysisResult.prediction.toUpperCase()}
                    </div>
                  </div>
                </div>

                <div className="text-right font-mono">
                  <div className="text-[10px] uppercase opacity-75">CALIBRATED CONFIDENCE</div>
                  <div className="text-xl font-bold">
                    {(analysisResult.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Local Healthcare & Specialist Referrals Box */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-500/20 text-xs space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center space-x-2 text-cyan-300 font-semibold font-mono">
                    <Building2 className="w-4 h-4 text-cyan-400" />
                    <span>LOCAL HEALTHCARE & SPECIALIST REFERRALS ({location.toUpperCase()})</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">GPS Verified</span>
                </div>

                {analysisResult.facilities && analysisResult.facilities.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {analysisResult.facilities.slice(0, 2).map((fac, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 space-y-1.5">
                        <div className="font-bold text-slate-100 flex items-center space-x-1.5">
                          <Building2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                          <span className="truncate">{fac.hospital_name || fac.name}</span>
                        </div>
                        <div className="text-slate-300 flex items-center space-x-1.5">
                          <UserCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                          <span className="font-medium text-emerald-300">{fac.doctor_name || fac.specialist}</span>
                        </div>
                        <div className="text-slate-400 flex items-center space-x-1.5 font-mono text-[11px]">
                          <Phone className="w-3 h-3 text-cyan-400 shrink-0" />
                          <span>{fac.phone || "+1 212-434-2000"}</span>
                        </div>
                        {fac.email && (
                          <div className="text-slate-400 flex items-center space-x-1.5 font-mono text-[11px] truncate">
                            <Mail className="w-3 h-3 text-slate-400 shrink-0" />
                            <span className="truncate">{fac.email}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-slate-400 italic">No specialist referrals required for normal scan.</div>
                )}
              </div>

              {/* Action Toolbar: Download RSNA PDF Report */}
              <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="w-full sm:w-auto flex-1 py-3 px-5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold text-xs tracking-wider flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/20 transition-all cursor-pointer border border-blue-400/30"
                >
                  {downloadingPdf ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>COMPILING RSNA REPORT...</span>
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      <span>DOWNLOAD RSNA CLINICAL PDF REPORT</span>
                    </>
                  )}
                </button>

                <button
                  onClick={() => {
                    setAnalysisResult(null);
                    setSelectedFile(null);
                    setPreviewUrl(null);
                  }}
                  className="w-full sm:w-auto py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-medium text-xs tracking-wider border border-slate-700 transition-colors cursor-pointer"
                >
                  NEW SCAN
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
