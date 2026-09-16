import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lock, 
  User, 
  Mail, 
  ShieldCheck, 
  AlertCircle, 
  CheckCircle2, 
  Stethoscope, 
  Eye, 
  EyeOff, 
  ArrowRight 
} from 'lucide-react';
import axios from 'axios';

export default function AuthModal({ isOpen, onClose, onLoginSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('User');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  // Password validation rules for sign up
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  const isPasswordValid = hasMinLength && hasUppercase && hasLowercase && hasNumber && hasSpecial;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    try {
      if (isSignUp) {
        if (!isPasswordValid) {
          setErrorMessage('Password must satisfy all security complexity requirements.');
          setIsLoading(false);
          return;
        }

        const res = await axios.post('/api/auth/signup', {
          full_name: fullName,
          username: username,
          email: email,
          password: password,
          role: role
        });

        if (res.data && res.data.success) {
          onLoginSuccess(res.data.user);
          onClose();
        }
      } else {
        const res = await axios.post('/api/auth/login', {
          username: username,
          password: password
        });

        if (res.data && res.data.success) {
          onLoginSuccess(res.data.user);
          onClose();
        }
      }
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Authentication error.';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B1727]/80 backdrop-blur-md">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden"
      >
        {/* Top Branding Banner */}
        <div className="bg-[#1982bf] p-6 text-white text-center relative">
          <div className="inline-flex w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-600 to-blue-600 items-center justify-center shadow-lg shadow-cyan-500/30 ring-1 ring-cyan-400/40 mb-3">
            <Stethoscope className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl font-bold tracking-wider">
            RADIVISION <span className="text-cyan-400">AI</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {isSignUp ? "Create your account" : "Sign in to your workstation"}
          </p>
        </div>

        {/* Form Body */}
        <div className="p-6 md:p-8">
          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignUp && (
              <>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    Full Name & Title
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Dr. Alexander Wright, MD"
                      required
                      className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    Institutional Email
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="radiology@hospital.org"
                      required
                      className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin or username"
                  required
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full pl-9 pr-10 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Password Validation Checklist (Sign Up) */}
            {isSignUp && (
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1 text-slate-600">
                <div className="font-semibold text-slate-700 mb-1">Security Standards:</div>
                <div className="flex items-center space-x-1.5">
                  <span className={hasMinLength ? "text-emerald-600" : "text-slate-400"}>• At least 8 characters</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className={hasUppercase ? "text-emerald-600" : "text-slate-400"}>• Uppercase letter (A-Z)</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className={hasLowercase ? "text-emerald-600" : "text-slate-400"}>• Lowercase letter (a-z)</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className={hasNumber ? "text-emerald-600" : "text-slate-400"}>• Numeric digit (0-9)</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className={hasSpecial ? "text-emerald-600" : "text-slate-400"}>• Special character (!@#$%^&*)</span>
                </div>
              </div>
            )}

            {/* Remember Me on Login */}
            {!isSignUp && (
              <div className="flex items-center justify-between text-xs text-slate-600 pt-1">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    defaultChecked 
                    className="w-4 h-4 rounded border-slate-300 text-[#1982bf] focus:ring-[#1982bf] cursor-pointer" 
                  />
                  <span>Remember workstation session</span>
                </label>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-3 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-sm flex items-center justify-center space-x-2 shadow-lg transition-all cursor-pointer"
            >
              <span>{isLoading ? "Authenticating..." : isSignUp ? "Create Account" : "Sign In"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Toggle between Login and Signup */}
          <div className="mt-6 text-center text-xs text-slate-500">
            {isSignUp ? (
              <span>
                Already have an account?{' '}
                <button
                  onClick={() => { setIsSignUp(false); setErrorMessage(''); }}
                  className="font-semibold text-[#1982bf] hover:underline cursor-pointer"
                >
                  Sign In
                </button>
              </span>
            ) : (
              <span>
                Don't have an account?{' '}
                <button
                  onClick={() => { setIsSignUp(true); setErrorMessage(''); }}
                  className="font-semibold text-[#1982bf] hover:underline cursor-pointer"
                >
                  Register Account
                </button>
              </span>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
