import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Sparkles } from 'lucide-react';
import splashImg from '../assets/splash_radivision.jpg';

export default function SplashScreen({ onComplete }) {
  const [animationDone, setAnimationDone] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(5);

  const handleFinish = () => {
    if (window.electronAPI?.toAuthWindow) {
      window.electronAPI.toAuthWindow();
    }
    onComplete();
  };

  // 1. Initial fade-in and clarity animation duration is ~1.4 seconds.
  useEffect(() => {
    const animTimer = setTimeout(() => {
      setAnimationDone(true);
    }, 1400);

    return () => clearTimeout(animTimer);
  }, []);

  // 2. 5-second countdown once animation is done
  useEffect(() => {
    if (!animationDone) return;

    const interval = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // 5-second timeout following the animation
    const transitionTimer = setTimeout(() => {
      handleFinish();
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(transitionTimer);
    };
  }, [animationDone]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
      style={{ WebkitAppRegion: 'drag' }}
      className="w-full h-full min-h-screen flex flex-col justify-between bg-slate-950 text-slate-100 select-none overflow-hidden cursor-default rounded-2xl border border-slate-800/80 shadow-2xl"
    >
      {/* Pure RadiVision AI Workflow Image with Clarity Animation */}
      <div className="relative flex-1 flex items-center justify-center overflow-hidden bg-slate-950">
        <motion.img
          src={splashImg}
          alt="RadiVision AI Multi-Modal Diagnostic Workflow"
          initial={{
            opacity: 0,
            filter: "blur(16px) brightness(0.7) contrast(1.1)",
            scale: 0.96
          }}
          animate={{
            opacity: 1,
            filter: "blur(0px) brightness(1) contrast(1)",
            scale: 1
          }}
          transition={{
            duration: 1.4,
            ease: [0.16, 1, 0.3, 1]
          }}
          className="w-full h-full object-cover select-none pointer-events-none"
        />

        {/* Subtle Light Sweep Effect */}
        <motion.div
          initial={{ x: "-100%", opacity: 0 }}
          animate={{ x: "200%", opacity: [0, 0.4, 0] }}
          transition={{ delay: 1.2, duration: 1.4, ease: "easeInOut" }}
          className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/25 to-transparent -skew-x-12 pointer-events-none"
        />

        {/* Top-right quick skip */}
        <button
          onClick={handleFinish}
          style={{ WebkitAppRegion: 'no-drag' }}
          className="absolute top-3 right-3 text-[10px] font-mono text-slate-400 hover:text-cyan-300 bg-slate-900/80 hover:bg-slate-900 border border-slate-700/60 px-2 py-1 rounded-md transition-all cursor-pointer backdrop-blur-sm"
        >
          Skip &rarr;
        </button>
      </div>

      {/* Sleek Glowing Progress Bar Anchored Directly to Image */}
      <div className="w-full h-1.5 bg-slate-900 overflow-hidden relative shrink-0">
        {animationDone ? (
          <motion.div
            initial={{ width: "0%" }}
            animate={{ width: "100%" }}
            transition={{ duration: 5, ease: "linear" }}
            className="h-full bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-500 shadow-[0_0_12px_rgba(6,182,212,0.9)]"
          />
        ) : (
          <motion.div
            initial={{ width: "0%" }}
            animate={{ width: "35%" }}
            transition={{ duration: 1.4, ease: "easeOut" }}
            className="h-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.7)]"
          />
        )}
      </div>

      {/* Bottom Compact Telemetry Strip */}
      <div className="px-3.5 py-2 bg-slate-950 border-t border-slate-900 flex items-center justify-between text-[11px] font-mono shrink-0">
        <div className="flex items-center space-x-1.5 truncate">
          {animationDone ? (
            <span className="text-emerald-400 flex items-center space-x-1 truncate">
              <CheckCircle2 className="w-3.5 h-3.5 shrink-0 text-emerald-400" />
              <span>Neural Pipeline Initialized • Loading Workstation...</span>
            </span>
          ) : (
            <span className="text-cyan-300 flex items-center space-x-1 truncate">
              <Sparkles className="w-3.5 h-3.5 shrink-0 text-cyan-400 animate-spin" style={{ animationDuration: '3s' }} />
              <span>Calibrating Vision Transformer & Gemini Multimodal AI...</span>
            </span>
          )}
        </div>
        <span className="text-cyan-400 font-bold ml-2 shrink-0">{secondsLeft}s</span>
      </div>
    </motion.div>
  );
}
