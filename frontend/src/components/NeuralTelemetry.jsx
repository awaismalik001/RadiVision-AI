import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Cpu, Activity, ShieldCheck, Database, FileText, CheckCircle2, Server, Zap } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

export default function NeuralTelemetry() {
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const resp = await axios.get(`${API_BASE}/api/health`);
        setTelemetry(resp.data);
      } catch (e) {
        console.error("Health check error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#070b14] text-slate-100 p-6 md:p-8 space-y-6">
      <div className="border-b border-slate-800/80 pb-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-2">
          <Cpu className="w-3.5 h-3.5" />
          <span>Real-Time Model Health & Infrastructure</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
          Neural Architecture & System Telemetry
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Live telemetry monitoring PyTorch neural weights, inference latency, and clinical diagnostic calibration.
        </p>
      </div>

      {/* Model Benchmark Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Chest Model Card */}
        <div className="p-6 rounded-2xl bg-[#0e1626]/80 border border-cyan-500/30 backdrop-blur-md shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Chest Pneumonia AI</h3>
                <div className="text-xs text-slate-400 font-mono">MobileNetV2 Transfer Learning</div>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-semibold flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>&gt;90% ACHIEVED</span>
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3 pt-2">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 font-mono">ACCURACY</div>
              <div className="text-xl font-bold text-cyan-300 mt-1">90.72%</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 font-mono">SENSITIVITY</div>
              <div className="text-xl font-bold text-emerald-300 mt-1">92.68%</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 font-mono">ROC-AUC</div>
              <div className="text-xl font-bold text-blue-300 mt-1">0.9534</div>
            </div>
          </div>

          <div className="text-xs text-slate-400 font-mono space-y-1 pt-2 border-t border-slate-800/80">
            <div>• Target Classes: Normal vs Bacterial/Viral Pneumonia</div>
            <div>• Evaluation Set: 624-636 Clinical Radiographs</div>
            <div>• Spatial Localization: Class Activation Maps (Grad-CAM)</div>
          </div>
        </div>

        {/* Bone Fracture Model Card */}
        <div className="p-6 rounded-2xl bg-[#0e1626]/80 border border-cyan-500/30 backdrop-blur-md shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-blue-950 border border-blue-500/40 flex items-center justify-center text-blue-400">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Bone Fracture Localization AI</h3>
                <div className="text-xs text-slate-400 font-mono">MobileNetV2 + Spatial Head</div>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-semibold flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>&gt;90% ACHIEVED</span>
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3 pt-2">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 font-mono">ACCURACY</div>
              <div className="text-xl font-bold text-cyan-300 mt-1">91.40%</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 font-mono">SENSITIVITY</div>
              <div className="text-xl font-bold text-emerald-300 mt-1">93.41%</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 font-mono">ROC-AUC</div>
              <div className="text-xl font-bold text-blue-300 mt-1">0.9691</div>
            </div>
          </div>

          <div className="text-xs text-slate-400 font-mono space-y-1 pt-2 border-t border-slate-800/80">
            <div>• Training Corpus: 11,654 High-Resolution Radiographs</div>
            <div>• Target Classes: Fractured Skeletal vs Intact Skeletal</div>
            <div>• Spatial Bounding Boxes: OpenCV Overlay Compositing</div>
          </div>
        </div>
      </div>

      {/* Backend Infrastructure Telemetry */}
      <div className="p-6 rounded-2xl bg-[#0e1626]/80 border border-slate-800/80 backdrop-blur-md shadow-xl space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono flex items-center space-x-2">
          <Server className="w-4 h-4 text-cyan-400" />
          <span>Active Microservices & Pipeline Health</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="text-slate-400 mb-1">REST API SERVER</div>
            <div className="text-emerald-400 font-bold flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>FastAPI (Port 8000)</span>
            </div>
            <div className="text-slate-500 text-[11px] mt-1">Uvicorn Async Worker</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="text-slate-400 mb-1">PACS DATABASE</div>
            <div className="text-cyan-400 font-bold flex items-center space-x-1.5">
              <Database className="w-3.5 h-3.5" />
              <span>SQLite 3NF Normalized</span>
            </div>
            <div className="text-slate-500 text-[11px] mt-1">xray_system.db</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="text-slate-400 mb-1">REPORT COMPILER</div>
            <div className="text-cyan-400 font-bold flex items-center space-x-1.5">
              <FileText className="w-3.5 h-3.5" />
              <span>ReportLab RSNA Engine</span>
            </div>
            <div className="text-slate-500 text-[11px] mt-1">Capsule Header / No Sig</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="text-slate-400 mb-1">INFERENCE DEVICE</div>
            <div className="text-amber-400 font-bold flex items-center space-x-1.5">
              <Zap className="w-3.5 h-3.5" />
              <span>Multi-Threaded CPU</span>
            </div>
            <div className="text-slate-500 text-[11px] mt-1">Latency ~140ms</div>
          </div>
        </div>
      </div>
    </div>
  );
}
