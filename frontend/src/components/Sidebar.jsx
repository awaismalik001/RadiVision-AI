import React from 'react';
import { motion } from 'framer-motion';
import { 
  Stethoscope, 
  FolderArchive, 
  Clock, 
  BarChart3, 
  User, 
  ShieldCheck, 
  LogOut, 
  ChevronLeft, 
  ChevronRight,
  Lock,
  LayoutDashboard
} from 'lucide-react';

export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  isCollapsed, 
  setIsCollapsed, 
  currentUser, 
  onLogout 
}) {
  const isAdmin = currentUser?.role === 'Admin';

  const menuItems = [
    { id: 'dashboard', label: isAdmin ? 'Admin Dashboard' : 'User Dashboard', icon: LayoutDashboard },
    { id: 'studio', label: 'AI Diagnostic Studio', icon: Stethoscope, badge: 'ViT Live' },
    ...(!isAdmin ? [{ id: 'my-history', label: 'My Scan History', icon: Clock, badge: 'Personal' }] : []),
    ...(isAdmin ? [{ id: 'history', label: 'PACS Patient Records', icon: FolderArchive }] : []),
    ...(isAdmin ? [{ id: 'admin', label: 'Admin Command Center', icon: BarChart3, badge: 'Admin' }] : []),
    { id: 'profile', label: isAdmin ? 'Profile Management' : 'Profile Settings', icon: User, badge: isAdmin ? 'Admin' : 'Read-Only' }
  ];

  return (
    <motion.aside
      animate={{ width: isCollapsed ? 72 : 260 }}
      transition={{ duration: 0.25, ease: "easeInOut" }}
      className="relative flex flex-col justify-between h-screen bg-[#1982bf] border-r border-[#156ea3] text-white z-30 select-none shadow-xl shrink-0"
    >
      {/* Top Header / Branding */}
      <div>
        <div className="flex items-center justify-between px-4 border-b border-[#156ea3] h-16">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 min-w-9 rounded-xl bg-white/20 flex items-center justify-center shadow-inner ring-1 ring-white/30">
              <Stethoscope className="w-5 h-5 text-white" />
            </div>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                className="whitespace-nowrap"
              >
                <div className="flex items-center space-x-1.5">
                  <span className="font-extrabold tracking-wider text-sm text-white">RADIVISION</span>
                  <span className="font-bold text-sm text-cyan-200">AI</span>
                </div>
                <div className="text-[11px] font-mono text-white/80 tracking-wider">
                  CLINICAL WORKSTATION
                </div>
              </motion.div>
            )}
          </div>

          {/* Collapse Toggle Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-2.5 space-y-1 mt-1.5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center px-0' : 'justify-between px-3.5'
                } py-2.5 rounded-xl text-sm font-medium transition-all group cursor-pointer ${
                  isActive
                    ? 'bg-white text-[#1982bf] shadow-md font-semibold'
                    : 'text-white/90 hover:text-white hover:bg-white/10'
                }`}
                title={isCollapsed ? item.label : undefined}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4.5 h-4.5 transition-colors ${isActive ? 'text-[#1982bf]' : 'text-white/85 group-hover:text-white'}`} />
                  {!isCollapsed && (
                    <span className="tracking-wide text-sm">{item.label}</span>
                  )}
                </div>
                {!isCollapsed && item.badge && (
                  <span className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded-full ${
                    isActive
                      ? 'bg-[#1982bf]/10 text-[#1982bf]'
                      : 'bg-white/20 text-white'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* System Telemetry Specs (when expanded) */}
        {!isCollapsed && (
          <div className="mx-3 mt-3.5 p-3 rounded-xl bg-white/10 border border-white/15 text-white">
            <div className="flex items-center justify-between text-white/85 mb-2 font-mono text-xs">
              <span className="flex items-center space-x-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-300 animate-ping" />
                <span>ACTIVE ENGINE</span>
              </span>
              <span className="text-cyan-200 font-semibold">ViT-B/16</span>
            </div>
            <div className="space-y-1.5 text-xs text-white/90">
              <div className="flex justify-between">
                <span className="text-white/75">PACS Vault:</span>
                <span className="font-mono text-emerald-200 flex items-center space-x-1">
                  <Lock className="w-3 h-3 inline" />
                  <span>AES-256</span>
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/75">AI Validation:</span>
                <span className="font-mono text-cyan-200">Gemini 3.8 Flash</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom User Profile Card & Logout */}
      <div className="p-2.5 border-t border-[#156ea3]">
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} p-2 rounded-xl bg-white/15 border border-white/20`}>
          <div className="flex items-center space-x-2.5 overflow-hidden">
            <div className="relative shrink-0">
              <div className="w-8 h-8 rounded-lg bg-white/20 border border-white/30 flex items-center justify-center text-white font-bold">
                <User className="w-4 h-4 text-white" />
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 ring-1 ring-[#1982bf]" />
            </div>
            {!isCollapsed && (
              <div className="overflow-hidden">
                <div className="text-xs font-bold text-white truncate">
                  {currentUser?.full_name || 'User'}
                </div>
                <div className="text-[11px] text-cyan-200 truncate flex items-center space-x-1 font-medium">
                  <ShieldCheck className="w-3 h-3 text-cyan-200 inline" />
                  <span>{currentUser?.role === 'Admin' ? 'Admin' : 'User'}</span>
                </div>
              </div>
            )}
          </div>

          {!isCollapsed && (
            <button
              onClick={onLogout}
              className="p-1.5 rounded-lg text-white/75 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </motion.aside>
  );
}
