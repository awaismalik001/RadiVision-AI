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
  Lock,
  Cpu,
  ShieldCheck,
  Bot
} from 'lucide-react';

const getMediaUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('blob:')) return url;
  return `http://127.0.0.1:8000${url.startsWith('/') ? '' : '/'}${url}`;
};

export default function DiagnosticStudio({ currentUser }) {
  const isAdmin = currentUser?.role === 'Admin';
  // Modality & Demographics State
  const [modality, setModality] = useState("Bone"); // 'Bone' or 'Chest'
  const activeUserName = currentUser?.full_name || currentUser?.username || "Active User";
  const [patientAge, setPatientAge] = useState(34);
  const [patientGender, setPatientGender] = useState("Female");
  const [patientId, setPatientId] = useState(`RV-${Math.floor(100000 + Math.random() * 900000)}`);
  const [location, setLocation] = useState("New York");

  // File & Prediction State
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [viewMode, setViewMode] = useState("annotated"); // 'original' | 'annotated'
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const fileInputRef = useRef(null);

  // Quick Load Preset Samples from dataset
  const handleLoadSample = (sampleType) => {
    setModality(sampleType);
    if (sampleType === "Bone") {
      setPreviewUrl("/sample_bone.png");
      setPatientAge(34);
      setLocation("New York");
    } else {
      setPreviewUrl("/sample_chest.png");
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

  // Run AI Diagnostics (ViT + Gemini Pipeline)
  const handleAnalyze = async () => {
    if (!selectedFile && !previewUrl) return;

    setAnalyzing(true);
    try {
      const formData = new FormData();
      if (selectedFile instanceof File) {
        formData.append("file", selectedFile);
      } else {
        const sampleResp = await fetch(previewUrl);
        const blob = await sampleResp.blob();
        formData.append("file", blob, `${modality.toLowerCase()}_sample.png`);
      }

      formData.append("modality", modality);
      formData.append("patient_name", activeUserName);
      formData.append("patient_age", patientAge);
      formData.append("patient_gender", patientGender);
      formData.append("patient_id", patientId);
      formData.append("location", location);
      formData.append("user_id", currentUser?.user_id || 2);

      const resp = await axios.post('/api/predict', formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      setAnalysisResult(resp.data);
      setViewMode("annotated");
    } catch (err) {
      console.error("Analysis failed:", err);
      alert("Analysis error: Unable to connect to RadiVision AI backend.");
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
        patient_name: analysisResult.patient_name || activeUserName,
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

      const resp = await axios.post('/api/export-pdf', payload, {
        responseType: 'blob'
      });

      const blob = new Blob([resp.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `RadiVision_Report_${analysisResult.patient_id}.pdf`;
      link.click();
    } catch (err) {
      console.error("PDF Export error:", err);
      alert("Failed to export PDF report. Please verify server connectivity.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const isAbnormal = analysisResult && (
    !analysisResult.prediction.toLowerCase().includes("normal") &&
    !analysisResult.prediction.toLowerCase().includes("no fracture") &&
    !analysisResult.prediction.toLowerCase().includes("healthy") &&
    !analysisResult.prediction.toLowerCase().includes("clear") &&
    (
      analysisResult.prediction.toLowerCase().includes("fracture") ||
      analysisResult.prediction.toLowerCase().includes("pneumonia") ||
      analysisResult.prediction.toLowerCase().includes("abnormal")
    )
  );

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-4 md:p-5 space-y-4">
      {/* Top Banner & Modality Toggles */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-[11px] font-semibold mb-1">
            <Sparkles className="w-3 h-3 text-blue-600" />
            <span>Vision Transformer (ViT-B/16) • Gemini Multimodal Cross-Verification</span>
          </div>
          <h1 className="text-lg md:text-xl font-bold text-slate-900 tracking-tight">
            AI Diagnostic Studio
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Deep learning plain radiograph screening with instant Grad-CAM localization & ViT triage.
          </p>
        </div>

        {/* Modality Selector Tabs */}
        <div className="flex items-center bg-white p-1 rounded-xl border border-slate-300 shadow-sm self-start md:self-auto">
          <button
            onClick={() => { setModality("Chest"); setAnalysisResult(null); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all cursor-pointer flex items-center space-x-1.5 ${
              modality === "Chest"
                ? "bg-[#1982bf] text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>CHEST (Pneumonia)</span>
          </button>
          <button
            onClick={() => { setModality("Bone"); setAnalysisResult(null); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all cursor-pointer flex items-center space-x-1.5 ${
              modality === "Bone"
                ? "bg-[#1982bf] text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Crosshair className="w-3.5 h-3.5" />
            <span>BONE (Fractures)</span>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Upload & Demographics (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Drag & Drop File Upload Area */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                <UploadCloud className="w-3.5 h-3.5 text-blue-600" />
                <span>Radiographic Ingestion</span>
              </h2>
              {isAdmin && (
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => handleLoadSample("Bone")}
                    className="text-[10px] font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 px-2 py-0.5 rounded transition-colors cursor-pointer"
                  >
                    Load Bone Sample
                  </button>
                  <button
                    type="button"
                    onClick={() => handleLoadSample("Chest")}
                    className="text-[11px] font-semibold text-teal-600 hover:text-teal-800 bg-teal-50 px-2.5 py-1 rounded-md transition-colors cursor-pointer"
                  >
                    Load Chest Sample
                  </button>
                </div>
              )}
            </div>

            {/* Dropzone */}
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                previewUrl 
                  ? "border-blue-400 bg-blue-50/20" 
                  : "border-slate-300 hover:border-blue-500 hover:bg-slate-50"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />

              {previewUrl ? (
                <div className="space-y-3">
                  <div className="relative mx-auto max-h-56 max-w-full rounded-xl overflow-hidden shadow-sm border border-slate-200 bg-slate-950 inline-block">
                    <img
                      src={previewUrl}
                      alt="Uploaded Radiograph"
                      className="max-h-56 object-contain"
                    />
                    <div className="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-[#0B1727]/80 text-white text-[10px] font-mono">
                      {modality} Modality
                    </div>
                  </div>
                  <p className="text-xs text-slate-500">
                    Click or drop another image to replace.
                  </p>
                </div>
              ) : (
                <div className="py-8 space-y-3">
                  <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto shadow-sm">
                    <UploadCloud className="w-7 h-7" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-800">
                      Drag & drop medical X-ray scan here
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      Supports DICOM exports, PNG, JPG, and WEBP formats
                    </p>
                  </div>
                  <div className="inline-block px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
                    Browse Local File
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Scan & Clinical Details Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 space-y-3">
            <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                <span>Scan & Clinical Details</span>
              </span>
              <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded flex items-center space-x-1">
                <Lock className="w-2.5 h-2.5 inline" />
                <span>AES-256 Encrypted</span>
              </span>
            </h2>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Medical Record # (MRN)</label>
                <input
                  type="text"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-300 text-sm text-slate-900 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">GPS / City Location</label>
                <div className="relative">
                  <MapPin className="w-3 h-3 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. New York, Islamabad"
                    className="w-full pl-7 pr-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-300 text-sm text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="col-span-2">
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Age & Gender</label>
                <div className="grid grid-cols-2 gap-2.5">
                  <input
                    type="number"
                    value={patientAge}
                    onChange={(e) => setPatientAge(Number(e.target.value))}
                    placeholder="Age"
                    className="w-full px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-300 text-sm text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <select
                    value={patientGender}
                    onChange={(e) => setPatientGender(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-300 text-sm text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Ingestion Trigger Button */}
            <button
              onClick={handleAnalyze}
              disabled={analyzing || (!selectedFile && !previewUrl)}
              className={`w-full py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center space-x-2 shadow-sm transition-all cursor-pointer ${
                analyzing || (!selectedFile && !previewUrl)
                  ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-[#0B1727] hover:bg-slate-800 text-white shadow-blue-900/10"
              }`}
            >
              {analyzing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue-400" />
                  <span>Executing Vision Transformer & Gemini Verification...</span>
                </>
              ) : (
                <>
                  <Stethoscope className="w-4 h-4 text-cyan-400" />
                  <span>Execute Diagnostic Analysis</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Diagnostic Output & Viewport (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Diagnostic Viewport Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between min-h-[420px]">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
                  <Eye className="w-4 h-4 text-blue-600" />
                  <span>Radiological Viewport</span>
                </h2>
                <div className="text-xs text-slate-500">
                  {analysisResult ? "Grad-CAM lesion highlight & bounding boxes active" : "Awaiting scan ingestion"}
                </div>
              </div>

              {/* View Toggle */}
              {analysisResult && (
                <div className="flex items-center bg-slate-100 p-1 rounded-xl">
                  <button
                    onClick={() => setViewMode("annotated")}
                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                      viewMode === "annotated"
                        ? "bg-white text-slate-900 shadow-sm font-semibold"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Annotated
                  </button>
                  <button
                    onClick={() => setViewMode("original")}
                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                      viewMode === "original"
                        ? "bg-white text-slate-900 shadow-sm font-semibold"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Raw Scan
                  </button>
                </div>
              )}
            </div>

            {/* Viewport Center */}
            <div className="my-auto py-4 flex items-center justify-center">
              {analysisResult ? (
                <div className="relative rounded-2xl overflow-hidden border border-slate-200 shadow-md bg-slate-950 max-h-[380px]">
                  <img
                    src={getMediaUrl(viewMode === "annotated" ? analysisResult.annotated_url : analysisResult.image_url)}
                    alt="Scan Result"
                    className="max-h-[380px] object-contain mx-auto"
                  />
                  <div className="absolute bottom-3 left-3 px-3 py-1 rounded-lg bg-[#0B1727]/85 text-white text-xs font-mono backdrop-blur-md">
                    {analysisResult.scan_type} • {analysisResult.body_region || "Skeletal"}
                  </div>
                </div>
              ) : previewUrl ? (
                <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-sm bg-slate-950 max-h-[340px]">
                  <img
                    src={previewUrl}
                    alt="Pending Analysis"
                    className="max-h-[340px] object-contain opacity-85"
                  />
                </div>
              ) : (
                <div className="text-center py-16 text-slate-400">
                  <Layers className="w-12 h-12 mx-auto mb-2 text-slate-300 stroke-1" />
                  <p className="text-sm font-medium text-slate-500">No radiograph loaded in viewport</p>
                  <p className="text-xs text-slate-400 mt-0.5">Ingest a scan or load a preset sample to view results</p>
                </div>
              )}
            </div>

            {/* Viewport Footer with Export PDF */}
            {analysisResult && (
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                <div className="text-xs text-slate-500 font-mono">
                  Scan ID: #{analysisResult.scan_id} • Analyzed: {analysisResult.timestamp}
                </div>
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="px-4 py-2 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-xs flex items-center space-x-2 shadow-sm transition-all cursor-pointer"
                >
                  {downloadingPdf ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Download className="w-3.5 h-3.5" />
                  )}
                  <span>{downloadingPdf ? "Compiling PDF..." : "Export Clinical PDF Report"}</span>
                </button>
              </div>
            )}
          </div>

          {/* AI Clinical Diagnosis & Gemini Refinement Card */}
          {analysisResult && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4"
            >
              {/* Clinical Discrepancy & Escalation Alert Banner */}
              {analysisResult.gemini_refinement?.escalated && (
                <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-950 flex items-start space-x-3 text-xs">
                  <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-bold uppercase tracking-wide flex items-center space-x-2 text-amber-900">
                      <span>Clinical Safety Escalation Active</span>
                      <span className="px-2 py-0.5 rounded-full bg-amber-200 text-amber-900 text-[10px] font-mono">
                        Discordance Reconciled
                      </span>
                    </div>
                    <div className="text-amber-900/90 mt-1 leading-relaxed font-medium">
                      Primary screening model suggested normal, but Gemini Multimodal Clinical AI detected an acute fracture/pathology. Triage has been automatically escalated to High Priority for patient safety.
                    </div>
                  </div>
                </div>
              )}

              {/* Primary ViT Result Banner */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    isAbnormal ? "bg-rose-100 text-rose-600" : "bg-emerald-100 text-emerald-600"
                  }`}>
                    {isAbnormal ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      {analysisResult.gemini_refinement?.escalated ? "Clinical Consensus Diagnosis (Escalated)" : "Primary ViT Diagnosis"}
                    </div>
                    <div className={`text-lg font-bold ${
                      isAbnormal ? "text-rose-700" : "text-emerald-700"
                    }`}>
                      {analysisResult.prediction}
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Confidence</div>
                  <div className="text-xl font-extrabold text-slate-900 font-mono">
                    {(analysisResult.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Gemini Multi-Modal Cross-Verification Box */}
              {analysisResult.gemini_refinement && (
                <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-blue-900 font-semibold text-xs uppercase tracking-wider">
                      <Bot className="w-4 h-4 text-blue-700" />
                      <span>Gemini AI Multimodal Cross-Verification</span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-200 text-blue-900 font-bold">
                      {analysisResult.gemini_refinement.status || "Verified"}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 leading-relaxed font-medium">
                    "{analysisResult.gemini_refinement.clinical_impression}"
                  </p>

                  <div className="pt-2 border-t border-blue-200/60 flex items-center justify-between text-[11px] text-blue-900">
                    <div className="flex items-center space-x-1.5">
                      <span className="font-semibold">Consensus:</span>
                      <span className={`font-bold px-2 py-0.5 rounded-md text-[10px] ${
                        analysisResult.gemini_refinement.model_agreement?.includes("Discordance")
                          ? "bg-amber-100 text-amber-900 border border-amber-300"
                          : "bg-emerald-100 text-emerald-900 border border-emerald-300"
                      }`}>
                        {analysisResult.gemini_refinement.model_agreement}
                      </span>
                    </div>
                    <div>
                      <span className="font-semibold">Triage Urgency:</span>{' '}
                      <span className={`font-bold ${isAbnormal ? "text-rose-600" : "text-emerald-700"}`}>
                        {analysisResult.gemini_refinement.urgency}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
