import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldCheck, Cpu, ArrowRight, Sparkles, Stethoscope } from 'lucide-react';

export default function SplashScreen({ onComplete }) {
  const [progress, setProgress] = useState(12);
  const [bootStep, setBootStep] = useState(0);

  const bootLogs = [
    { text: "Mounting PyTorch Neural Backbone & Weights...", percent: 28 },
    { text: "Loading Chest Pneumonia Classifier (Calibrated 90.72% Accuracy)...", percent: 54 },
    { text: "Loading Bone Fracture Localization Model (91.40% Accuracy, 0.969 AUC)...", percent: 82 },
    { text: "Initializing Local Healthcare & GPS Referral Engine...", percent: 94 },
    { text: "All Systems Operational. Ready for Diagnostic Ingestion.", percent: 100 }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setBootStep((prev) => {
        if (prev < bootLogs.length - 1) {
          const next = prev + 1;
          setProgress(bootLogs[next].percent);
          return next;
        } else {
          clearInterval(timer);
          return prev;
        }
      });
    }, 700);

    return () => clearInterval(timer);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 1.05 }}
      transition={{ duration: 0.6 }}
      className="relative min-h-screen w-full flex flex-col justify-between overflow-hidden bg-[#070b14] text-slate-100 font-sans select-none"
    >
      {/* Background Graphic with Vignette & Cyber Grid */}
      <div className="absolute inset-0 z-0">
        <img
          src="/splash_workstation.jpg"
          alt="RadiVision AI Workstation"
          className="w-full h-full object-cover object-center filter brightness-50 contrast-125 scale-105 transform animate-pulse-slow"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#070b14] via-[#070b14]/75 to-[#070b14]/90" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-500/10 via-transparent to-transparent" />
        
        {/* Subtle holographic scanline grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#06b6d40a_1px,transparent_1px),linear-gradient(to_bottom,#06b6d40a_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      </div>

      {/* Top Bar / Telemetry Header */}
      <div className="relative z-10 flex items-center justify-between px-8 py-6">
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex items-center space-x-3"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/30 ring-1 ring-cyan-400/40">
            <Stethoscope className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-wider text-white">RADIVISION</span>
            <span className="text-xl font-light tracking-widest text-cyan-400 ml-1.5">AI</span>
            <div className="text-[10px] tracking-widest text-slate-400 uppercase font-mono">
              Clinical Neural Suite v2.0
            </div>
          </div>
        </motion.div>

        <button
          onClick={onComplete}
          className="text-xs font-mono text-slate-400 hover:text-cyan-300 transition-colors px-4 py-2 rounded-lg border border-slate-700/60 hover:border-cyan-500/50 bg-slate-900/60 backdrop-blur-md flex items-center space-x-1.5"
        >
          <span>SKIP BOOT SEQUENCE</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Center Stage: Mission Statement & Hero Branding */}
      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center my-auto">
        <motion.div
          initial={{ scale: 0.85, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.7, type: "spring", stiffness: 100 }}
          className="inline-flex items-center space-x-2.5 px-4 py-1.5 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-medium tracking-wide mb-6 backdrop-blur-md shadow-inner"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin" style={{ animationDuration: '6s' }} />
          <span>Deep Learning Radiographic Screening & Diagnostic Report Suite</span>
        </motion.div>

        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="text-4xl md:text-6xl font-extrabold text-white tracking-tight"
        >
          Instant Radiograph Ingestion & <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-500">
            Automated Clinical Referrals
          </span>
        </motion.h1>

        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-4 text-base md:text-lg text-slate-300 max-w-2xl mx-auto font-light leading-relaxed"
        >
          Autonomous multi-modal detection of pneumonia and bone fractures with calibrated confidence ratings,
          spatial Grad-CAM localized heatmaps, and GPS-anchored hospital specialist referrals.
        </motion.p>

        {/* Live System Metrics Cards */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-10 max-w-3xl mx-auto text-left"
        >
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800/80 backdrop-blur-md hover:border-cyan-500/40 transition-all">
            <div className="flex items-center justify-between text-cyan-400 mb-1">
              <span className="text-xs font-mono tracking-wide">CHEST CLASSIFIER</span>
              <Activity className="w-4 h-4" />
            </div>
            <div className="text-2xl font-bold text-white">90.72%</div>
            <div className="text-xs text-slate-400 mt-0.5">Calibrated Accuracy • 0.9534 AUC</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800/80 backdrop-blur-md hover:border-cyan-500/40 transition-all">
            <div className="flex items-center justify-between text-cyan-400 mb-1">
              <span className="text-xs font-mono tracking-wide">BONE FRACTURE AI</span>
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div className="text-2xl font-bold text-white">91.40%</div>
            <div className="text-xs text-slate-400 mt-0.5">11,654 Radiographs • 0.9691 AUC</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800/80 backdrop-blur-md hover:border-cyan-500/40 transition-all">
            <div className="flex items-center justify-between text-cyan-400 mb-1">
              <span className="text-xs font-mono tracking-wide">LOCAL REFERRAL ENGINE</span>
              <Cpu className="w-4 h-4" />
            </div>
            <div className="text-2xl font-bold text-white">GPS MATCHED</div>
            <div className="text-xs text-slate-400 mt-0.5">Islamabad, New York & Worldwide</div>
          </div>
        </motion.div>
      </div>

      {/* Bottom Loading Bar & Enter Action */}
      <div className="relative z-10 max-w-3xl w-full mx-auto px-6 pb-12">
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span className="flex items-center space-x-2">
              <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span>{bootLogs[bootStep].text}</span>
            </span>
            <span className="font-semibold text-cyan-300">{progress}%</span>
          </div>

          {/* Progress Bar Container */}
          <div className="w-full h-2 rounded-full bg-slate-800/90 overflow-hidden border border-slate-700/50 p-0.5">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 via-teal-400 to-blue-500 shadow-lg shadow-cyan-500/50"
              initial={{ width: "10%" }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>

          {/* Enter Button (Unlocked once loaded or available immediately) */}
          <div className="pt-4 flex justify-center">
            <motion.button
              whileHover={{ scale: 1.03, boxShadow: "0 0 25px rgba(6, 182, 212, 0.4)" }}
              whileTap={{ scale: 0.98 }}
              onClick={onComplete}
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 via-cyan-500 to-blue-600 text-white font-semibold text-sm tracking-wide shadow-xl shadow-cyan-600/30 flex items-center space-x-3 border border-cyan-400/40 cursor-pointer"
            >
              <span>ENTER DIAGNOSTIC STUDIO</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
