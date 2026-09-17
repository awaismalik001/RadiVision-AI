import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Stethoscope, Minus, Square, X } from 'lucide-react';
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
    if (window.electronAPI?.maximizeWorkstation) {
      window.electronAPI.maximizeWorkstation();
    }
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
    if (window.electronAPI?.shrinkToAuthWindow) {
      window.electronAPI.shrinkToAuthWindow();
    }
  };

  return (
    <div className={`relative min-h-screen w-full font-sans overflow-hidden flex ${currentUser ? 'bg-slate-50 text-slate-900' : 'bg-transparent'}`}>
      <AnimatePresence mode="wait">
        {showSplash ? (
          <SplashScreen key="splash" onComplete={() => setShowSplash(false)} />
        ) : !currentUser ? (
          /* Desktop Login Screen: Only the clean centered Auth card */
          <motion.div
            key="login-screen"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="w-full min-h-screen flex items-center justify-center bg-transparent select-none overflow-hidden p-2"
          >
            {/* Centered Desktop Auth Card (Sign In & Sign Up Views) */}
            <AuthModal
              isOpen={true}
              isStandalone={true}
              onLoginSuccess={handleLoginSuccess}
            />
          </motion.div>
        ) : (
          /* Authenticated Workstation: Shown ONLY after successful login */
          <motion.div
            key="workspace"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="flex w-full h-screen overflow-hidden bg-slate-50"
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
              {/* Sleek Frameless Window Controls for Desktop Workstation */}
              {window.electronAPI?.isElectron && (
                <div 
                  className="absolute top-0 right-0 z-50 flex items-center h-8 bg-slate-200/50 hover:bg-slate-200/90 backdrop-blur-xs border-b border-l border-slate-300/60 rounded-bl-md overflow-hidden select-none transition-colors"
                  style={{ WebkitAppRegion: 'no-drag' }}
                >
                  <button
                    onClick={() => window.electronAPI.minimize?.()}
                    className="h-8 px-3 text-slate-600 hover:text-slate-950 hover:bg-slate-300/80 transition-colors flex items-center justify-center cursor-pointer"
                    title="Minimize"
                  >
                    <Minus className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => window.electronAPI.maximizeToggle?.()}
                    className="h-8 px-3 text-slate-600 hover:text-slate-950 hover:bg-slate-300/80 transition-colors flex items-center justify-center cursor-pointer"
                    title="Maximize / Restore"
                  >
                    <Square className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => window.electronAPI.close?.()}
                    className="h-8 px-3.5 text-slate-600 hover:text-white hover:bg-rose-600 transition-colors flex items-center justify-center cursor-pointer"
                    title="Close Application"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
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
