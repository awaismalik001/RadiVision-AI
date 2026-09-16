import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import SplashScreen from './components/SplashScreen';
import Sidebar from './components/Sidebar';
import UserDashboard from './components/UserDashboard';
import DiagnosticStudio from './components/DiagnosticStudio';
import PatientHistory from './components/PatientHistory';
import AdminDashboard from './components/AdminDashboard';
import ProfileManagement from './components/ProfileManagement';
import AuthModal from './components/AuthModal';
import axios from 'axios';

const DEFAULT_ADMIN = {
  user_id: 1,
  full_name: "Lead System Administrator",
  username: "admin",
  email: "admin@radivision.ai",
  role: "Admin",
  is_active: 1
};

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Load active session from local storage or default to initialized Admin
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('radivision_user');
      return saved ? JSON.parse(saved) : DEFAULT_ADMIN;
    } catch {
      return DEFAULT_ADMIN;
    }
  });

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
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout');
    } catch (e) {
      console.error('Logout error:', e);
    }
    localStorage.removeItem('radivision_user');
    setCurrentUser(null);
    setShowAuthModal(true);
  };

  return (
    <div className="relative min-h-screen w-full bg-slate-50 text-slate-900 font-sans overflow-hidden flex">
      <AnimatePresence mode="wait">
        {showSplash ? (
          <SplashScreen key="splash" onComplete={() => setShowSplash(false)} />
        ) : (
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

      {/* Desktop Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal || (!currentUser && !showSplash)}
        onClose={() => setShowAuthModal(false)}
        onLoginSuccess={handleLoginSuccess}
      />
    </div>
  );
}
