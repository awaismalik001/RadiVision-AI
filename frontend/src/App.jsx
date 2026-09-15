import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import SplashScreen from './components/SplashScreen';
import Sidebar from './components/Sidebar';
import DiagnosticStudio from './components/DiagnosticStudio';
import PatientHistory from './components/PatientHistory';
import HealthcareNetwork from './components/HealthcareNetwork';
import NeuralTelemetry from './components/NeuralTelemetry';

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [activeTab, setActiveTab] = useState('studio');
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="relative min-h-screen w-full bg-[#070b14] text-slate-100 font-sans overflow-hidden flex">
      <AnimatePresence mode="wait">
        {showSplash ? (
          <SplashScreen key="splash" onComplete={() => setShowSplash(false)} />
        ) : (
          <motion.div
            key="workspace"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="flex w-full h-screen overflow-hidden"
          >
            {/* Collapsible Left Sidebar */}
            <Sidebar
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              isCollapsed={isCollapsed}
              setIsCollapsed={setIsCollapsed}
            />

            {/* Main Stage Viewport */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
              {activeTab === 'studio' && <DiagnosticStudio />}
              {activeTab === 'history' && (
                <PatientHistory onNavigateStudio={() => setActiveTab('studio')} />
              )}
              {activeTab === 'referrals' && <HealthcareNetwork />}
              {activeTab === 'telemetry' && <NeuralTelemetry />}
            </main>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
