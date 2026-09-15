import React from 'react';
import { motion } from 'framer-motion';
import { 
  Stethoscope, 
  Activity, 
  FolderClock, 
  Building2, 
  Cpu, 
  ChevronLeft, 
  ChevronRight, 
  ShieldCheck,
  User,
  ExternalLink
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, isCollapsed, setIsCollapsed, telemetry }) {
  const menuItems = [
    { id: 'studio', label: 'AI Diagnostic Studio', icon: Stethoscope, badge: 'Live' },
    { id: 'history', label: 'PACS Patient Records', icon: FolderClock },
    { id: 'referrals', label: 'Healthcare Network', icon: Building2, badge: 'GPS' },
    { id: 'telemetry', label: 'Neural Telemetry', icon: Cpu },
  ];

  return (
    <motion.aside
      animate={{ width: isCollapsed ? 80 : 260 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="relative flex flex-col justify-between h-screen bg-[#0d1322]/95 border-r border-slate-800/80 backdrop-blur-xl text-slate-200 z-30 select-none shadow-2xl shrink-0"
    >
      {/* Top Header / Branding */}
      <div>
        <div className="flex items-center justify-between p-4 border-b border-slate-800/60 h-20">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-10 h-10 min-w-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-md shadow-cyan-500/20 ring-1 ring-cyan-400/30">
              <Stethoscope className="w-5 h-5 text-white" />
            </div>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="whitespace-nowrap"
              >
                <div className="flex items-center space-x-1">
                  <span className="font-extrabold tracking-wider text-white">RADIVISION</span>
                  <span className="font-bold text-cyan-400">AI</span>
                </div>
                <div className="text-[10px] font-mono text-slate-400 tracking-wider">
                  CLINICAL SUITE
                </div>
              </motion.div>
            )}
          </div>

          {/* Collapse Toggle Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800/60 transition-colors cursor-pointer"
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center px-0' : 'justify-between px-3.5'
                } py-3 rounded-xl text-sm font-medium transition-all group cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-300 border border-cyan-500/30 shadow-lg shadow-cyan-500/5'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 border border-transparent'
                }`}
                title={isCollapsed ? item.label : undefined}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-5 h-5 transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-cyan-300'}`} />
                  {!isCollapsed && (
                    <span className="tracking-wide">{item.label}</span>
                  )}
                </div>
                {!isCollapsed && item.badge && (
                  <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full ${
                    item.badge === 'Live'
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Model Benchmark Overview (when expanded) */}
        {!isCollapsed && (
          <div className="mx-3 mt-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs">
            <div className="flex items-center justify-between text-slate-400 mb-2 font-mono text-[11px]">
              <span className="flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                <span>MODELS ONLINE</span>
              </span>
              <span className="text-cyan-400 font-semibold">PyTorch</span>
            </div>
            <div className="space-y-1.5 text-[11px] text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Chest Pneumonia:</span>
                <span className="font-mono text-cyan-300 font-semibold">90.72% Acc</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Bone Fracture:</span>
                <span className="font-mono text-emerald-300 font-semibold">91.40% Acc</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Clinician Profile Card */}
      <div className="p-3 border-t border-slate-800/60">
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'space-x-3'} p-2 rounded-xl bg-slate-900/50 border border-slate-800/60`}>
          <div className="relative">
            <div className="w-9 h-9 rounded-lg bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-300 font-bold">
              <User className="w-5 h-5 text-cyan-400" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 ring-2 ring-[#0d1322]" />
          </div>
          {!isCollapsed && (
            <div className="overflow-hidden">
              <div className="text-xs font-semibold text-slate-200 truncate">Dr. Radiologist</div>
              <div className="text-[10px] text-slate-400 truncate flex items-center space-x-1">
                <ShieldCheck className="w-3 h-3 text-cyan-400 inline" />
                <span>Chief AI Attending</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.aside>
  );
}
