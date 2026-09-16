import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Stethoscope } from 'lucide-react';
import SplashScreen from './components/SplashScreen';
import Sidebar from './components/Sidebar';
import UserDashboard from './components/UserDashboard';
import DiagnosticStudio from './components/DiagnosticStudio';
import PatientHistory from './components/PatientHistory';
import AdminDashboard from './components/AdminDashboard';
import ProfileManagement from './components/ProfileManagement';
import AuthModal from './components/AuthModal';
import axios from 'axios';

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // currentUser initializes to null: On app launch, the application ALWAYS opens to the Login screen, NOT the user panel
  const [currentUser, setCurrentUser] = useState(null);

  // Native Desktop Window: Auto-logout trigger on application window close
  useEffect(() => {
    const handleCloseLogout = () => {
      axios.post('/api/auth/logout').catch(() => {});
      localStorage.removeItem('radivision_user');
    };

    if (window.electronAPI && window.electronAPI.onAutoLogout) {
      window.electronAPI.onAutoLogout(handleCloseLogout);
    }

    window.addEventListener('beforeunload', handleCloseLogout);
    return () => window.removeEventListener('beforeunload', handleCloseLogout);
  }, []);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    localStorage.setItem('radivision_user', JSON.stringify(user));
    setShowAuthModal(false);
    if (user.role === 'Admin') {
      setActiveTab('admin');
    } else {
      setActiveTab('dashboard');
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout');
    } catch (e) {
      console.error('Logout error:', e);
    }
    localStorage.removeItem('radivision_user');
    setCurrentUser(null);
    setActiveTab('dashboard');
    setShowAuthModal(false);
  };

  return (
    <div className="relative min-h-screen w-full bg-slate-50 text-slate-900 font-sans overflow-hidden flex">
      <AnimatePresence mode="wait">
        {showSplash ? (
          <SplashScreen key="splash" onComplete={() => setShowSplash(false)} />
        ) : !currentUser ? (
          /* Desktop Login Screen: Opened upon app launch */
          <motion.div
            key="login-screen"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="w-full h-screen overflow-hidden flex items-center justify-center bg-gradient-to-br from-slate-950 via-[#0B1727] to-[#0A2540] relative p-4 select-none"
          >
            {/* Background Medical Pattern & Radial Glow */}
            <div className="absolute inset-0 opacity-15 bg-[radial-gradient(#1982bf_1px,transparent_1px)] [background-size:20px_20px] pointer-events-none" />
            <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#1982bf]/20 rounded-full blur-3xl pointer-events-none" />

            {/* Top Desktop App Branding */}
            <div className="absolute top-6 left-8 flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-[#1982bf] flex items-center justify-center text-white font-bold shadow-lg ring-1 ring-cyan-400/40">
                <Stethoscope className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="text-base font-bold text-white tracking-wider">
                  RADIVISION <span className="text-cyan-400">AI</span>
                </div>
                <div className="text-[10px] text-slate-400 font-mono tracking-wider">
                  NATIVE DESKTOP CLINICAL WORKSTATION
                </div>
              </div>
            </div>

            {/* System Engine Status Badge */}
            <div className="absolute top-6 right-8 flex items-center space-x-2">
              <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>PACS ENGINE ONLINE</span>
              </span>
            </div>

            {/* Centered Desktop Login Card */}
            <AuthModal
              isOpen={true}
              isStandalone={true}
              onLoginSuccess={handleLoginSuccess}
            />

            {/* Bottom Security Note */}
            <div className="absolute bottom-5 text-center text-[11px] text-slate-500 font-mono">
              RadiVision AI v2.0 • ViT-B/16 Deep Learning • AES-256 Vault Encryption
            </div>
          </motion.div>
        ) : (
          /* Authenticated Workstation: Shown ONLY after successful login */
          <motion.div
            key="workspace"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="flex w-full h-screen overflow-hidden"
          >
            {/* Left Desktop Sidebar (#1982BF) */}
            <Sidebar
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              isCollapsed={isCollapsed}
              setIsCollapsed={setIsCollapsed}
              currentUser={currentUser}
              onLogout={handleLogout}
            />

            {/* Main Stage Viewport (Clean Hospital White Aesthetic) */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden relative bg-slate-50">
              {activeTab === 'dashboard' && (
                <UserDashboard 
                  currentUser={currentUser} 
                  onNavigate={setActiveTab} 
                />
              )}
              {activeTab === 'studio' && (
                <DiagnosticStudio currentUser={currentUser} />
              )}
              {activeTab === 'my-history' && (
                <PatientHistory 
                  currentUser={currentUser} 
                  isMyHistory={true} 
                  onNavigateStudio={() => setActiveTab('studio')} 
                />
              )}
              {activeTab === 'history' && (
                <PatientHistory 
                  currentUser={currentUser} 
                  isMyHistory={false} 
                  onNavigateStudio={() => setActiveTab('studio')} 
                />
              )}
              {activeTab === 'admin' && (
                <AdminDashboard currentUser={currentUser} />
              )}
              {activeTab === 'profile' && (
                <ProfileManagement currentUser={currentUser} />
              )}
            </main>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Manual AuthModal popup if triggered inside workstation */}
      {currentUser && showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      )}
    </div>
  );
}
